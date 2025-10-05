#!/usr/bin/env python3
"""
Test script to debug Yahoo OAuth endpoint response
"""
import requests
import json

# Get a valid JWT token first
def get_auth_token():
    # Register or login to get a token
    response = requests.post(
        'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'test123'
        }
    )
    if response.status_code == 200:
        return response.json().get('data', {}).get('token')
    else:
        # Try registering
        response = requests.post(
            'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/auth/register',
            json={
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'test123'
            }
        )
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
    return None

def test_yahoo_endpoint():
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return

    print(f"Using token: {token[:20]}...")

    # Test Yahoo leagues endpoint
    response = requests.get(
        'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/yahoo/leagues',
        headers={'Authorization': f'Bearer {token}'}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body ({len(response.text)} bytes):")
    try:
        json_data = response.json()
        print(json.dumps(json_data, indent=2))
    except:
        print(response.text)

if __name__ == '__main__':
    test_yahoo_endpoint()