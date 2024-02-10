from services.queries import WalletQueryService


class WalletProjection:

    def get_wallet_current_balance(self, wallet_id):
        WalletQueryService