from typing import Callable, List
from domain.events import WalletCreated, Deposited, Withdrawn, Event
from infrastructure.data_access import mongo_instance
from pymongo.errors import PyMongoError, DuplicateKeyError


class WalletCommandRepository:
    """
    Repository for handling wallet-related commands,
    such as creating wallets, depositing, and withdrawing funds.
    """

    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def apply(self, event: Event) -> None:
        """
        Apply the given event to update the wallet and event collections.

        Args:
            event: The event to apply.

        Raises:
            PyMongoError: If there is an error during MongoDB operations.
            ValueError: If there is an invalid operation, e.g., withdrawing more than the available balance.
            DuplicateKeyError: If there is a duplicate key error during MongoDB operations.
        """

        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        async def transaction_logic(session):
            """
            Execute the transaction logic within a MongoDB session.

            Args:
                session: The MongoDB session to execute the transaction in.
            """

            match event.event_type:
                case "WalletCreated":
                    await self.wallet_collection.insert_one(
                        document=event.model_dump(), session=session
                    )
                    await self.event_collection.insert_one(
                        document=event.model_dump(), session=session
                    )

                case "Deposited":
                    await self.wallet_collection.find_one_and_update(
                        {"wallet_id": event.wallet_id},
                        {"$inc": {"balance": event.amount}},
                        session=session,
                    )
                    await self.event_collection.insert_one(
                        document=event.model_dump(), session=session
                    )

                case "Withdrawn":
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
                        document=event.model_dump(), session=session
                    )

        await self._run_transaction(transaction_logic)

    async def _initialize_collections(self):
        """
        Initialize the wallet and event collections.
        """
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def _run_transaction(self, transaction_func: Callable):
        """
        Execute a MongoDB transaction with the provided transaction logic.

        Args:
            transaction_func: The transaction logic function to execute within the transaction.

        Raises:
            PyMongoError: If there is an error during MongoDB operations.
            ValueError: If there is an invalid operation within the transaction logic.
            DuplicateKeyError: If there is a duplicate key error during MongoDB operations.
        """

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
    """
    Repository for querying wallet-related information.
    """

    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def _initialize_collections(self):
        """
        Initialize the wallet and event collections.
        """
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def get_wallet(
        self, user_id: int = None, wallet_id: str = None
    ) -> dict | None:
        """
        Retrieve wallet information by user ID or wallet ID.

        Args:
           user_id (int, optional): The ID of the user associated with the wallet.
           wallet_id (str, optional): The ID of the wallet.

        Returns:
           dict | None: The wallet information if found, otherwise None.
        """
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        if not wallet_id:
            wallet = await self.wallet_collection.find_one({"user_id": user_id})
        else:
            wallet = await self.wallet_collection.find_one({"wallet_id": wallet_id})
        return wallet if wallet else None

    async def get_balance(self, wallet_id: str) -> float:
        """
        Retrieve the balance of a wallet.

        Args:
            wallet_id (str): The ID of the wallet.

        Returns:
            float: The balance of the wallet.

        Raises:
            ValueError: If the wallet cannot be found.
        """
        wallet = await self.get_wallet(wallet_id=wallet_id)
        if not wallet:
            raise ValueError("Could not find wallet")
        return wallet["balance"]

    async def get_transactions(self, wallet_id: str) -> List[dict]:
        """
        Retrieve transactions for a wallet, excluding "WalletCreated" events.

        Args:
            wallet_id (str): The ID of the wallet.

        Returns:
            List[dict]: List of transactions for the wallet.
        """
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
        """
        Retrieve events for a wallet within the specified date range.

        Args:
            wallet_id (str): The ID of the wallet.
            from_date (str): Start date of the date range (format: YYYY-MM-DD).
            to_date (str): End date of the date range (format: YYYY-MM-DD).

        Returns:
            dict: Dictionary containing wallet balance and transactions within the specified date range.
        """

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
