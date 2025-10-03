"""
Validation schemas for analysis endpoints
"""
from marshmallow import Schema, fields, validate


class PercentageCalculatorSchema(Schema):
    """Schema for probability calculation"""
    factors = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        required=True,
        error_messages={'required': 'factors object is required'}
    )


class MatchupStrengthSchema(Schema):
    """Schema for matchup strength query parameters"""
    position = fields.Str(
        required=True,
        validate=validate.OneOf(['QB', 'RB', 'WR', 'TE', 'K', 'DEF']),
        error_messages={'required': 'position parameter is required'}
    )
    defense_team = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'defense_team parameter is required'}
    )
