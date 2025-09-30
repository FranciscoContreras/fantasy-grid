import numpy as np
from sklearn.ensemble import RandomForestRegressor

class AIGrader:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

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
