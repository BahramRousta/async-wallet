from fastapi import FastAPI, status
from domain.events import WalletCreated
from services.commands import CreateWalletCommand
from services.queries import WalletQueryService

app = FastAPI()


@app.post('/create-wallet/{user_id}', status_code=status.HTTP_201_CREATED)
async def create_wallet(user_id: int) -> dict:
    event = WalletCreated(user_id=user_id)
    await CreateWalletCommand().execute(event)
    wallet = await WalletQueryService().execute(user_id=user_id)
    return {
        'data': wallet,
        'message': "Wallet created successfully",
        'status': 200
    }
