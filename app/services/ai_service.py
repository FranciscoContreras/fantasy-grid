import os
import hashlib
import requests
import logging
from groq import Groq
from anthropic import Anthropic
import google.generativeai as genai
from app.services.cache_service import cache_ai_response, get_cached_ai_response

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBHlAoGFQVlAuuQAv_PkEo9JXkMs28CNhA')
        
        # Initialize clients
        self.groq_client = None
        self.anthropic_client = None
        self.gemini_model = None
        
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        
        if self.anthropic_api_key:
            try:
                self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

    def generate_analysis(self, prompt, use_premium=False):
        """
        Generate AI analysis using Gemini (default), Grok, Groq, or Claude

        Args:
            prompt: The analysis prompt
            use_premium: If True, use Claude API (costs money). If False, use free options

        Returns:
            Generated text analysis
        """
        # Check cache first
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cached = get_cached_ai_response(prompt_hash)
        if cached:
            logger.info(f"Using cached AI response for prompt hash: {prompt_hash}")
            return cached

        logger.info(f"Generating new AI analysis (use_premium={use_premium})")
        logger.debug(f"Prompt: {prompt[:200]}...")

        # Generate response - prioritize Gemini (free and powerful)
        if use_premium and self.anthropic_client:
            logger.info("Using Claude for premium analysis")
            response = self._generate_with_claude(prompt)
        elif self.gemini_model:
            logger.info("Using Gemini for analysis")
            response = self._generate_with_gemini(prompt)
        elif self.groq_client:
            logger.info("Using Groq for analysis")
            response = self._generate_with_groq(prompt)
        else:
            logger.warning("No AI service available, using fallback")
            response = self._generate_fallback(prompt)

        # Cache the response
        if response:
            cache_ai_response(prompt_hash, response)
            logger.info(f"Cached AI response: {response[:100]}...")

        return response

    def _generate_with_grok(self, prompt):
        """Use Grok API (xAI's Grok-4-latest)"""
        try:
            logger.debug(f"Calling Grok API with prompt: {prompt[:100]}...")
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.grok_api_key}'
                },
                json={
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert fantasy football analyst with deep knowledge of NFL players, defenses, and matchups. Provide concise, data-driven insights in 2-3 sentences.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'model': 'grok-4-latest',
                    'stream': False,
                    'temperature': 0.7
                },
                timeout=30  # Increased from 10 to 30 seconds
            )
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content'].strip()
            logger.info(f"Grok API success: {result[:100]}...")
            return result
        except requests.exceptions.Timeout:
            logger.error("Grok API timeout after 30s")
            # Fallback to Groq if Grok times out
            if self.groq_client:
                logger.info("Falling back to Groq due to timeout")
                return self._generate_with_groq(prompt)
            logger.warning("No Groq available, using rule-based fallback")
            return self._generate_fallback(prompt)
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            # Fallback to Groq if Grok fails
            if self.groq_client:
                logger.info("Falling back to Groq")
                return self._generate_with_groq(prompt)
            logger.warning("No Groq available, using rule-based fallback")
            return self._generate_fallback(prompt)

    def _generate_with_gemini(self, prompt):
        """Use Google Gemini API (free tier)"""
        try:
            logger.debug(f"Calling Gemini API with prompt: {prompt[:100]}...")
            response = self.gemini_model.generate_content(
                f"""You are an expert fantasy football analyst with deep knowledge of NFL players, defenses, and matchups. Provide concise, data-driven insights in 2-3 sentences.

{prompt}""",
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 150,
                }
            )
            result = response.text.strip()
            logger.info(f"Gemini API success: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback to Groq if Gemini fails
            if self.groq_client:
                logger.info("Falling back to Groq")
                return self._generate_with_groq(prompt)
            logger.warning("No Groq available, using rule-based fallback")
            return self._generate_fallback(prompt)

    def _generate_with_groq(self, prompt):
        """Use Groq's free API (Llama 3.1 70B)"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Fast and free
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fantasy football analyst. Provide concise, data-driven insights in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._generate_fallback(prompt)

    def _generate_with_claude(self, prompt):
        """Use Claude API for premium analysis"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert fantasy football analyst. Provide concise, data-driven insights in 2-3 sentences.\n\n{prompt}"
                    }
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Claude API error: {e}")
            return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt):
        """Simple rule-based fallback when no AI is available"""
        # Parse the prompt to extract key info
        if "favorable matchup" in prompt.lower():
            return "Strong matchup fundamentals suggest starting this player with confidence."
        elif "difficult matchup" in prompt.lower():
            return "Challenging matchup conditions recommend benching or monitoring closely."
        else:
            return "Moderate matchup profile warrants careful consideration of recent form and injury status."

    def generate_matchup_reasoning(self, player_name, position, team, matchup_score, injury_status, opponent_defense=None, opponent_roster=None, defensive_stats=None, weather=None, historical_performance=None, defensive_scheme=None, injury_history=None, weather_forecast=None):
        """
        Generate reasoning for a player's matchup analysis

        Args:
            player_name: Player's name
            position: Player's position
            team: Player's team abbreviation
            matchup_score: Numerical matchup score (0-100)
            injury_status: Current injury status
            opponent_defense: Optional opponent defense team abbreviation
            opponent_roster: Optional dict of opponent's offensive players
            defensive_stats: Optional dict of opponent's defensive rankings
            weather: Optional weather context string
            historical_performance: Optional historical stats vs this opponent
            defensive_scheme: Optional defensive coordinator and key players
            injury_history: Optional list of past injuries
            weather_forecast: Optional upcoming game weather forecast

        Returns:
            AI-generated reasoning text (concise snippet)
        """
        # Build context prompt
        matchup_quality = "favorable" if matchup_score > 70 else "difficult" if matchup_score < 50 else "average"
        injury_context = f" They are dealing with {injury_status} status." if injury_status != "HEALTHY" else ""
        defense_context = f" vs {opponent_defense}" if opponent_defense else ""

        # Enhanced opponent context
        roster_context = ""
        if opponent_roster:
            # Build concise roster summary
            roster_parts = []
            for pos, players in opponent_roster.items():
                if players:
                    names = [p['name'] for p in players[:2]]  # Top 2 per position
                    if names:
                        roster_parts.append(f"{pos}: {', '.join(names)}")
            if roster_parts:
                roster_context = f"\n- Opponent roster: {'; '.join(roster_parts)}"

        # Enhanced defensive stats context
        defense_stats_context = ""
        if defensive_stats:
            ppg = defensive_stats.get('points_allowed_per_game', 0)
            def_rank = defensive_stats.get('defensive_rank', 16)

            # Position-specific defensive metrics
            if position in ['QB', 'WR', 'TE']:
                pass_def_rank = defensive_stats.get('pass_defense_rank', 16)
                pass_yards = defensive_stats.get('pass_yards_allowed_per_game', 0)
                defense_stats_context = f"\n- {opponent_defense} pass defense: Rank #{pass_def_rank}, {pass_yards:.0f} yds/game, {ppg:.1f} PPG allowed"
            elif position == 'RB':
                rush_def_rank = defensive_stats.get('rush_defense_rank', 16)
                rush_yards = defensive_stats.get('rush_yards_allowed_per_game', 0)
                defense_stats_context = f"\n- {opponent_defense} run defense: Rank #{rush_def_rank}, {rush_yards:.0f} yds/game, {ppg:.1f} PPG allowed"
            else:
                defense_stats_context = f"\n- {opponent_defense} defense: Rank #{def_rank}, {ppg:.1f} PPG allowed"

        # NEW: Injury history context
        injury_history_context = ""
        if injury_history and len(injury_history) > 0:
            # Summarize recent injuries (last 3)
            recent_injuries = injury_history[:3]
            injury_types = [inj.get('injury_type', 'unknown') for inj in recent_injuries]
            if injury_types:
                injury_history_context = f"\n- Injury history: {', '.join(injury_types[:2])}"

        # NEW: Weather forecast context (prefer forecast over current)
        weather_context = ""
        if weather_forecast:
            conditions = weather_forecast.get('conditions', '')
            temp = weather_forecast.get('temperature')
            wind = weather_forecast.get('wind_speed')
            if conditions or temp or wind:
                weather_parts = []
                if conditions:
                    weather_parts.append(conditions)
                if temp:
                    weather_parts.append(f"{temp}°F")
                if wind:
                    weather_parts.append(f"{wind}mph wind")
                weather_context = f"\n- Forecast: {', '.join(weather_parts)}"
        elif weather:
            weather_context = f"\n- Weather: {weather}"

        historical_context = f"\n- Historical performance: {historical_performance}" if historical_performance else ""
        scheme_context = f"\n- Defensive scheme: {defensive_scheme}" if defensive_scheme else ""

        prompt = f"""Analyze {player_name} ({team} {position}){defense_context}:
- Matchup score: {matchup_score}/100 ({matchup_quality})
- Injury status: {injury_status}{injury_context}{injury_history_context}{defense_stats_context}{scheme_context}{roster_context}{historical_context}{weather_context}

Provide a concise 1-2 sentence analysis with clear START/SIT/CONSIDER recommendation. Focus on the most impactful factors: matchup strength, defensive rankings, injury concerns, and weather impact."""

        # Use free tier for individual player analysis
        return self.generate_analysis(prompt, use_premium=False)
