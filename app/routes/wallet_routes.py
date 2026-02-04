from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas import SpendRequest, TopUpRequest, BonusRequest
from app.services.ledger_service import get_wallet_balance
from app.services.wallet_service import spend_money,top_up_money,bonus_money

router=APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/{wallet_id}/balance")
async def walletBalance(wallet_id: int, db: AsyncSession=Depends(get_db)):
    balance=await get_wallet_balance(db,wallet_id)
    return {
        "wallet_id":wallet_id,
        "balance":balance
    }

@router.post("/spend")
async def spendMoney(request: SpendRequest, db: AsyncSession=Depends(get_db)):
    result=await spend_money(db, request.user_wallet_id, request.amount, request.idempotency_key)
    return result

@router.post("/top-up")
async def topUpMoney(request: TopUpRequest, db: AsyncSession=Depends(get_db)):

    result=await top_up_money(db, request.user_wallet_id, request.amount, request.idempotency_key)
    return result

@router.post("/bonus")
async def bonusMoney(request: BonusRequest, db: AsyncSession=Depends(get_db)):
    result= await bonus_money(db,request.user_wallet_id,request.amount,request.idempotency_key)
    return result 