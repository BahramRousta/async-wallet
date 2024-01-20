import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


mongo_uri = "mongodb://localhost:27017"


class EventStore:

    def __init__(self, db_uri: str, db_name: str, collection_name: str) -> None:
        self.client = AsyncIOMotorClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def save_event(self, event) -> None:
        await self.collection.insert_one(event)


mongo_event_store = EventStore(db_uri=mongo_uri, db_name='async-wallets', collection_name='wallets')
