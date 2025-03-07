from pymongo import MongoClient
from bson import ObjectId
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

# Establish MongoDB connection using the URI from environment variables
mongo_client = MongoClient(os.environ['MONGODB_URI'], tlsCAFile=certifi.where())  
userprofiles_collection = mongo_client.get_default_database()['userprofiles']
users_collection = mongo_client.get_default_database()['users']

def convert_object_ids(data):
    """Recursively converts ObjectId fields to strings in dictionaries and lists."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, list):
                data[key] = [convert_object_ids(item) for item in value]
            elif isinstance(value, dict):
                data[key] = convert_object_ids(value)
    return data

def get_user_profile(userId):
    # Check if user profile exists
    try:
        user_profile = userprofiles_collection.find_one({"user": ObjectId(userId)})
        if user_profile:
            del user_profile['_id']
            del user_profile['user']
            user_profile = convert_object_ids(user_profile) 
        return user_profile
    except Exception as e:
        raise Exception(f"Error querying user profile: {str(e)}")
    
# insert userProfile in Database
def insert_user_profile(userId, user_profile):
    try:
        user_profile['user'] = ObjectId(userId)

        # List of fields that are expected to be arrays of dictionaries
        array_fields = [
            'courses', 'education', 'experience', 'publications', 'skills', 
            'personal_projects', 'awards_and_achievements', 
            'position_of_responsibility', 'competitions', 
            'extra_curricular_activities'
        ]

        # Ensure each item in these arrays is a dictionary before adding an `_id`
        for field in array_fields:
            if field in user_profile and isinstance(user_profile[field], list):
                for i in range(len(user_profile[field])):
                    if isinstance(user_profile[field][i], dict):  # Ensure it's a dictionary
                        user_profile[field][i]['_id'] = ObjectId()

        result = userprofiles_collection.insert_one(user_profile)

        users_collection.find_one_and_update(
            {"_id": ObjectId(userId)},
            {"$set": {"isParsedResume": True}}
        )

        return str(result.inserted_id)
    except Exception as e:
        raise Exception(f"Error inserting user profile: {str(e)}")