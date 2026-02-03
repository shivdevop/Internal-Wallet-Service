from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func 
from app.models import LedgerEntry

async def get_wallet_balance(db: AsyncSession, wallet_id: int)-> int:
    result=await db.execute(
        select(func.coalesce(func.sum(LedgerEntry.amount),0)).where(LedgerEntry.wallet_id==wallet_id)
    )

    balance=result.scalar_one()
    return balance 

    