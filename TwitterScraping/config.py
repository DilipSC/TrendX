from pymongo import MongoClient
from utils import MONGO_URI

def get_mongo_client():
    return MongoClient(MONGO_URI)


