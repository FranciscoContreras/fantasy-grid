import os
import hashlib
import requests
import logging
from groq import Groq
from anthropic import Anthropic
from app.services.cache_service import cache_ai_response, get_cached_ai_response

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.grok_api_key = os.getenv('GROK_API_KEY')

        # Initialize clients
        self.groq_client = None
        self.anthropic_client = None

        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")

        if self.anthropic_api_key:
            try:
                self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
            except Exception as e:
                print(f"Failed to initialize Anthropic client: {e}")

    def generate_analysis(self, prompt, use_premium=False):
        """
        Generate AI analysis using Grok (default), Groq, or Claude

        Args:
            prompt: The analysis prompt
            use_premium: If True, use Claude API (costs money). If False, use Grok/Groq (free)

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

        # Generate response - prioritize Grok (free and powerful)
        if use_premium and self.anthropic_client:
            logger.info("Using Claude for premium analysis")
            response = self._generate_with_claude(prompt)
        elif self.grok_api_key:
            logger.info("Using Grok for analysis")
            response = self._generate_with_grok(prompt)
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

    def generate_matchup_reasoning(self, player_name, position, matchup_score, injury_status, opponent_defense=None, weather=None, historical_performance=None, defensive_scheme=None):
        """
        Generate reasoning for a player's matchup analysis

        Args:
            player_name: Player's name
            position: Player's position
            matchup_score: Numerical matchup score (0-100)
            injury_status: Current injury status
            opponent_defense: Optional opponent defense team abbreviation
            weather: Optional weather context string
            historical_performance: Optional historical stats vs this opponent
            defensive_scheme: Optional defensive coordinator and key players

        Returns:
            AI-generated reasoning text (concise snippet)
        """
        # Build context prompt
        matchup_quality = "favorable" if matchup_score > 70 else "difficult" if matchup_score < 50 else "average"
        injury_context = f" They are dealing with {injury_status} status." if injury_status != "HEALTHY" else ""
        defense_context = f" facing the {opponent_defense} defense" if opponent_defense else ""
        weather_context = f"\n- Weather conditions: {weather}" if weather else ""
        historical_context = f"\n- Historical performance: {historical_performance}" if historical_performance else ""
        scheme_context = f"\n- Defensive scheme: {defensive_scheme}" if defensive_scheme else ""

        prompt = f"""Analyze {player_name} ({position}){defense_context}:
- Matchup score: {matchup_score}/100 ({matchup_quality})
- Injury status: {injury_status}{injury_context}{weather_context}{historical_context}{scheme_context}

Provide a brief 1-2 sentence snippet explaining WHY to start or sit this player. Focus on the most important factors: defensive matchup, coordinator scheme, key defenders, historical performance, or weather."""

        # Use free tier for individual player analysis
        return self.generate_analysis(prompt, use_premium=False)
