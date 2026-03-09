from pymongo import MongoClient

from app.config import COLLECTION_NAME, DATABASE_NAME, MONGO_URI


if not MONGO_URI:
    raise ValueError("MONGO_URI is not configured")

if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME is not configured")

if not COLLECTION_NAME:
    raise ValueError("COLLECTION_NAME is not configured")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
wafer_collection = db[COLLECTION_NAME]