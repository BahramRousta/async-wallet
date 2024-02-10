from infrastructure.repository import WalletQueryRepository


class WalletQueryService:

    def __init__(self):
        self.repository = WalletQueryRepository()

    async def execute(self, user_id: int) -> dict | None:
        wallet = await self.repository.get_wallet(user_id=user_id)
        if wallet is None:
            return None
        return {
            'wallet_id': wallet.get('wallet_id', ''),
            'user_id': wallet.get('user_id', ''),
            'balance': wallet.get('balance', ''),
        }