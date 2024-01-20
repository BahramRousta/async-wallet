
class EventStoreRepository:

    def __init__(self, event_store):
        self.event_store = event_store

    async def save_event(self, event) -> None:
        await self.event_store.collection.insert_one(event)

    async def get_events(self, query=None) -> list:
        cursor = self.event_store.collection.find(query)
        events = [document async for document in cursor]
        return events


from db import mongo_event_store as es

event_store_repository = EventStoreRepository(event_store=es)