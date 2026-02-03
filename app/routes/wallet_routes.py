from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.ledger_service import get_wallet_balance

router=APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/{wallet_id}/balance")
async def walletBalance(wallet_id: int, db: AsyncSession=Depends(get_db)):
    balance=await get_wallet_balance(db,wallet_id)
    return {
        "wallet_id":wallet_id,
        "balance":balance
    }

