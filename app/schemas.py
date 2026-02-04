from pydantic import BaseModel

class SpendRequest(BaseModel):
    user_wallet_id: int
    amount: int
    idempotency_key: str

    