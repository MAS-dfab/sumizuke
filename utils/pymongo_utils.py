from pymongo import MongoClient
import datetime

def insert_data(collection, data):
    # Insert data into the collection
    data["timestamp"] = datetime.datetime.now()
    collection.insert_one(data)
    print("Data inserted")

def fetch_data(collection, query):
    # Fetch data from the collection
    data = collection.find()
    for d in data:
        print(d)

def delete_data(collection):
    # Delete all data from the collection
    collection.delete_many({})
    print("Data deleted")

def check_collection_size(collection):
    # Check the size of the collection
    size = collection.count_documents({})
    print(f"Collection size: {size}")

