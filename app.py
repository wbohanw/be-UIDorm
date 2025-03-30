from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
from bson import ObjectId
from pymongo import MongoClient

from mangodb import (
    create_user,
    read_user,
    create_regular_post,
    create_featured_post,
    read_regular_posts,
    read_featured_posts,
    read_post_by_id
)
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.environ.get("MONGODB_URI"))
db = client["my_app_db"]

users_collection = db["users_collection"]
regular_posts_collection = db["regular_posts"]
featured_posts_collection = db["featured_posts"]


# Custom JSON encoder to handle MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set the custom JSON encoder
app.json_encoder = MongoJSONEncoder

@app.route('/')
def index():
    if client:
        return jsonify({"message": "Color Dorm API"}), 200
    else:
        return jsonify({"message": "Failed to connect to MongoDB"}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_new_user():
    data = request.get_json()
    print(data)
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    try:
        user_id = create_user(data['username'], data['email'], data['password'])
        return jsonify({"message": "User created successfully", "user_id": str(user_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<identifier>', methods=['GET'])
def get_user(identifier):
    password = request.args.get('password')
    if not password:
        return jsonify({"error": "Password is required"}), 400

    try:
        user = read_user(identifier)
        if user and user.get('password') == password:
            # Convert ObjectId to string for JSON serialization
            user['_id'] = str(user['_id'])
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found or incorrect password"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Regular posts endpoints
@app.route('/api/posts/regular', methods=['POST'])
def create_new_regular_post():
    data = request.get_json()
    
    # Add color data validation
    if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
        return jsonify({"error": "Title, content, and user_id are required"}), 400
    
    try:
        # Include colors and css in post creation
        post_id = create_regular_post(
            data['title'],
            data['content'],
            data['user_id'],
            data.get('colors', []),  # Add colors
            data.get('css', '')      # Add CSS
        )
        return jsonify({"message": "Regular post created successfully", "post_id": str(post_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/regular', methods=['GET'])
def get_all_regular_posts():
    try:
        posts = read_regular_posts()
        # Serialize the posts for JSON response
        serialized_posts = []
        for post in posts:
            post['_id'] = str(post['_id'])
            post['user_id'] = str(post['user_id'])
            
            # Add author information
            user = read_user(post['user_id'])
            if user:
                post['author'] = user.get('username', 'Unknown')
            else:
                post['author'] = 'Unknown'
                
            serialized_posts.append(post)
        return jsonify(serialized_posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Featured posts endpoints
@app.route('/api/posts/featured', methods=['POST'])
def create_new_featured_post():
    data = request.get_json()
    
    # Add color data validation
    if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
        return jsonify({"error": "Title, content, and user_id are required"}), 400
    
    try:
        # Include colors and css in post creation
        post_id = create_featured_post(
            data['title'],
            data['content'],
            data['user_id'],
            data.get('colors', []),  # Add colors
            data.get('css', '')      # Add CSS
        )
        return jsonify({"message": "Featured post created successfully", "post_id": str(post_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/featured', methods=['GET'])
def get_all_featured_posts():
    try:
        posts = read_featured_posts()
        # Serialize the posts for JSON response
        serialized_posts = []
        for post in posts:
            post['_id'] = str(post['_id'])
            post['user_id'] = str(post['user_id'])
            
            # Add author information
            user = read_user(post['user_id'])
            if user:
                post['author'] = user.get('username', 'Unknown')
            else:
                post['author'] = 'Unknown'
                
            serialized_posts.append(post)
        return jsonify(serialized_posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new endpoint to get a specific post by ID
@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    try:
        post = read_post_by_id(post_id)
        if post:
            # Convert ObjectId to string for JSON serialization
            post['_id'] = str(post['_id'])
            post['user_id'] = str(post['user_id'])
            
            # Get user info to add author information
            user = read_user(post['user_id'])
            if user:
                post['author'] = user.get('username', 'Unknown')
            else:
                post['author'] = 'Unknown'
                
            return jsonify(post), 200
        else:
            return jsonify({"error": "Post not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
        # Connect to MongoDB
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)

    # Create and select a new database
    db = client["my_app_db"]

    # Define the three collections
    users_collection = db["users_collection"]
    regular_posts_collection = db["regular_posts"]
    featured_posts_collection = db["featured_posts"]
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
