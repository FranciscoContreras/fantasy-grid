"""
Data indexing service.
Fetches data from Grid Iron Mind API and indexes it for search.
"""
import logging
from typing import List, Optional
from app.services.api_client import FantasyAPIClient
from app.services.search.search_engine import SearchEngine, SearchDocument, get_search_engine

logger = logging.getLogger(__name__)


class SearchIndexer:
    """Handles indexing of data from the API into the search engine"""

    def __init__(self):
        self.api_client = FantasyAPIClient()
        self.search_engine = get_search_engine()
        self.logger = logging.getLogger(__name__)

    def index_player(self, player_data: dict) -> bool:
        """
        Index a single player.

        Args:
            player_data: Player data dict from API

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract player information
            player_id = str(player_data.get('id', ''))
            name = player_data.get('name', '')
            team = player_data.get('team', '')
            position = player_data.get('position', '')
            number = str(player_data.get('number', ''))
            status = player_data.get('status', 'active')

            # Build searchable content
            content_parts = [
                name,
                team,
                position,
                f"#{number}" if number else "",
                status
            ]

            # Add college if available
            college = player_data.get('college', '')
            if college:
                content_parts.append(college)

            content = ' '.join([p for p in content_parts if p])

            # Build metadata
            metadata = {
                'team': team,
                'position': position,
                'number': number,
                'status': status
            }

            # Add optional fields
            if college:
                metadata['college'] = college
            if 'height' in player_data:
                metadata['height'] = player_data['height']
            if 'weight' in player_data:
                metadata['weight'] = player_data['weight']
            if 'experience' in player_data:
                metadata['experience'] = player_data['experience']

            # Create document
            doc = SearchDocument(
                doc_type='player',
                entity_id=player_id,
                title=name,
                content=content,
                metadata=metadata
            )

            # Index the document
            doc_id = self.search_engine.add_document(doc)
            return doc_id is not None

        except Exception as e:
            self.logger.error(f"Error indexing player: {e}", exc_info=True)
            return False

    def index_all_players(self, limit: Optional[int] = None) -> int:
        """
        Index all players from the API.

        Args:
            limit: Optional limit on number of players to index

        Returns:
            Number of successfully indexed players
        """
        try:
            self.logger.info("Fetching players from API...")

            # Fetch players from API
            players_response = self.api_client.get_players(limit=limit or 1000)

            if not players_response or 'data' not in players_response:
                self.logger.error("No player data received from API")
                return 0

            players = players_response['data']
            self.logger.info(f"Fetched {len(players)} players from API")

            # Index each player
            success_count = 0
            for player in players:
                if self.index_player(player):
                    success_count += 1

            self.logger.info(f"Successfully indexed {success_count}/{len(players)} players")
            return success_count

        except Exception as e:
            self.logger.error(f"Error indexing players: {e}", exc_info=True)
            return 0

    def index_team(self, team_data: dict) -> bool:
        """
        Index a single team.

        Args:
            team_data: Team data dict from API

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract team information
            team_id = str(team_data.get('id', ''))
            name = team_data.get('name', '')
            city = team_data.get('city', '')
            abbreviation = team_data.get('abbreviation', '')
            conference = team_data.get('conference', '')
            division = team_data.get('division', '')

            # Build searchable content
            content_parts = [
                name,
                city,
                abbreviation,
                f"{city} {name}",
                conference,
                division
            ]

            content = ' '.join([p for p in content_parts if p])

            # Build metadata
            metadata = {
                'city': city,
                'abbreviation': abbreviation,
                'conference': conference,
                'division': division
            }

            # Add optional fields
            if 'stadium' in team_data:
                metadata['stadium'] = team_data['stadium']
                content += f" {team_data['stadium']}"

            # Create document
            doc = SearchDocument(
                doc_type='team',
                entity_id=team_id,
                title=f"{city} {name}" if city else name,
                content=content,
                metadata=metadata
            )

            # Index the document
            doc_id = self.search_engine.add_document(doc)
            return doc_id is not None

        except Exception as e:
            self.logger.error(f"Error indexing team: {e}", exc_info=True)
            return False

    def index_all_teams(self) -> int:
        """
        Index all teams from the API.

        Returns:
            Number of successfully indexed teams
        """
        try:
            self.logger.info("Fetching teams from API...")

            # Fetch teams from API
            teams_response = self.api_client.get_teams()

            if not teams_response or 'data' not in teams_response:
                self.logger.error("No team data received from API")
                return 0

            teams = teams_response['data']
            self.logger.info(f"Fetched {len(teams)} teams from API")

            # Index each team
            success_count = 0
            for team in teams:
                if self.index_team(team):
                    success_count += 1

            self.logger.info(f"Successfully indexed {success_count}/{len(teams)} teams")
            return success_count

        except Exception as e:
            self.logger.error(f"Error indexing teams: {e}", exc_info=True)
            return 0

    def rebuild_index(self, doc_type: Optional[str] = None) -> dict:
        """
        Rebuild the entire search index or a specific document type.

        Args:
            doc_type: Optional type to rebuild ('player', 'team', or None for all)

        Returns:
            Dict with rebuild statistics
        """
        stats = {
            'players_indexed': 0,
            'teams_indexed': 0,
            'success': False
        }

        try:
            # Clear existing index for the doc_type
            if doc_type:
                self.search_engine.clear_index(doc_type)
            else:
                self.search_engine.clear_index()

            # Rebuild based on doc_type
            if not doc_type or doc_type == 'player':
                stats['players_indexed'] = self.index_all_players()

            if not doc_type or doc_type == 'team':
                stats['teams_indexed'] = self.index_all_teams()

            stats['success'] = True
            self.logger.info(f"Index rebuild complete: {stats}")

        except Exception as e:
            self.logger.error(f"Error rebuilding index: {e}", exc_info=True)
            stats['error'] = str(e)

        return stats

    def update_player_index(self, player_id: str) -> bool:
        """
        Update the index for a single player by fetching fresh data from API.

        Args:
            player_id: Player ID to update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch player details from API
            player_data = self.api_client.get_player_details(player_id)

            if not player_data:
                self.logger.warning(f"No data found for player {player_id}")
                return False

            # Index the updated player data
            return self.index_player(player_data)

        except Exception as e:
            self.logger.error(f"Error updating player index: {e}", exc_info=True)
            return False


# Singleton instance
_indexer = None

def get_indexer() -> SearchIndexer:
    """Get or create the search indexer singleton"""
    global _indexer
    if _indexer is None:
        _indexer = SearchIndexer()
    return _indexer
