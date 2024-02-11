from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from domain.exceptions import MongoConnectionError


class MongoManager:

    def __init__(self, max_pool_size=100):
        self.mongo_url = 'mongodb://localhost:27017'
        self.max_pool_size = max_pool_size

        try:
            self.client = AsyncIOMotorClient(self.mongo_url, maxPoolSize=self.max_pool_size)
            self.database = self.client.get_database('Wallet')
        except ConnectionFailure as e:
            raise MongoConnectionError(f"Failed to connect to MongoDB: {e}")

        self.database = self.client['Wallet']

    @property
    def event_collection(self):
        return self.database['WalletEvents']

    @property
    def wallet_collection(self):
        return self.database['WalletBalance']


mongo_instance = MongoManager()
