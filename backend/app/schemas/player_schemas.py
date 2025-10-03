"""
Validation schemas for player-related endpoints
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class PlayerSearchSchema(Schema):
    """Schema for player search query parameters"""
    q = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Query parameter "q" is required'}
    )
    position = fields.Str(
        validate=validate.OneOf(['QB', 'RB', 'WR', 'TE', 'K', 'DEF']),
        allow_none=True
    )


class PlayerAnalysisSchema(Schema):
    """Schema for player analysis query parameters"""
    opponent = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'Query parameter "opponent" is required'}
    )
    location = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True
    )


class PlayerComparisonSchema(Schema):
    """Schema for comparing multiple players"""
    player_ids = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        required=True,
        validate=validate.Length(min=2, max=10),
        error_messages={
            'required': 'player_ids is required',
            'length': 'Must provide 2-10 player IDs for comparison'
        }
    )
    opponent_ids = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)),
        validate=validate.Length(max=10),
        allow_none=True
    )

    @validates_schema
    def validate_opponent_ids(self, data, **kwargs):
        """Ensure opponent_ids length matches player_ids if provided"""
        if 'opponent_ids' in data and data['opponent_ids']:
            if len(data['opponent_ids']) != len(data['player_ids']):
                raise ValidationError(
                    'opponent_ids length must match player_ids length',
                    field_name='opponent_ids'
                )
