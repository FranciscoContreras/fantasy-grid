"""Marshmallow schemas for request validation"""
from marshmallow import Schema, fields, validates, ValidationError, validate

# Player-related schemas
class PlayerSearchSchema(Schema):
    """Schema for player search requests"""
    query = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    position = fields.Str(required=False, allow_none=True, validate=validate.OneOf([
        'QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'FLEX'
    ]))

class PlayerAnalysisSchema(Schema):
    """Schema for player analysis requests"""
    player_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    week = fields.Int(required=True, validate=validate.Range(min=1, max=18))
    season = fields.Int(required=True, validate=validate.Range(min=2020, max=2030))
    opponent = fields.Str(required=False, allow_none=True, validate=validate.Length(max=10))

# Roster-related schemas
class CreateRosterSchema(Schema):
    """Schema for creating a new roster"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    league_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    scoring_type = fields.Str(required=False, validate=validate.OneOf(['PPR', 'STANDARD', 'HALF_PPR']))
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class AddPlayerToRosterSchema(Schema):
    """Schema for adding a player to a roster"""
    player_id = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    player_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    position = fields.Str(required=True, validate=validate.OneOf([
        'QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'FLEX', 'BENCH'
    ]))
    team = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    roster_slot = fields.Str(required=True, validate=validate.OneOf([
        'QB', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 'TE', 'FLEX', 'K', 'DEF', 'BENCH'
    ]))
    is_starter = fields.Bool(required=False)
    injury_status = fields.Str(required=False, allow_none=True, validate=validate.OneOf([
        'OUT', 'DOUBTFUL', 'QUESTIONABLE', 'PROBABLE', 'HEALTHY', None
    ]))

# Matchup-related schemas
class CreateMatchupSchema(Schema):
    """Schema for creating a matchup"""
    user_roster_id = fields.Int(required=True, validate=validate.Range(min=1))
    opponent_roster_id = fields.Int(required=True, validate=validate.Range(min=1))
    week = fields.Int(required=True, validate=validate.Range(min=1, max=18))
    season = fields.Int(required=True, validate=validate.Range(min=2020, max=2030))
    user_roster_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    opponent_roster_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))

    @validates('opponent_roster_id')
    def validate_different_rosters(self, value):
        """Ensure user and opponent rosters are different"""
        if 'user_roster_id' in self.context and value == self.context.get('user_roster_id'):
            raise ValidationError("Opponent roster must be different from user roster")

class AnalyzeMatchupSchema(Schema):
    """Schema for analyzing a matchup"""
    matchup_id = fields.Int(required=True, validate=validate.Range(min=1))

# Prediction-related schemas
class PredictionSchema(Schema):
    """Schema for prediction requests"""
    player_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    week = fields.Int(required=True, validate=validate.Range(min=1, max=18))
    season = fields.Int(required=True, validate=validate.Range(min=2020, max=2030))
    include_weather = fields.Bool(required=False)
    include_matchup = fields.Bool(required=False)

# Query parameter schemas
class WeekSeasonSchema(Schema):
    """Schema for week and season query parameters"""
    week = fields.Int(required=False, validate=validate.Range(min=1, max=18))
    season = fields.Int(required=False, validate=validate.Range(min=2020, max=2030))

class RosterIdSchema(Schema):
    """Schema for roster ID parameter"""
    roster_id = fields.Int(required=True, validate=validate.Range(min=1))

class UserIdSchema(Schema):
    """Schema for user ID parameter"""
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
