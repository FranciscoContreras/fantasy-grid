-- Simplified Search Engine Schema
-- Core tables for inverted index

-- Documents table: stores all searchable entities
CREATE TABLE IF NOT EXISTS search_documents (
    id SERIAL PRIMARY KEY,
    doc_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_search_documents_type ON search_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_search_documents_metadata ON search_documents USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_search_documents_title ON search_documents(title);

-- Inverted index: maps terms to document IDs
CREATE TABLE IF NOT EXISTS search_index (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    doc_id INTEGER NOT NULL REFERENCES search_documents(id) ON DELETE CASCADE,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(term, doc_id)
);

CREATE INDEX IF NOT EXISTS idx_search_index_term ON search_index(term);
CREATE INDEX IF NOT EXISTS idx_search_index_doc_id ON search_index(doc_id);
CREATE INDEX IF NOT EXISTS idx_search_index_term_doc ON search_index(term, doc_id);

-- Search statistics
CREATE TABLE IF NOT EXISTS search_stats (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    result_count INTEGER DEFAULT 0,
    search_count INTEGER DEFAULT 1,
    last_searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(query)
);

CREATE INDEX IF NOT EXISTS idx_search_stats_count ON search_stats(search_count DESC);
