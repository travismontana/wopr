#!/bin/bash
# WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025 Bob Bomar <bob@bomar.us>
# SPDX-License-Identifier: MIT
#
# Quick start script for WOPR API

set -e

echo "==================================="
echo "WOPR API - Quick Start"
echo "==================================="
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env - EDIT THIS FILE with your actual values!"
    echo ""
    echo "Required values:"
    echo "  - DATABASE_URL"
    echo "  - JWT_SECRET_KEY"
    echo ""
    read -p "Press enter when .env is configured..."
fi

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in a virtual environment. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check database connection
echo ""
echo "🔌 Checking database connection..."
python -c "from app.config import settings; print(f'Database: {settings.DATABASE_URL}')"

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
alembic upgrade head

# Create initial admin user (optional)
echo ""
read -p "Create initial admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@wopr.local',
            password_hash=get_password_hash('admin123'),
            role='admin'
        )
        db.add(user)
        await db.commit()
        print('✅ Admin user created: admin / admin123')
        print('⚠️  CHANGE THIS PASSWORD IMMEDIATELY!')

asyncio.run(create_admin())
"
fi

echo ""
echo "==================================="
echo "✅ Setup complete!"
echo "==================================="
echo ""
echo "To start the API:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or with docker-compose:"
echo "  docker-compose up"
echo ""
echo "API docs will be at: http://localhost:8000/docs"
echo ""
