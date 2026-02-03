from fastapi import FastAPI
from app.db import engine 
from app.models import Base

app=FastAPI()

@app.get("/health")
async def health():
    return{
        "status":"ok"
    }