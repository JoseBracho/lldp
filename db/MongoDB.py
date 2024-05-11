import pymongo

from . import Conexion

class MongoDBManager:
    def __init__(self, database_name: str):
        self.client = Conexion.MongoDBConnection().get_client()
        self.db = self.client[database_name]

    def insert_document(self, collection_name: str, document: dict):
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def find_documents(self, collection_name: str, query={}):
        collection = self.db[collection_name]
        return collection.find(query)
    
    def find_documents_one(self, collection_name: str, query={}):
        collection = self.db[collection_name]
        return collection.find_one(query)
    
    def update_document(self, collection_name: str, query: dict, new_values: dict):
        collection = self.db[collection_name]
        result = collection.update_one(query, {"$set": new_values})
        return result.modified_count

    def delete_document(self, collection_name: str, query: dict):
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count
    
    def create_unique_index(self, collection_name: str, field_name: str):
        collection = self.db[collection_name]
        collection.create_index([(field_name, pymongo.ASCENDING)], unique=True)
    
    def close(self): 
        self.client.close_connection()
    
if __name__ == "__main__":
    manager = MongoDBManager("SDN")
