import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Create a new client and connect to the server
mongo_connection = os.getenv('MONGODB_CONNECTION')
uri = mongo_connection
mongo = MongoClient(uri)