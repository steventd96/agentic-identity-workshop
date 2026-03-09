"""
AskHR Demo App Backend API
Handles OAuth authentication flow with IBM Verify
"""

from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import requests
import os
import secrets
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Enable CORS for frontend
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'http://localhost:7860'
])

# IBM Verify Configuration - Frontend Client
IBM_VERIFY_TENANT = os.getenv('IBM_VERIFY_TENANT')
IBM_VERIFY_CLIENT_ID = os.getenv('IBM_VERIFY_FRONTEND_CLIENT_ID')
IBM_VERIFY_CLIENT_SECRET = os.getenv('IBM_VERIFY_FRONTEND_CLIENT_SECRET')
IBM_VERIFY_OIDC_URL = os.getenv(
    'IBM_VERIFY_OIDC_URL',
    f'https://{IBM_VERIFY_TENANT}.verify.ibm.com/oidc/endpoint/default'
)
REDIRECT_URI = os.getenv('IBM_VERIFY_REDIRECT_URI', 'http://localhost:3000/callback')

# Validate configuration
if not all([IBM_VERIFY_TENANT, IBM_VERIFY_CLIENT_ID, IBM_VERIFY_CLIENT_SECRET]):
    logger.error("Missing required IBM Verify configuration")
    raise ValueError("Missing required IBM Verify environment variables: IBM_VERIFY_FRONTEND_CLIENT_ID, IBM_VERIFY_FRONTEND_CLIENT_SECRET")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'askhr-backend',
        'version': '1.0.0'
    })


@app.route('/api/auth/login', methods=['GET'])
def login():
    """
    Initiate OAuth login flow with IBM Verify
    Redirects user to IBM Verify authorization endpoint
    """
    try:
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Build authorization URL
        auth_params = {
            'client_id': IBM_VERIFY_CLIENT_ID,
            'response_type': 'code',
            'scope': 'openid profile email groups',
            'redirect_uri': REDIRECT_URI,
            'state': state
        }
        
        auth_url = f"{IBM_VERIFY_OIDC_URL}/authorize?{urlencode(auth_params)}"
        
        logger.info(f"Redirecting to IBM Verify for authentication")
        return jsonify({
            'auth_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Error initiating login: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/callback', methods=['POST'])
def callback():
    """
    Handle OAuth callback from IBM Verify
    Exchange authorization code for tokens
    """
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')
        
        if not code:
            return jsonify({'error': 'Missing authorization code'}), 400
        
        # Verify state parameter (CSRF protection)
        stored_state = session.get('oauth_state')
        if not stored_state or stored_state != state:
            logger.warning("State mismatch - possible CSRF attack")
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Exchange authorization code for tokens
        token_endpoint = f"{IBM_VERIFY_OIDC_URL}/token"
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': IBM_VERIFY_CLIENT_ID,
            'client_secret': IBM_VERIFY_CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI
        }
        
        logger.info("Exchanging authorization code for tokens")
        token_response = requests.post(
            token_endpoint,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return jsonify({
                'error': 'Token exchange failed',
                'details': token_response.text
            }), 400
        
        tokens = token_response.json()
        
        # Get user info
        userinfo_endpoint = f"{IBM_VERIFY_OIDC_URL}/userinfo"
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={'Authorization': f"Bearer {tokens['access_token']}"},
            timeout=30
        )
        
        if userinfo_response.status_code == 200:
            user_info = userinfo_response.json()
        else:
            user_info = {}
        
        # Store tokens in session
        session['access_token'] = tokens.get('access_token')
        session['id_token'] = tokens.get('id_token')
        session['refresh_token'] = tokens.get('refresh_token')
        session['user_info'] = user_info
        
        logger.info(f"User authenticated: {user_info.get('email', 'unknown')}")
        
        # Return both id_token and access_token for delegation semantics
        # id_token = subject token (user identity)
        # access_token = actor token (for delegation)
        return jsonify({
            'success': True,
            'access_token': tokens.get('access_token'),  # Real access token for actor
            'id_token': tokens.get('id_token'),  # ID token for subject
            'token_type': tokens.get('token_type', 'Bearer'),
            'expires_in': tokens.get('expires_in', 3600),
            'user': user_info
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during callback: {e}")
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/user', methods=['GET'])
def get_user():
    """Get current authenticated user information"""
    try:
        user_info = session.get('user_info')
        access_token = session.get('access_token')
        id_token = session.get('id_token')
        
        if not user_info or not access_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        return jsonify({
            'authenticated': True,
            'user': user_info,
            'has_token': bool(access_token),
            'access_token': access_token,
            'id_token': id_token
        })
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        session.clear()
        logger.info("User logged out")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        refresh_token = session.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'No refresh token available'}), 401
        
        token_endpoint = f"{IBM_VERIFY_OIDC_URL}/token"
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': IBM_VERIFY_CLIENT_ID,
            'client_secret': IBM_VERIFY_CLIENT_SECRET
        }
        
        logger.info("Refreshing access token")
        token_response = requests.post(
            token_endpoint,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token refresh failed: {token_response.text}")
            return jsonify({'error': 'Token refresh failed'}), 400
        
        tokens = token_response.json()
        
        # Update session with new tokens
        session['access_token'] = tokens.get('access_token')
        if tokens.get('refresh_token'):
            session['refresh_token'] = tokens.get('refresh_token')
        
        logger.info("Access token refreshed successfully")
        
        return jsonify({
            'success': True,
            'access_token': tokens.get('access_token'),
            'token_type': tokens.get('token_type', 'Bearer'),
            'expires_in': tokens.get('expires_in', 3600)
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during token refresh: {e}")
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AskHR Backend API on port {port}")
    logger.info(f"IBM Verify Tenant: {IBM_VERIFY_TENANT}")
    logger.info(f"Redirect URI: {REDIRECT_URI}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

# Made with Bob