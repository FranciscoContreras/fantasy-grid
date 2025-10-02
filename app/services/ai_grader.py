import numpy as np
from sklearn.ensemble import RandomForestRegressor

class AIGrader:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.use_advanced_stats = True  # Enable advanced stats from API v2

    def train(self, training_data, labels):
        """
        Train the model on historical data
        training_data: historical player stats
        labels: actual fantasy points scored
        """
        self.model.fit(training_data, labels)
        self.is_trained = True

    def grade_player(self, player_features):
        """
        Grade a player based on features
        Returns: {grade, predicted_points, confidence}
        """
        if not self.is_trained:
            return self._fallback_grading(player_features)

        prediction = self.model.predict([player_features])[0]

        grade = self._score_to_grade(prediction)
        confidence = self._calculate_confidence(player_features)

        return {
            'grade': grade,
            'predicted_points': round(prediction, 2),
            'confidence': confidence
        }

    def _score_to_grade(self, score):
        """Convert predicted points to letter grade"""
        if score >= 20:
            return 'A+'
        elif score >= 17:
            return 'A'
        elif score >= 14:
            return 'B+'
        elif score >= 11:
            return 'B'
        elif score >= 8:
            return 'C'
        else:
            return 'D'

    def _calculate_confidence(self, features):
        """Calculate confidence percentage for prediction"""
        # Simplified confidence calculation
        # In production, this would use model variance, feature quality, etc.
        return 85.0

    def _fallback_grading(self, features):
        """Simple rule-based grading when model not trained"""
        # features: [avg_points, matchup_score, weather_impact, consistency]
        avg_points = features[0] if len(features) > 0 else 10
        matchup = features[1] if len(features) > 1 else 50
        weather = features[2] if len(features) > 2 else 100

        # Weighted prediction
        predicted = avg_points * (matchup / 100) * (weather / 100)

        return {
            'grade': self._score_to_grade(predicted),
            'predicted_points': round(predicted, 2),
            'confidence': 60.0
        }

    def grade_player_with_advanced_stats(self, player_features, advanced_stats=None):
        """
        Grade a player using both traditional and advanced stats (API v2).
        
        Args:
            player_features: Traditional features (avg_points, matchup, weather, etc.)
            advanced_stats: Dictionary with Next Gen Stats, EPA, CPOE
        
        Returns:
            {grade, predicted_points, confidence, insights}
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Start with base prediction
        base_prediction = self.grade_player(player_features)
        
        if not advanced_stats or not self.use_advanced_stats:
            return base_prediction
        
        # Enhance prediction with advanced stats
        predicted_points = base_prediction['predicted_points']
        confidence = base_prediction['confidence']
        insights = []
        
        # QB-specific advanced stat adjustments
        if advanced_stats.get('position') in ['QB']:
            cpoe = advanced_stats.get('cpoe', 0)
            epa_per_play = advanced_stats.get('epa_per_play', 0)
            time_to_throw = advanced_stats.get('time_to_throw', 2.5)
            
            # CPOE (Completion % Over Expected) - positive is good
            if cpoe and cpoe > 3.0:
                predicted_points *= 1.10
                confidence += 5
                insights.append(f"Exceptional accuracy (CPOE: +{cpoe:.1f}%)")
            elif cpoe and cpoe < -3.0:
                predicted_points *= 0.90
                confidence -= 5
                insights.append(f"Below expected completion rate (CPOE: {cpoe:.1f}%)")
            
            # EPA (Expected Points Added) - measures efficiency
            if epa_per_play and epa_per_play > 0.2:
                predicted_points *= 1.08
                confidence += 3
                insights.append(f"Elite efficiency (EPA/play: {epa_per_play:.2f})")
            elif epa_per_play and epa_per_play < -0.1:
                predicted_points *= 0.92
                confidence -= 3
                insights.append(f"Struggling with efficiency (EPA/play: {epa_per_play:.2f})")
            
            # Time to throw - pressure indicator
            if time_to_throw and time_to_throw < 2.3:
                insights.append(f"Quick release ({time_to_throw:.1f}s) - good vs pressure")
            elif time_to_throw and time_to_throw > 2.8:
                insights.append(f"Holds ball longer ({time_to_throw:.1f}s) - risky vs blitz")
        
        # WR/TE-specific advanced stat adjustments
        elif advanced_stats.get('position') in ['WR', 'TE']:
            avg_separation = advanced_stats.get('avg_separation', 0)
            avg_yac = advanced_stats.get('avg_yac', 0)
            target_share = advanced_stats.get('target_share', 0)
            wopr = advanced_stats.get('wopr', 0)  # Weighted Opportunity Rating
            
            # Average Separation - measures route running
            if avg_separation and avg_separation > 3.5:
                predicted_points *= 1.12
                confidence += 6
                insights.append(f"Excellent route running ({avg_separation:.1f} yd separation)")
            elif avg_separation and avg_separation < 2.0:
                predicted_points *= 0.88
                confidence -= 4
                insights.append(f"Struggles creating separation ({avg_separation:.1f} yd)")
            
            # Yards After Catch
            if avg_yac and avg_yac > 6.0:
                predicted_points *= 1.08
                insights.append(f"Elite YAC ability ({avg_yac:.1f} yd/catch)")
            
            # Target Share - volume indicator
            if target_share and target_share > 25:
                confidence += 8
                insights.append(f"High target share ({target_share:.1f}%)")
            elif target_share and target_share < 12:
                predicted_points *= 0.90
                confidence -= 8
                insights.append(f"Low target share ({target_share:.1f}%)")
            
            # WOPR (Weighted Opportunity Rating) - combines targets + air yards
            if wopr and wopr > 0.7:
                predicted_points *= 1.10
                confidence += 5
                insights.append(f"Dominant opportunity (WOPR: {wopr:.2f})")
        
        # RB-specific advanced stat adjustments
        elif advanced_stats.get('position') in ['RB']:
            rush_yards_over_expected = advanced_stats.get('rush_yards_over_expected_per_att', 0)
            success_rate = advanced_stats.get('success_rate', 0)
            snap_share = advanced_stats.get('snap_share', 0)
            
            # Yards Over Expected - measures vision/elusiveness
            if rush_yards_over_expected and rush_yards_over_expected > 0.5:
                predicted_points *= 1.15
                confidence += 7
                insights.append(f"Exceptional vision (+{rush_yards_over_expected:.1f} yd over expected)")
            elif rush_yards_over_expected and rush_yards_over_expected < -0.3:
                predicted_points *= 0.85
                confidence -= 6
                insights.append(f"Below expected rushing efficiency")
            
            # Success Rate - % of positive EPA plays
            if success_rate and success_rate > 50:
                predicted_points *= 1.08
                insights.append(f"Highly efficient ({success_rate:.1f}% success rate)")
            
            # Snap Share - workload indicator
            if snap_share and snap_share > 70:
                confidence += 10
                insights.append(f"Workhorse role ({snap_share:.1f}% snaps)")
            elif snap_share and snap_share < 40:
                predicted_points *= 0.85
                confidence -= 10
                insights.append(f"Limited role ({snap_share:.1f}% snaps)")
        
        # Recalculate grade based on adjusted points
        new_grade = self._score_to_grade(predicted_points)
        
        # Cap confidence at 95%
        confidence = min(confidence, 95.0)
        
        logger.info(f"Advanced stats grading: {new_grade} ({predicted_points:.1f} pts, {confidence:.1f}% confidence)")
        
        return {
            'grade': new_grade,
            'predicted_points': round(predicted_points, 2),
            'confidence': round(confidence, 1),
            'insights': insights,
            'advanced_stats_used': True
        }
    
    def extract_advanced_features(self, advanced_stats_data):
        """
        Extract relevant features from API v2 advanced stats response.
        
        Args:
            advanced_stats_data: Raw response from get_player_advanced_stats()
        
        Returns:
            Dictionary of normalized advanced stats
        """
        if not advanced_stats_data:
            return {}
        
        return {
            'position': advanced_stats_data.get('position'),
            # QB stats
            'cpoe': advanced_stats_data.get('cpoe'),
            'epa_per_play': advanced_stats_data.get('epa_per_play'),
            'time_to_throw': advanced_stats_data.get('time_to_throw'),
            'avg_air_yards': advanced_stats_data.get('avg_air_yards'),
            # WR/TE stats
            'avg_separation': advanced_stats_data.get('avg_separation'),
            'avg_yac': advanced_stats_data.get('avg_yac'),
            'target_share': advanced_stats_data.get('target_share'),
            'wopr': advanced_stats_data.get('wopr'),
            'racr': advanced_stats_data.get('racr'),
            # RB stats
            'rush_yards_over_expected_per_att': advanced_stats_data.get('rush_yards_over_expected_per_att'),
            'success_rate': advanced_stats_data.get('success_rate'),
            'snap_share': advanced_stats_data.get('snap_share'),
            # General
            'epa_total': advanced_stats_data.get('epa_total'),
            'snap_count': advanced_stats_data.get('snap_count')
        }
