#!/bin/bash

# Fantasy Grid API v2 Launch Script
# This script helps you launch the application with API v2

set -e  # Exit on error

echo "=================================================="
echo "   Fantasy Grid - API v2 Launch Helper"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env 2>/dev/null || echo "No .env.example found"
fi

# Check if API_VERSION is set
if grep -q "API_VERSION=v2" .env; then
    echo -e "${GREEN}✅ API_VERSION=v2 configured${NC}"
else
    echo -e "${YELLOW}⚠️  API_VERSION not set to v2${NC}"
    echo "API v1 will be used by default"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed${NC}"
    echo "Installing requirements..."
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Check database
if grep -q "DATABASE_URL" .env; then
    echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
else
    echo -e "${YELLOW}⚠️  DATABASE_URL not configured${NC}"
    echo "App will run in API-only mode (no local caching)"
    echo "See DATABASE_SETUP.md for database setup instructions"
fi

echo ""
echo "=================================================="
echo "   Starting Backend Server"
echo "=================================================="
echo ""
echo "Backend will be available at: http://localhost:5000"
echo "Health check: http://localhost:5000/health"
echo "Advanced stats endpoints: http://localhost:5000/api/advanced/*"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=================================================="
echo ""

# Start the server
python wsgi.py
