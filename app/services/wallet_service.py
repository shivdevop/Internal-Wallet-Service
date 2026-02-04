import uuid 
from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, LedgerEntry, Wallet
from app.services.ledger_service import get_wallet_balance


#we will implement a function to spend money from a wallet and transfer amount to treasury wallet 
# first we will do idempotency check to prevent duplicate transactions
#if transaction is not found, we will create a new transaction and ledger entries (idempotency check is done on idempotency key)
#we will implement acid transaction with row locking and deadlock avoidance 

TREASURY_WALLET_ID=3 #from seed data(treasury wallet)
async def spend_money(
    db: AsyncSession,
    user_wallet_id: int,
    amount: int,
    idempotency_key: str):

    #idempotency check
    existing_transaction=await db.execute(
        select(Transaction).where(Transaction.idempotency_key==idempotency_key)
    )
    ext_txn=existing_transaction.scalar_one_or_none()

    if ext_txn and ext_txn.status=="COMPLETED":
        return{
            "status":"ALREADY_PROCESSED",
            "message":"Transaction already processed"
        }

    new_txn_id=uuid.uuid4()

    #create new transaction row with status as pending 
    new_txn=Transaction(
        id=new_txn_id,
        idempotency_key=idempotency_key,
        status="PENDING"
       )

    db.add(new_txn)
  
     #lock wallets in sorted order to avoid deadlocks
    wallet_ids=sorted([user_wallet_id, TREASURY_WALLET_ID])

    wallets=await db.execute(
            select(Wallet).where(Wallet.id.in_(wallet_ids)).with_for_update()
        )

    #check balance whether we have enough money in the wallet for spending 
    balance_user_wallet=await get_wallet_balance(db, user_wallet_id)
    if balance_user_wallet<amount:
        raise Exception("Insufficient balance")

    #create ledger entries for spending and treasury (double entry bookkeeping)
    db.add_all(
            [
                LedgerEntry(
                    transaction_id=new_txn_id,
                    wallet_id=user_wallet_id,
                    amount=-amount
                ),
                LedgerEntry(
                    transaction_id=new_txn_id,
                    wallet_id=TREASURY_WALLET_ID,
                    amount=amount
                )
            ]
        )
 
    #mark transaction as completed
    new_txn.status="COMPLETED"

    await db.commit()
    
    return{
        "status":"COMPLETED",
        "message":"Money spent successfully",
        "transaction_id":new_txn_id
    }
