from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:

    def __init__(self):
        self.mongo_url = 'mongodb://localhost:27017'
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.database = self.client['Wallet']

    @property
    def event_collection(self):
        return self.database['WalletEvents']

    @property
    def wallet_collection(self):
        return self.database['WalletBalance']


mongo_instance = MongoManager()
