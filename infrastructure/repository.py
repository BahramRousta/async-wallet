from typing import Callable, List
from datetime import datetime
from domain.events import WalletCreated, Deposited, Withdrawn
from domain.models import Wallet
from infrastructure.data_access import mongo_instance
from pymongo.errors import PyMongoError, DuplicateKeyError


class WalletCommandRepository:
    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def apply(self, event):
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        match event.event_type:
            case "WalletCreated":

                async def transaction_logic(session):
                    await self.wallet_collection.insert_one(
                        document=event.model_dump(), session=session
                    )
                    await self.event_collection.insert_one(
                        document=event.model_dump(), session=session
                    )

            case "Deposited":

                async def transaction_logic(session):
                    await self.wallet_collection.find_one_and_update(
                        {"wallet_id": event.wallet_id},
                        {"$inc": {"balance": event.amount}},
                        session=session,
                    )
                    await self.event_collection.insert_one(
                        document=event.model_dump(), session=session
                    )

            case "Withdrawn":

                async def transaction_logic(session):
                    wallet = await self.wallet_collection.find_one(
                        {"wallet_id": event.wallet_id}, session=session
                    )

                    balance = wallet["balance"]
                    if event.amount > balance:
                        raise ValueError("Unable to withdraw")

                    await self.wallet_collection.update_one(
                        {"wallet_id": event.wallet_id},
                        {"$inc": {"balance": -event.amount}},
                        session=session,
                    )
                    await self.event_collection.insert_one(
                        event.model_dump(), session=session
                    )

        await self._run_transaction(transaction_logic)

    async def _initialize_collections(self):
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def _run_transaction(self, transaction_func: Callable):

        try:
            async with await self.db.client.start_session() as session:
                async with session.start_transaction():
                    await transaction_func(session)
        except (PyMongoError, ValueError, DuplicateKeyError) as e:
            raise e

    async def create_wallet(self, event: WalletCreated) -> None:
        await self.apply(event)

    async def deposit(self, event: Deposited) -> None:
        await self.apply(event)

    async def withdraw(self, event: Withdrawn) -> None:
        await self.apply(event)


class WalletQueryRepository:
    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def _initialize_collections(self):
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def get_wallet(
        self, user_id: int = None, wallet_id: str = None
    ) -> dict | None:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        if not wallet_id:
            wallet = await self.wallet_collection.find_one({"user_id": user_id})
        else:
            wallet = await self.wallet_collection.find_one({"wallet_id": wallet_id})
        return wallet if wallet else None

    async def get_balance(self, wallet_id: str) -> float:
        wallet = await self.get_wallet(wallet_id=wallet_id)
        if not wallet:
            raise ValueError("Could not find wallet")
        return wallet["balance"]

    async def get_transactions(self, wallet_id: str) -> List[dict]:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()
        documents = self.event_collection.find(
            {
                "$and": [
                    {"wallet_id": wallet_id},
                    {"event_type": {"$ne": "WalletCreated"}},
                ]
            },
            {"_id": 0, "wallet_id": 0},
        )

        transactions = [document async for document in documents]
        return transactions

    async def get_events(self, wallet_id: str, from_date: str, to_date: str) -> dict:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        events = self.event_collection.find(
            {
                "$and": [
                    {"wallet_id": wallet_id},
                    {"created_at": {"$gte": from_date}},
                    {"created_at": {"$lte": to_date}},
                ]
            },
            {"_id": 0},
        ).sort("created_at", 1)

        wallet_balance = 0
        transactions = []
        async for event in events:
            match event.get("event_type"):
                case "WalletCreated":
                    transactions.append(event)
                case "Deposited":
                    wallet_balance += event.get("amount", 0)
                    transactions.append(event)
                case "Withdrawn":
                    wallet_balance -= event.get("amount", 0)
                    transactions.append(event)

        return {"wallet_balance": wallet_balance, "transactions": transactions}
