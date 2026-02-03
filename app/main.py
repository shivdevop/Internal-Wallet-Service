from fastapi import FastAPI
from app.db import engine 
from app.models import Base
from app.routes.wallet_routes import router as wallet_router

app=FastAPI()

@app.get("/health")
async def health():
    return{
        "status":"ok"
    }

app.include_router(wallet_router)