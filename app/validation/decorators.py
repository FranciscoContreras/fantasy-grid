"""Decorators for request validation"""
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_request(schema_class, location='json'):
    """
    Decorator to validate request data using a Marshmallow schema

    Args:
        schema_class: The Marshmallow schema class to use for validation
        location: Where to get the data from ('json', 'args', 'form')

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_request(MySchema)
        def my_endpoint(validated_data):
            # validated_data contains the validated and deserialized data
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get data from the specified location
            if location == 'json':
                data = request.get_json(silent=True) or {}
            elif location == 'args':
                data = request.args.to_dict()
            elif location == 'form':
                data = request.form.to_dict()
            else:
                logger.error(f"Invalid validation location: {location}")
                return jsonify({'error': 'Internal validation error'}), 500

            # Validate the data
            schema = schema_class()
            try:
                validated_data = schema.load(data)
                # Pass validated data as first argument to the route function
                return f(validated_data, *args, **kwargs)
            except ValidationError as err:
                logger.warning(f"Validation error: {err.messages}")
                return jsonify({
                    'error': 'Validation failed',
                    'details': err.messages
                }), 400
            except Exception as e:
                logger.error(f"Unexpected validation error: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        return decorated_function
    return decorator

def validate_query_params(schema_class):
    """
    Convenience decorator for validating query parameters
    Equivalent to validate_request(schema_class, location='args')
    """
    return validate_request(schema_class, location='args')

def validate_json(schema_class):
    """
    Convenience decorator for validating JSON body
    Equivalent to validate_request(schema_class, location='json')
    """
    return validate_request(schema_class, location='json')
