# Docker Setup Guide

The DSA AI Coach uses Docker Compose to orchestrate its backend services (FastAPI, PostgreSQL, Redis). The frontend runs natively via Vite for rapid UI development.

## Prerequisites

1. Docker & Docker Compose installed.
2. Node.js (v18+) & npm installed.
3. Python 3.12+ (optional, for running local scripts).

## 1. Environment Configuration

Copy the example environment file:
`ash
cp .env.example .env
`
Ensure your NVIDIA_NIM_API_KEY and JWT_SECRET are set inside .env.

## 2. Start the Backend Stack

Run the following to build and launch the databases and FastAPI:
`ash
docker-compose up -d --build
`

**What this does:**
*   Boots dsa_postgres (Port 5433)
*   Boots dsa_redis (Port 6380)
*   Boots dsa_backend (Port 8000)
*   *Automatically runs Alembic migrations (lembic upgrade head)* to initialize the schema!

## 3. Seed the Database

Once the backend is healthy, seed the curriculum and create a demo user by running the scripts *inside* the container:

`ash
# 1. Seed Curriculum (25 Executable Problems)
docker exec dsa_backend python scripts/seed_dsa_data.py

# 2. Create Demo User (demo@kalvium.com / DemoPassword123!)
docker exec dsa_backend python scripts/create_demo_user.py
`

## 4. Run the Frontend

In a new terminal:
`ash
cd frontend
npm install
npm run dev
`

Visit http://localhost:5173 and log in with the demo account!
