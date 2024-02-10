from fastapi import FastAPI, status, HTTPException
from domain.events import WalletCreated
from presentation.schemas import GetWalletOutSchema
from services.commands import CreateWalletCommand
from services.queries import WalletQueryService

app = FastAPI()


@app.post('/create-wallet/{user_id}', status_code=status.HTTP_201_CREATED)
async def create_wallet(user_id: int) -> dict:

    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if existing_wallet:
        raise HTTPException(
            status_code=400,
            detail='Wallet already exists'
        )

    event = WalletCreated(user_id=user_id)
    await CreateWalletCommand().execute(event)

    return {
        'data': event.model_dump(),
        'message': "Wallet created successfully",
        'status': status.HTTP_201_CREATED
    }


@app.get('/get-wallet/{user_id}', response_model=GetWalletOutSchema, status_code=status.HTTP_200_OK)
async def get_wallet(user_id: int) -> dict:
    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if not existing_wallet:
        raise HTTPException(
            status_code=404,
            detail='Wallet does not exist.'
        )

    return existing_wallet