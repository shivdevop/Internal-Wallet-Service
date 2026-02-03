from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionLocal=sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

#dependency we can inject further into routes 
async def get_db():
    with AsyncSessionLocal() as session:
            yield session
 
