from pymongo import MongoClient
from bson import ObjectId
import os

# Establish MongoDB connection using the URI from environment variables
mongo_client = MongoClient(os.environ['MONGODB_URI'])  
userprofiles_collection = mongo_client.get_default_database()['userprofiles']  # Get the default database and collection

def get_user_profile(userId):
    # Log the userId
    print("Received userId:", userId)

    # Check if user profile exists
    try:
        user_profile = userprofiles_collection.find_one({"user": ObjectId(userId)})  # Use ObjectId for the query
        # Log the user_profile
        print("Retrieved user_profile:", user_profile)
        return user_profile
    except Exception as e:
        raise Exception(f"Error querying user profile: {str(e)}")