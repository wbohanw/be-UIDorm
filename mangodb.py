from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from bson.objectid import ObjectId

load_dotenv()
uri = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(uri)

# Create and select a new database
db = client["my_app_db"]

# Define the three collections
users_collection = db["users_collection"]
regular_posts_collection = db["regular_posts"]
featured_posts_collection = db["featured_posts"]

# Function to create a user
def create_user(username, email, password):
    """
    Creates a new user in the 'users' collection.
    Returns the ID of the inserted user.
    """
    user = {"username": username, "email": email, "password": password}
    result = users_collection.insert_one(user)
    return result.inserted_id

# Function to read a user by username or ID
def read_user(identifier):
    """
    Retrieves a user from the 'users_collection' by username, email, or ID.
    Returns the user document or None if not found.
    """
    # First check if this might be an ObjectId
    if isinstance(identifier, str) and len(identifier) == 24:
        try:
            # Try to convert string ID to ObjectId
            obj_id = ObjectId(identifier)
            user = users_collection.find_one({"_id": obj_id})
            if user:
                return user
        except:
            pass  # Not a valid ObjectId, continue with other lookups
    
    # Try username lookup
    user = users_collection.find_one({"username": identifier})
    
    # If not found, try email lookup
    if not user:
        user = users_collection.find_one({"email": identifier})
        
    return user

# Function to create a regular post
def create_regular_post(title, content, user_id, colors, css):
    """
    Creates a new regular post in the 'regular_posts' collection.
    Returns the ID of the inserted post.
    """
    new_post = {
        "title": title,
        "content": content,
        "user_id": ObjectId(user_id),
        "colors": colors,
        "css": css,
        "timestamp": datetime.datetime.utcnow()
    }
    return regular_posts_collection.insert_one(new_post).inserted_id

# Function to create a featured post
def create_featured_post(title, content, user_id, colors, css):
    """
    Creates a new featured post in the 'featured_posts' collection.
    Returns the ID of the inserted post.
    """
    new_post = {
        "title": title,
        "content": content,
        "user_id": ObjectId(user_id),
        "colors": colors,
        "css": css,
        "is_featured": True,
        "timestamp": datetime.datetime.utcnow()
    }
    return featured_posts_collection.insert_one(new_post).inserted_id

# Function to read all regular posts
def read_regular_posts():
    """
    Retrieves all posts from the 'regular_posts' collection.
    Returns a list of post documents.
    """
    posts = list(regular_posts_collection.find())
    return posts

# Function to read all featured posts
def read_featured_posts():
    """
    Retrieves all posts from the 'featured_posts' collection.
    Returns a list of post documents.
    """
    posts = list(featured_posts_collection.find())
    return posts

# Function to read a post by ID from either regular or featured collections
def read_post_by_id(post_id):
    """
    Retrieves a post from either 'regular_posts' or 'featured_posts' collection by ID.
    Returns the post document or None if not found.
    """
    try:
        # Try to convert string ID to ObjectId
        obj_id = ObjectId(post_id)
        
        # First check in regular posts
        post = regular_posts_collection.find_one({"_id": obj_id})
        
        # If not found, check in featured posts
        if post is None:
            post = featured_posts_collection.find_one({"_id": obj_id})
            
        return post
    except:
        return None

# Demonstration of the operations
if __name__ == "__main__":

    # Load environment variables
    load_dotenv()
    uri = os.getenv("MONGODB_URI")

    # Connect to MongoDB
    client = MongoClient(uri)

    # Create and select a new database
    db = client["my_app_db"]

    # Define the three collections
    users_collection = db["users_collection"]
    regular_posts_collection = db["regular_posts"]
    featured_posts_collection = db["featured_posts"]

    # Create a user
    user_id = create_user("john_doe", "john@example.com", "securepassword123")
    print(f"Created user with id: {user_id}")

    # Read the user
    user = read_user("john_doe")
    print("Read user:")
    for key, value in user.items():
        print(f"{key}: {value}")
    print("----------")

    # Create a regular post
    post_id = create_regular_post("My first post", "Hello world!", user_id, [], "")
    print(f"Created regular post with id: {post_id}")

    # Create a featured post
    featured_post_id = create_featured_post("Featured post", "This is featured!", user_id, [], "")
    print(f"Created featured post with id: {featured_post_id}")

    # Read regular posts
    regular_posts = read_regular_posts()
    print("Regular posts:")
    for post in regular_posts:
        print("📄 Post:")
        for key, value in post.items():
            print(f"{key}: {value}")
        print("----------")

    # Read featured posts
    featured_posts = read_featured_posts()
    print("Featured posts:")
    for post in featured_posts:
        print("📄 Post:")
        for key, value in post.items():
            print(f"{key}: {value}")
        print("----------")

    # Close the MongoDB client
    client.close()