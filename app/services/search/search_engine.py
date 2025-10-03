"""
Core search engine implementation.
Handles document indexing, searching, and ranking.
"""
import logging
from typing import List, Dict, Optional, Any
from collections import defaultdict
import json
from app.database import execute_query
from app.services.search.tokenizer import analyze_text

logger = logging.getLogger(__name__)


class SearchDocument:
    """Represents a searchable document"""

    def __init__(self, doc_type: str, entity_id: str, title: str, content: str, metadata: Dict = None):
        self.doc_type = doc_type
        self.entity_id = entity_id
        self.title = title
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            'doc_type': self.doc_type,
            'entity_id': self.entity_id,
            'title': self.title,
            'content': self.content,
            'metadata': self.metadata
        }


class SearchEngine:
    """Main search engine class"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def add_document(self, document: SearchDocument) -> Optional[int]:
        """
        Add a document to the search index.
        Returns the document ID if successful, None otherwise.
        """
        try:
            # Insert or update the document
            doc_query = """
                INSERT INTO search_documents (doc_type, entity_id, title, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (doc_type, entity_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """

            result = execute_query(
                doc_query,
                (document.doc_type, document.entity_id, document.title,
                 document.content, json.dumps(document.metadata))
            )

            if not result or len(result) == 0:
                return None

            doc_id = result[0]['id']

            # Analyze the content to get tokens
            tokens = analyze_text(document.content)

            # Count token frequencies
            token_freq = defaultdict(int)
            for token in tokens:
                token_freq[token] += 1

            # Delete old index entries for this document
            execute_query(
                "DELETE FROM search_index WHERE doc_id = %s",
                (doc_id,)
            )

            # Insert new index entries
            if token_freq:
                index_values = [(term, doc_id, freq) for term, freq in token_freq.items()]

                # Use batch insert for performance
                insert_query = """
                    INSERT INTO search_index (term, doc_id, frequency)
                    VALUES %s
                    ON CONFLICT (term, doc_id) DO NOTHING
                """

                # Since we can't use execute_values with our execute_query function,
                # insert one by one (or we could modify execute_query to support it)
                for term, doc_id, freq in index_values:
                    execute_query(
                        "INSERT INTO search_index (term, doc_id, frequency) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (term, doc_id, freq)
                    )

            self.logger.info(f"Indexed document {doc_id}: {document.title} ({len(token_freq)} unique terms)")
            return doc_id

        except Exception as e:
            self.logger.error(f"Error indexing document: {e}", exc_info=True)
            return None

    def add_documents_batch(self, documents: List[SearchDocument]) -> int:
        """
        Add multiple documents to the index.
        Returns the number of successfully indexed documents.
        """
        success_count = 0
        for doc in documents:
            if self.add_document(doc):
                success_count += 1
        return success_count

    def search(self, query: str, doc_type: Optional[str] = None,
               filters: Dict[str, Any] = None, limit: int = 50) -> List[Dict]:
        """
        Search for documents matching the query.

        Args:
            query: Search query string
            doc_type: Optional document type filter ('player', 'team', 'game')
            filters: Optional metadata filters (e.g., {'position': 'QB', 'team': 'KC'})
            limit: Maximum number of results to return

        Returns:
            List of matching documents with relevance scores
        """
        try:
            if not query or not query.strip():
                return []

            # Analyze the query to get search terms
            search_terms = analyze_text(query)

            if not search_terms:
                return []

            # Build the search query
            sql_query = """
                SELECT
                    sd.id as doc_id,
                    sd.doc_type,
                    sd.entity_id,
                    sd.title,
                    sd.metadata,
                    SUM(si.frequency)::FLOAT / (1.0 + COUNT(DISTINCT si.term)::FLOAT) as relevance_score
                FROM search_documents sd
                JOIN search_index si ON sd.id = si.doc_id
                WHERE si.term = ANY(%s)
            """

            params = [search_terms]

            # Add doc_type filter if provided
            if doc_type:
                sql_query += " AND sd.doc_type = %s"
                params.append(doc_type)

            # Add metadata filters if provided
            if filters:
                for key, value in filters.items():
                    sql_query += f" AND sd.metadata->>'{key}' = %s"
                    params.append(str(value))

            sql_query += """
                GROUP BY sd.id, sd.doc_type, sd.entity_id, sd.title, sd.metadata
                ORDER BY relevance_score DESC
                LIMIT %s
            """
            params.append(limit)

            results = execute_query(sql_query, tuple(params))

            # Track search statistics
            self._track_search(query, len(results) if results else 0)

            # Parse metadata JSON
            if results:
                for result in results:
                    if isinstance(result['metadata'], str):
                        result['metadata'] = json.loads(result['metadata'])

            return results or []

        except Exception as e:
            self.logger.error(f"Error searching: {e}", exc_info=True)
            return []

    def autocomplete(self, prefix: str, doc_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get autocomplete suggestions based on a prefix.

        Args:
            prefix: Search prefix
            doc_type: Optional document type filter
            limit: Maximum number of suggestions

        Returns:
            List of autocomplete suggestions
        """
        try:
            if not prefix or len(prefix) < 2:
                return []

            query = """
                SELECT DISTINCT
                    title as suggestion,
                    entity_id,
                    doc_type,
                    metadata
                FROM search_documents
                WHERE LOWER(title) LIKE LOWER(%s)
            """

            params = [f"{prefix}%"]

            if doc_type:
                query += " AND doc_type = %s"
                params.append(doc_type)

            query += " ORDER BY title LIMIT %s"
            params.append(limit)

            results = execute_query(query, tuple(params))

            # Parse metadata JSON
            if results:
                for result in results:
                    if isinstance(result['metadata'], str):
                        result['metadata'] = json.loads(result['metadata'])

            return results or []

        except Exception as e:
            self.logger.error(f"Error in autocomplete: {e}", exc_info=True)
            return []

    def _track_search(self, query: str, result_count: int):
        """Track search statistics"""
        try:
            track_query = """
                INSERT INTO search_stats (query, result_count, search_count, last_searched_at)
                VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (query)
                DO UPDATE SET
                    search_count = search_stats.search_count + 1,
                    result_count = %s,
                    last_searched_at = CURRENT_TIMESTAMP
            """
            execute_query(track_query, (query, result_count, result_count))
        except Exception as e:
            # Don't fail the search if tracking fails
            self.logger.warning(f"Failed to track search: {e}")

    def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get the most popular search queries"""
        try:
            query = """
                SELECT query, search_count, result_count, last_searched_at
                FROM search_stats
                ORDER BY search_count DESC
                LIMIT %s
            """
            return execute_query(query, (limit,)) or []
        except Exception as e:
            self.logger.error(f"Error getting popular searches: {e}")
            return []

    def delete_document(self, doc_type: str, entity_id: str) -> bool:
        """Delete a document from the index"""
        try:
            query = "DELETE FROM search_documents WHERE doc_type = %s AND entity_id = %s"
            execute_query(query, (doc_type, entity_id))
            return True
        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            return False

    def clear_index(self, doc_type: Optional[str] = None) -> bool:
        """Clear the entire index or just documents of a specific type"""
        try:
            if doc_type:
                query = "DELETE FROM search_documents WHERE doc_type = %s"
                execute_query(query, (doc_type,))
            else:
                execute_query("TRUNCATE search_documents, search_index, search_stats CASCADE")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing index: {e}")
            return False

    def get_index_stats(self) -> Dict:
        """Get statistics about the search index"""
        try:
            stats = {}

            # Document counts by type
            doc_query = """
                SELECT doc_type, COUNT(*) as count
                FROM search_documents
                GROUP BY doc_type
            """
            doc_results = execute_query(doc_query)
            stats['documents_by_type'] = {row['doc_type']: row['count'] for row in doc_results} if doc_results else {}

            # Total documents
            total_docs = execute_query("SELECT COUNT(*) as count FROM search_documents")
            stats['total_documents'] = total_docs[0]['count'] if total_docs else 0

            # Total index terms
            total_terms = execute_query("SELECT COUNT(DISTINCT term) as count FROM search_index")
            stats['total_terms'] = total_terms[0]['count'] if total_terms else 0

            # Total index entries
            total_entries = execute_query("SELECT COUNT(*) as count FROM search_index")
            stats['total_index_entries'] = total_entries[0]['count'] if total_entries else 0

            return stats
        except Exception as e:
            self.logger.error(f"Error getting index stats: {e}")
            return {}


# Singleton instance
_search_engine = None

def get_search_engine() -> SearchEngine:
    """Get or create the search engine singleton"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
