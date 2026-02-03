#!/bin/bash
# ============================================================================
# AegisAI Setup Script
# Automates the complete installation process
# ============================================================================

set -e  # Exit on error

echo "🛡️  AegisAI Setup Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo "🔍 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"

echo ""
echo "📦 Setting up Backend..."
echo "========================"

# Backend setup
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

echo -e "${GREEN}✅ Backend setup complete${NC}"

echo ""
echo "📦 Setting up Frontend..."
echo "========================"

# Frontend setup
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo -e "${GREEN}✅ Frontend setup complete${NC}"

echo ""
echo "⚙️  Configuration..."
echo "==================="

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${BLUE}📝 Please edit .env and add your GEMINI_API_KEY${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create frontend .env.local if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo "Creating frontend/.env.local..."
    echo "VITE_GEMINI_API_KEY=your_key_here" > frontend/.env.local
    echo -e "${BLUE}📝 Please edit frontend/.env.local and add your GEMINI_API_KEY${NC}"
else
    echo -e "${GREEN}✅ frontend/.env.local already exists${NC}"
fi

# Create directories
mkdir -p evidence
mkdir -p logs
mkdir -p data

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Edit frontend/.env.local and add your GEMINI_API_KEY"
echo "3. Run the application:"
echo ""
echo "   Option 1 - Frontend Only:"
echo "   $ cd frontend && npm run dev"
echo ""
echo "   Option 2 - Full Stack:"
echo "   Terminal 1: $ cd backend && source venv/bin/activate && python main.py"
echo "   Terminal 2: $ cd frontend && npm run dev"
echo ""
echo "   Option 3 - Docker:"
echo "   $ docker-compose up"
echo ""
echo "🎉 Happy Monitoring!"
