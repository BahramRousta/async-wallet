from infrastructure.repository import WalletQueryRepository


class WalletQueryService:

    def __init__(self):
        self.repository = WalletQueryRepository()

    async def execute(self, user_id: int) -> dict:
        wallet = await self.repository.get_wallet(user_id=user_id)
        return {
            'wallet_id': wallet['wallet_id'],
            'user_id': wallet['user_id'],
            'balance': wallet['balance'],
        }