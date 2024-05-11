import os
from pymongo import MongoClient
from urllib.parse import quote_plus

class MongoDBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        cls.user = quote_plus(os.getenv('USER_DB'))
        cls.password = quote_plus(os.getenv('PASSWORD_DB'))
        cls.ip = quote_plus(os.getenv('IP_DB'))
        cls.port = quote_plus(os.getenv('PORT_DB'))
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = cls._instance.connect()
        return cls._instance

    @staticmethod
    def connect():
        try:
            client = MongoClient(f'mongodb://{MongoDBConnection.user}:{MongoDBConnection.password}@{MongoDBConnection.ip}:{MongoDBConnection.port}/')
            return client
        except Exception as e:
            print("Error al conectarse a MongoDB:", e)

    def get_client(self):
        return self.client
    
    def close_connection(self):
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            print("Error al cerrar la conexión a MongoDB:", e)

if __name__ == "__main__":
    connection = MongoDBConnection()
    client = connection.get_client()
    try:
        db = client["SDN"]
        collection = db["Nodo"]
        cursor = collection.find()
        for document in cursor:
            print('name: ', document['name'], 'nickname: ', document['nickname'] )

    finally:
        connection.close_connection()
