"""
Async API client for Grid Iron Mind NFL API
Solves N+1 query problems by batching requests
"""
import aiohttp
import asyncio
import os
from typing import List, Dict, Optional


class AsyncFantasyAPIClient:
    """Async API client for batched requests to solve N+1 problems"""

    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'https://nfl.wearemachina.com/api/v1')
        self.api_key = os.getenv('API_KEY')

    def _get_headers(self, include_api_key=False):
        headers = {'Content-Type': 'application/json'}
        if include_api_key and self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    async def _fetch(self, session: aiohttp.ClientSession, url: str, headers: dict) -> dict:
        """Fetch a single URL"""
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            return {'error': str(e)}

    async def get_multiple_players(self, player_ids: List[str]) -> List[dict]:
        """
        Fetch multiple players concurrently
        Solves N+1 problem for player comparison endpoint

        Args:
            player_ids: List of player IDs to fetch

        Returns:
            List of player data dicts (same order as input)
        """
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch(session, f'{self.base_url}/players/{pid}', headers)
                for pid in player_ids
            ]
            results = await asyncio.gather(*tasks)
            return results

    async def get_multiple_defenses(self, team_ids: List[str]) -> List[dict]:
        """
        Fetch multiple defense stats concurrently
        Solves N+1 problem for roster prediction endpoint

        Args:
            team_ids: List of team IDs to fetch

        Returns:
            List of defense stats dicts (same order as input)
        """
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch(session, f'{self.base_url}/teams/{tid}', headers)
                for tid in team_ids
            ]
            results = await asyncio.gather(*tasks)
            return results

    async def get_players_and_defenses(
        self,
        player_ids: List[str],
        team_ids: List[str]
    ) -> tuple[List[dict], List[dict]]:
        """
        Fetch players and defenses concurrently
        Maximum parallelization for roster predictions

        Args:
            player_ids: List of player IDs
            team_ids: List of team/defense IDs

        Returns:
            Tuple of (players, defenses) lists
        """
        players_task = self.get_multiple_players(player_ids)
        defenses_task = self.get_multiple_defenses(team_ids)

        players, defenses = await asyncio.gather(players_task, defenses_task)
        return players, defenses

    async def batch_player_analysis(
        self,
        player_ids: List[str],
        opponent_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Batch analyze multiple players
        Optimized for /api/analysis/compare endpoint

        Args:
            player_ids: List of player IDs to analyze
            opponent_ids: Optional list of opponent team IDs (same length)

        Returns:
            List of analysis results with player and defense data
        """
        # Fetch all players concurrently
        players = await self.get_multiple_players(player_ids)

        # Fetch all defenses if opponents provided
        defenses = []
        if opponent_ids:
            defenses = await self.get_multiple_defenses(opponent_ids)

        # Combine results
        results = []
        for i, player in enumerate(players):
            result = {
                'player_id': player_ids[i],
                'player': player.get('data', player) if 'data' in player else player
            }

            if opponent_ids and i < len(opponent_ids):
                result['defense'] = defenses[i].get('data', defenses[i]) if 'data' in defenses[i] else defenses[i]
                result['opponent_id'] = opponent_ids[i]

            results.append(result)

        return results


def run_async(coroutine):
    """
    Run async function in Flask sync context
    Creates new event loop if needed
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coroutine)
