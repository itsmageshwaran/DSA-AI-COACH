import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database.session import AsyncSessionFactory
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.schemas import RegisterRequest
from src.modules.auth.service import register_user, authenticate_user

async def create_demo():
    async with AsyncSessionFactory() as session:
        uow = UnitOfWork(session)
        try:
            # Check if user already exists
            user = await authenticate_user(uow, "demo@kalvium.com", "DemoPassword123!")
            print("Demo user already exists.")
            return
        except Exception:
            pass

        try:
            payload = RegisterRequest(
                email="demo@kalvium.com",
                password="DemoPassword123!",
                full_name="Demo User"
            )
            user = await register_user(uow, payload)
            print("Successfully created demo user!")
        except Exception as e:
            print(f"Failed to create using service: {e}")

if __name__ == "__main__":
    asyncio.run(create_demo())
