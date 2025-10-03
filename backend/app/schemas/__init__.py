"""
Marshmallow validation schemas for Fantasy Grid API
"""
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError


def validate_json(schema_class):
    """
    Decorator to validate JSON request body against a Marshmallow schema

    Usage:
        @bp.route('/endpoint', methods=['POST'])
        @validate_json(MySchema)
        def my_endpoint(validated_data):
            # validated_data is sanitized and validated
            pass
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            try:
                schema = schema_class()
                validated_data = schema.load(request.json)
                return f(validated_data, *args, **kwargs)
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation failed',
                    'messages': err.messages
                }), 400
            except Exception as e:
                return jsonify({'error': 'Invalid request data'}), 400

        return wrapper
    return decorator


def validate_query_params(schema_class):
    """
    Decorator to validate query parameters against a Marshmallow schema

    Usage:
        @bp.route('/endpoint', methods=['GET'])
        @validate_query_params(MyQuerySchema)
        def my_endpoint(validated_params):
            # validated_params is sanitized and validated
            pass
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                schema = schema_class()
                validated_params = schema.load(request.args)
                return f(validated_params, *args, **kwargs)
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation failed',
                    'messages': err.messages
                }), 400
            except Exception as e:
                return jsonify({'error': 'Invalid query parameters'}), 400

        return wrapper
    return decorator
