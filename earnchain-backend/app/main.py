# app/main.py
from flask import Flask, request, jsonify
# Import CORS to handle requests from the frontend static site
from flask_cors import CORS
import os
# Import your database and model logic
# Make sure these imports match the structure and content of your existing files
from app.database import init_db, get_db
from app.models import User, Ad, Click

# Create the Flask app instance
app = Flask(__name__)

# --- Enable CORS ---
# This is CRITICAL to allow your frontend (static site) to call this backend API
# if they are hosted on different URLs (which they will be).
# For simplicity and during development, allow all origins (*).
# For production, you should restrict this to your frontend's specific URL.
# Example for production: CORS(app, origins=["https://your-frontend-url.onrender.com"])
CORS(app) # This line enables CORS for all routes

# Get the Admin User ID from environment variables for security
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '7746836233') # Default if not set

# --- Initialize the database ---
# This should create tables if they don't exist when the app starts.
# Ensure your database.py handles pathing correctly for Render (e.g., /tmp/earnchain.db)
init_db()

# --- API Routes ---
# These routes provide the data and logic for your frontend to interact with.
# They are the core of your application's functionality.

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user or ensure an existing user is recognized."""
    data = request.get_json()
    user_id = data.get('userId')

    if not user_id:
        return jsonify({'error': 'userId required'}), 400

    try:
        User.register(user_id)
        return jsonify({'message': 'User registered'}), 200
    except Exception as e:
        # It's good practice to log the actual error 'e' for debugging
        print(f"Error registering user {user_id}: {e}")
        return jsonify({'error': 'Internal server error during registration'}), 500

@app.route('/ads')
def get_ads():
    """Get a list of ads available for the user to click."""
    user_id = request.args.get('userId')

    if not user_id:
        return jsonify({'error': 'userId required'}), 400

    try:
        ads = Ad.get_available_ads(user_id)
        return jsonify(ads), 200
    except Exception as e:
        print(f"Error fetching ads for user {user_id}: {e}")
        return jsonify({'error': 'Failed to fetch ads'}), 500

@app.route('/click', methods=['POST'])
def click_ad():
    """Record a user clicking an ad and update their balance."""
    data = request.get_json()
    user_id = data.get('userId')
    ad_id = data.get('adId')

    if not user_id or not ad_id:
        return jsonify({'error': 'userId and adId required'}), 400

    try:
        # Get ad details
        ad = Ad.get_ad(ad_id)
        if not ad:
            return jsonify({'error': 'Ad not found'}), 404

        # Record click
        success = Click.record_click(user_id, ad_id, ad['reward'])

        if success:
            return jsonify({
                'message': 'Ad clicked successfully',
                'points': ad['reward']
            }), 200
        else:
            # This covers the case where the click was not recorded due to cooldown
            return jsonify({'error': 'Ad already clicked within 24 hours'}), 400
    except Exception as e:
        print(f"Error processing click for user {user_id} on ad {ad_id}: {e}")
        return jsonify({'error': 'Failed to process click'}), 500

@app.route('/user/<int:user_id>') # Capture user_id from the URL path
def get_user_balance(user_id):
    """Get the current balance for a specific user."""
    try:
        balance = User.get_balance(user_id)
        # Ensure balance is a number before sending
        return jsonify({'balance': float(balance)}), 200
    except Exception as e:
        print(f"Error fetching balance for user {user_id}: {e}")
        # If user not found, get_balance might return None or raise, handle accordingly
        # Let's assume get_balance returns 0 for not found or handles it.
        # If it raises, the except block catches it.
        return jsonify({'error': 'Failed to fetch user balance'}), 500

@app.route('/history/<int:user_id>') # Capture user_id from the URL path
def get_history(user_id):
    """Get the recent click history for a specific user."""
    try:
        history = Click.get_history(user_id)
        return jsonify(history), 200
    except Exception as e:
        print(f"Error fetching history for user {user_id}: {e}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@app.route('/admin/ad', methods=['POST'])
def add_ad():
    """(Admin only) Add a new ad to the system."""
    # --- Authentication Check ---
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'No authorization header'}), 401

    # Expecting "Bearer <USER_ID>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({'error': 'Invalid authorization header format'}), 401

    token = parts[1]
    if token != ADMIN_USER_ID:
        return jsonify({'error': 'Forbidden'}), 403
    # --- End Authentication ---

    # --- Data Validation ---
    data = request.get_json()
    title = data.get('title')
    url = data.get('url')
    reward = data.get('reward')

    if not title or not url or reward is None: # Checks for None or missing key
        return jsonify({'error': 'title, url, and reward required'}), 400
    # --- End Validation ---

    try:
        # Add the new ad to the database
        with get_db() as conn: # Use context manager for connection
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO ads (title, url, reward) VALUES (?, ?, ?)',
                (title, url, float(reward)) # Ensure reward is a number
            )
            conn.commit()
            ad_id = cursor.lastrowid

        return jsonify({'message': 'Ad created successfully', 'id': ad_id}), 201
    except Exception as e:
        print(f"Error adding ad: {e}")
        return jsonify({'error': 'Failed to create ad'}), 500

# --- Entry Point ---
# This part runs when the script is executed directly (e.g., by `python app/main.py`)
if __name__ == '__main__':
    # Get the port from environment variable (Render sets this) or default to 3000
    port = int(os.environ.get('PORT', 3000))
    # IMPORTANT for Render: Bind to '0.0.0.0' so it's accessible outside the container
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug=False for production