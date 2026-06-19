#!/bin/bash
# aQuickRescue - Setup & Installation Script
# Initializes the entire project

set -e  # Exit on error

echo "🚀 aQuickRescue - Full Stack Setup"
echo "===================================="
echo ""

# Check Node.js
echo "✓ Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js >= 18.0.0"
    exit 1
fi
node_version=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$node_version" -lt 18 ]; then
    echo "❌ Node.js version must be >= 18.0.0"
    exit 1
fi
echo "✅ Node.js $(node -v) found"
echo ""

# Check Python
echo "✓ Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python >= 3.11"
    exit 1
fi
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version found"
echo ""

# Install Frontend Dependencies
echo "📦 Installing Frontend dependencies..."
npm install
npm install --workspace=frontend
npm install --workspace=shared
echo "✅ Frontend dependencies installed"
echo ""

# Install Backend Dependencies
echo "📦 Installing Backend dependencies..."
pip install -r backend/requirements.txt
echo "✅ Backend dependencies installed"
echo ""

# Setup Environment Files
echo "⚙️  Setting up environment files..."
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local 2>/dev/null || echo "No .env.example found"
fi

if [ ! -f "frontend/.env.local" ]; then
    cp frontend/.env.example frontend/.env.local 2>/dev/null || echo "No frontend .env.example found"
fi
echo "✅ Environment files configured"
echo ""

# Build Packages
echo "🔨 Building packages..."
npm run build
echo "✅ Packages built"
echo ""

echo ""
echo "✨ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Start the development server:"
echo "   npm run dev --workspace=frontend"
echo ""
echo "2. In another terminal, start the backend:"
echo "   cd backend"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "3. Open browser:"
echo "   http://localhost:5173"
echo ""
echo "Demo Credentials:"
echo "  Responder: responder1 / password123"
echo "  Patient: patient1 / password123"
echo "  Admin: admin1 / password123"
echo ""
echo "📚 Documentation:"
echo "  Frontend: frontend/README.md"
echo "  Backend: backend/README.md"
echo "  API: docs/API.md"
echo ""

