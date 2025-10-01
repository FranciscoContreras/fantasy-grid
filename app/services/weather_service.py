import os
import requests
from datetime import datetime, timedelta
import logging
from app.services.cache_service import cache_weather, get_cached_weather

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Weather service for fetching game day weather conditions.
    Uses OpenWeatherMap free tier (1000 calls/day).
    """

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'https://api.openweathermap.org/data/2.5'

        # NFL stadium locations (city coordinates)
        self.stadium_locations = {
            'ARI': {'city': 'Glendale', 'lat': 33.5276, 'lon': -112.2626, 'dome': True},
            'ATL': {'city': 'Atlanta', 'lat': 33.7555, 'lon': -84.4009, 'dome': True},
            'BAL': {'city': 'Baltimore', 'lat': 39.2780, 'lon': -76.6227, 'dome': False},
            'BUF': {'city': 'Buffalo', 'lat': 42.7738, 'lon': -78.7870, 'dome': False},
            'CAR': {'city': 'Charlotte', 'lat': 35.2258, 'lon': -80.8528, 'dome': False},
            'CHI': {'city': 'Chicago', 'lat': 41.8623, 'lon': -87.6167, 'dome': False},
            'CIN': {'city': 'Cincinnati', 'lat': 39.0954, 'lon': -84.5160, 'dome': False},
            'CLE': {'city': 'Cleveland', 'lat': 41.5061, 'lon': -81.6995, 'dome': False},
            'DAL': {'city': 'Arlington', 'lat': 32.7473, 'lon': -97.0945, 'dome': True},
            'DEN': {'city': 'Denver', 'lat': 39.7439, 'lon': -105.0201, 'dome': False},
            'DET': {'city': 'Detroit', 'lat': 42.3400, 'lon': -83.0456, 'dome': True},
            'GB': {'city': 'Green Bay', 'lat': 44.5013, 'lon': -88.0622, 'dome': False},
            'HOU': {'city': 'Houston', 'lat': 29.6847, 'lon': -95.4107, 'dome': True},
            'IND': {'city': 'Indianapolis', 'lat': 39.7601, 'lon': -86.1639, 'dome': True},
            'JAX': {'city': 'Jacksonville', 'lat': 30.3240, 'lon': -81.6373, 'dome': False},
            'KC': {'city': 'Kansas City', 'lat': 39.0489, 'lon': -94.4839, 'dome': False},
            'LAC': {'city': 'Inglewood', 'lat': 33.9535, 'lon': -118.3390, 'dome': False},
            'LAR': {'city': 'Inglewood', 'lat': 33.9535, 'lon': -118.3390, 'dome': False},
            'LV': {'city': 'Las Vegas', 'lat': 36.0909, 'lon': -115.1833, 'dome': True},
            'MIA': {'city': 'Miami Gardens', 'lat': 25.9580, 'lon': -80.2389, 'dome': False},
            'MIN': {'city': 'Minneapolis', 'lat': 44.9738, 'lon': -93.2577, 'dome': True},
            'NE': {'city': 'Foxborough', 'lat': 42.0909, 'lon': -71.2643, 'dome': False},
            'NO': {'city': 'New Orleans', 'lat': 29.9511, 'lon': -90.0812, 'dome': True},
            'NYG': {'city': 'East Rutherford', 'lat': 40.8128, 'lon': -74.0742, 'dome': False},
            'NYJ': {'city': 'East Rutherford', 'lat': 40.8128, 'lon': -74.0742, 'dome': False},
            'PHI': {'city': 'Philadelphia', 'lat': 39.9008, 'lon': -75.1675, 'dome': False},
            'PIT': {'city': 'Pittsburgh', 'lat': 40.4468, 'lon': -80.0158, 'dome': False},
            'SEA': {'city': 'Seattle', 'lat': 47.5952, 'lon': -122.3316, 'dome': False},
            'SF': {'city': 'Santa Clara', 'lat': 37.4030, 'lon': -121.9697, 'dome': False},
            'TB': {'city': 'Tampa', 'lat': 27.9759, 'lon': -82.5033, 'dome': False},
            'TEN': {'city': 'Nashville', 'lat': 36.1665, 'lon': -86.7713, 'dome': False},
            'WAS': {'city': 'Landover', 'lat': 38.9076, 'lon': -76.8645, 'dome': False},
        }

    def get_game_weather(self, team_abbr, game_date=None):
        """
        Get weather forecast for a team's home stadium.

        Args:
            team_abbr: Team abbreviation (e.g., 'KC', 'BUF')
            game_date: Optional datetime for the game (defaults to next Sunday)

        Returns:
            Weather data dict or None if API unavailable
        """
        # Check cache first
        cached = get_cached_weather(team_abbr)
        if cached:
            logger.debug(f"Using cached weather for {team_abbr}")
            return cached

        # If no API key, return None (app will use fallback)
        if not self.api_key:
            logger.warning("No OpenWeather API key configured")
            return None

        # Get stadium location
        location = self.stadium_locations.get(team_abbr)
        if not location:
            logger.warning(f"Unknown team abbreviation: {team_abbr}")
            return None

        # If it's a dome, weather doesn't matter
        if location['dome']:
            dome_weather = {
                'condition': 'Dome',
                'temperature': 72,
                'wind_speed': 0,
                'precipitation_chance': 0,
                'impact': 'No impact',
                'dome': True
            }
            cache_weather(team_abbr, dome_weather)
            return dome_weather

        try:
            # Use forecast API for future games
            params = {
                'lat': location['lat'],
                'lon': location['lon'],
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }

            response = requests.get(f'{self.base_url}/forecast', params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Get forecast for game time (usually Sunday 1pm ET)
            # For now, use first forecast available
            if data.get('list') and len(data['list']) > 0:
                forecast = data['list'][0]

                weather_data = {
                    'condition': forecast['weather'][0]['main'],
                    'description': forecast['weather'][0]['description'],
                    'temperature': round(forecast['main']['temp']),
                    'wind_speed': round(forecast['wind']['speed']),
                    'precipitation_chance': int(forecast.get('pop', 0) * 100),
                    'dome': False
                }

                # Calculate weather impact on play
                weather_data['impact'] = self._calculate_weather_impact(weather_data)

                # Cache the result
                cache_weather(team_abbr, weather_data)

                return weather_data

            return None

        except Exception as e:
            logger.error(f"Weather API error for {team_abbr}: {e}")
            return None

    def _calculate_weather_impact(self, weather):
        """
        Calculate how weather conditions impact fantasy performance.

        Returns:
            String describing the impact level
        """
        impacts = []

        # Temperature impact
        temp = weather['temperature']
        if temp < 20:
            impacts.append('Extreme cold may limit passing game')
        elif temp > 95:
            impacts.append('High heat may affect player stamina')

        # Wind impact (affects passing and kicking)
        wind = weather['wind_speed']
        if wind > 20:
            impacts.append('High winds significantly impact passing and kicking')
        elif wind > 15:
            impacts.append('Moderate winds may affect passing game')

        # Precipitation impact
        precip = weather['precipitation_chance']
        condition = weather['condition'].lower()
        if 'rain' in condition or 'snow' in condition or precip > 60:
            impacts.append('Wet conditions favor run game over passing')

        if not impacts:
            return 'No significant impact'

        return '; '.join(impacts)

    def get_weather_adjustment_factor(self, position, weather):
        """
        Get a multiplier to adjust fantasy projections based on weather.

        Args:
            position: Player position (QB, RB, WR, TE, K, DEF)
            weather: Weather data dict from get_game_weather()

        Returns:
            Float multiplier (0.8 - 1.1)
        """
        if not weather or weather.get('dome'):
            return 1.0  # No adjustment for domes

        adjustment = 1.0
        temp = weather['temperature']
        wind = weather['wind_speed']
        condition = weather['condition'].lower()

        # Position-specific adjustments
        if position == 'QB':
            # QBs affected by wind and cold
            if wind > 20:
                adjustment *= 0.85
            elif wind > 15:
                adjustment *= 0.92

            if temp < 20:
                adjustment *= 0.90

            if 'rain' in condition or 'snow' in condition:
                adjustment *= 0.88

        elif position in ['WR', 'TE']:
            # Pass catchers affected similarly to QBs
            if wind > 20:
                adjustment *= 0.87
            elif wind > 15:
                adjustment *= 0.93

            if temp < 20:
                adjustment *= 0.92

            if 'rain' in condition or 'snow' in condition:
                adjustment *= 0.90

        elif position == 'RB':
            # RBs benefit from bad weather (more running)
            if wind > 15 or 'rain' in condition or 'snow' in condition:
                adjustment *= 1.08

            if temp < 20:
                adjustment *= 0.95  # Still slightly negative

        elif position == 'K':
            # Kickers heavily affected by wind and precipitation
            if wind > 20:
                adjustment *= 0.75
            elif wind > 15:
                adjustment *= 0.85
            elif wind > 10:
                adjustment *= 0.92

            if 'rain' in condition or 'snow' in condition:
                adjustment *= 0.85

            if temp < 20:
                adjustment *= 0.90

        elif position == 'DEF':
            # Defenses benefit from bad weather (more turnovers)
            if wind > 15 or 'rain' in condition or 'snow' in condition:
                adjustment *= 1.05

        # Cap adjustments
        return max(0.8, min(1.1, adjustment))
