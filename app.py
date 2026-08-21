import os
import subprocess
import uvicorn
from loguru import logger

# Automatically apply database migrations and seed curriculum on startup
try:
    logger.info("Running database migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=False)
    logger.info("Seeding curriculum data...")
    subprocess.run(["python", "scripts/seed_dsa_data.py"], check=False)
    subprocess.run(["python", "scripts/create_demo_user.py"], check=False)
except Exception as e:
    logger.warning(f"Startup setup notice: {e}")

# Import FastAPI application
from src.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
