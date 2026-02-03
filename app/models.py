from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base 
from sqlalchemy.sql import func 


Base=declarative_base()

class User(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)

class AssetType(Base):
    __tablename__ = "asset_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


#a user can have multiple wallets 
#every wallet is a container for one currency(AssetType) for one user 
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_type_id = Column(Integer, ForeignKey("asset_types.id"))
    wallet_type = Column(String, nullable=False)


#idempotency key is a unique identifier for a transaction
#it is used to prevent duplicate transactions
#this table keeps a track whether or not this exact request has already been processed
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    idempotency_key = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


#ledger entries table track the exact movement of money
#it is a double entry bookkeeping system
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    amount = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())