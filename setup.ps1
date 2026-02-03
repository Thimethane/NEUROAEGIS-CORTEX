# ============================================================================
# AegisAI Setup Script (PowerShell)
# Fully Windows-compatible, avoids venv activation issues
# ============================================================================

Write-Host "🛡️  AegisAI Setup Script"
Write-Host "==========================`n"

# ---------------- Check Python ----------------
Write-Host "🔍 Checking Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# ---------------- Check Node.js ----------------
Write-Host "🔍 Checking Node.js..."
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# ---------------- Backend Setup ----------------
Write-Host "`n📦 Setting up Backend..."
Write-Host "========================"

$backendDir = "backend"
Set-Location $backendDir

# Create virtual environment if it doesn't exist
$venvPath = "venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
}

# Use venv Python executable directly (Windows-safe)
$venvPython = ".\$venvPath\Scripts\python.exe"

Write-Host "Installing Python dependencies..."
& $venvPython -m pip install --upgrade pip wheel setuptools
& $venvPython -m pip install --only-binary=:all: -r requirements.txt

Set-Location ..

Write-Host "✅ Backend setup complete" -ForegroundColor Green

# ---------------- Frontend Setup ----------------
Write-Host "`n📦 Setting up Frontend..."
Write-Host "========================"

$frontendDir = "frontend"
Set-Location $frontendDir

Write-Host "Installing Node.js dependencies..."
npm install

Set-Location ..

Write-Host "✅ Frontend setup complete" -ForegroundColor Green

# ---------------- Configuration ----------------
Write-Host "`n⚙️  Configuration..."
Write-Host "==================="

# Create backend .env
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..."
    Copy-Item .env.example .env
    Write-Host "📝 Please edit .env and add your GEMINI_API_KEY" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create frontend .env.local
$frontendEnv = ".\frontend\.env.local"
if (!(Test-Path $frontendEnv)) {
    Write-Host "Creating frontend/.env.local..."
    "VITE_GEMINI_API_KEY=your_key_here" | Out-File $frontendEnv
    Write-Host "📝 Please edit frontend/.env.local and add your GEMINI_API_KEY" -ForegroundColor Cyan
} else {
    Write-Host "✅ frontend/.env.local already exists" -ForegroundColor Green
}

# Create required directories
$dirs = @("evidence", "logs", "data")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}

# ---------------- Finish ----------------
Write-Host "`n✅ Setup Complete!"
Write-Host "==================`n"

Write-Host "📋 Next Steps:"
Write-Host "1. Edit .env and add your GEMINI_API_KEY"
Write-Host "2. Edit frontend/.env.local and add your GEMINI_API_KEY"
Write-Host ""
Write-Host "3. Run the application:"
Write-Host ""
Write-Host "Option 1 - Frontend Only:"
Write-Host "   cd frontend"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "Option 2 - Full Stack:"
Write-Host "   Terminal 1:"
Write-Host "     cd backend"
Write-Host "     .\venv\Scripts\python.exe main.py"
Write-Host ""
Write-Host "   Terminal 2:"
Write-Host "     cd frontend"
Write-Host "     npm run dev"
Write-Host ""
Write-Host "Option 3 - Docker:"
Write-Host "   docker-compose up"
Write-Host ""
Write-Host "🎉 Happy Monitoring!"
