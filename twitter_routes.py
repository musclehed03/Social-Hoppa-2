import os
import base64
import hashlib
import secrets
import requests
from flask import Blueprint, redirect, request, session, url_for, jsonify
from urllib.parse import urlencode
from datetime import datetime, timedelta
from extensions import db
from models import SocialConnection, User

twitter_bp = Blueprint('twitter', __name__)

# Twitter OAuth 2.0 Endpoints
AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
USER_INFO_URL = "https://api.twitter.com/2/users/me"

# Scopes for Twitter v2 API
# 'offline.access' is required for refresh tokens
SCOPES = "tweet.read tweet.write users.read offline.access"

def generate_pkce_pair():
    """Generates a code verifier and its corresponding code challenge for PKCE."""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('ascii')).digest()
    ).decode('ascii').replace('=', '')
    return code_verifier, code_challenge

@twitter_bp.route('/auth/twitter/login')
def initiate_twitter_auth():
    """Initiates the Twitter OAuth 2.0 Authorization Code Flow with PKCE."""
    client_id = os.environ.get('TWITTER_CLIENT_ID')
    redirect_uri = os.environ.get('TWITTER_REDIRECT_URI')
    
    if not client_id or not redirect_uri:
        return jsonify({"error": "Twitter credentials not configured in environment variables."}), 500

    # Generate PKCE and state for security
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)

    # Store in session for the callback route
    session['twitter_oauth_state'] = state
    session['twitter_oauth_code_verifier'] = code_verifier

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': SCOPES,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    auth_redirect_url = f"{AUTH_URL}?{urlencode(params)}"
    return redirect(auth_redirect_url)

@twitter_bp.route('/auth/twitter/callback')
def twitter_callback():
    """Handles the Twitter OAuth 2.0 callback, exchanges code for tokens, and stores them."""
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return jsonify({"error": f"Twitter OAuth error: {error}"}), 400

    # Verify state to prevent CSRF
    if state != session.get('twitter_oauth_state'):
        return jsonify({"error": "Invalid OAuth state."}), 400

    code_verifier = session.get('twitter_oauth_code_verifier')
    client_id = os.environ.get('TWITTER_CLIENT_ID')
    client_secret = os.environ.get('TWITTER_CLIENT_SECRET')
    redirect_uri = os.environ.get('TWITTER_REDIRECT_URI')

    # Exchange authorization code for access token
    token_data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier
    }

    # Twitter requires Basic Auth for the token endpoint if a client secret is used
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
    headers = {
        'Authorization': f"Basic {auth_header}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    
    if not response.ok:
        return jsonify({"error": "Failed to exchange code for token", "details": response.text}), 400

    tokens = response.json()
    
    # Get user info from Twitter to identify the account
    user_headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    user_response = requests.get(USER_INFO_URL, headers=user_headers)
    
    if not user_response.ok:
        return jsonify({"error": "Failed to fetch user info", "details": user_response.text}), 400
    
    twitter_user = user_response.json().get('data', {})
    twitter_id = twitter_user.get('id')

    # Store tokens in the database
    # Assuming the current user is logged in and stored in session['user_id']
    # If not logged in, we'll use a dummy user for demonstration
    user_id = session.get('user_id')
    if not user_id:
        user = User.query.first()
        if not user:
            # Fallback for demonstration: create a user if none exists
            user = User(email='demo@example.com', password_hash='dummy')
            db.session.add(user)
            db.session.commit()
        user_id = user.id

    # Check if a connection already exists for this user and platform
    connection = SocialConnection.query.filter_by(user_id=user_id, platform_name='twitter').first()
    
    if not connection:
        connection = SocialConnection(user_id=user_id, platform_name='twitter')
        db.session.add(connection)

    connection.platform_user_id = twitter_id
    connection.access_token = tokens['access_token']
    connection.refresh_token = tokens.get('refresh_token')
    connection.scopes = tokens.get('scope')
    
    # Calculate expiration time
    expires_in = tokens.get('expires_in', 7200)
    connection.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    db.session.commit()

    # Clear OAuth session data
    session.pop('twitter_oauth_state', None)
    session.pop('twitter_oauth_code_verifier', None)

    return jsonify({
        "message": "Twitter account connected successfully!",
        "twitter_id": twitter_id,
        "platform": "twitter"
    })
