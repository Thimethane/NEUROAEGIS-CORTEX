# AegisAI Quick Verification Script
# Run from project root: .\verify.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "🛡️  AegisAI System Verification" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Helper function
function Test-File {
    param($Path, $Description)
    if (Test-Path $Path) {
        Write-Host "✅ $Description" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $Description - NOT FOUND: $Path" -ForegroundColor Red
        $script:allPassed = $false
        return $false
    }
}

Write-Host "📁 File Structure Verification" -ForegroundColor Yellow
Write-Host "─────────────────────────────" -ForegroundColor Yellow

# Backend files
Test-File "backend\__init__.py" "Backend package init"
Test-File "backend\main.py" "Backend entry point"
Test-File "backend\requirements.txt" "Python dependencies"
Test-File "backend\agents\__init__.py" "Agents package"
Test-File "backend\agents\base_agent.py" "Base agent"
Test-File "backend\agents\vision_agent.py" "Vision agent"
Test-File "backend\agents\planner_agent.py" "Planner agent"
Test-File "backend\services\__init__.py" "Services package"
Test-File "backend\services\database_service.py" "Database service"
Test-File "backend\services\action_executor.py" "Action executor"
Test-File "backend\services\video_processor.py" "Video processor"
Test-File "backend\config\settings.py" "Configuration"
Test-File "backend\api\routes.py" "API routes"
Test-File "backend\utils\logger.py" "Logger utility"

# Frontend files
Test-File "frontend\package.json" "Frontend package config"
Test-File "frontend\vite.config.ts" "Vite config"
Test-File "frontend\tsconfig.json" "TypeScript config"
Test-File "frontend\tsconfig.node.json" "TypeScript node config"
Test-File "frontend\src\index.tsx" "React entry point"
Test-File "frontend\src\App.tsx" "Main app component"
Test-File "frontend\src\constants.ts" "App constants"
Test-File "frontend\src\vite-env.d.ts" "Vite types"
Test-File "frontend\src\types\index.ts" "TypeScript types"
Test-File "frontend\src\components\VideoFeed.tsx" "VideoFeed component"
Test-File "frontend\src\components\Dashboard\Dashboard.tsx" "Dashboard component"
Test-File "frontend\src\components\index.ts" "Component exports"
Test-File "frontend\src\hooks\useMonitoring.ts" "Monitoring hook"
Test-File "frontend\src\hooks\useCamera.ts" "Camera hook"
Test-File "frontend\src\services\geminiService.ts" "Gemini service"

Write-Host ""
Write-Host "🔧 Configuration Verification" -ForegroundColor Yellow
Write-Host "────────────────────────────" -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=.+") {
        Write-Host "✅ GEMINI_API_KEY is set in .env" -ForegroundColor Green
    } else {
        Write-Host "⚠️  GEMINI_API_KEY not set in .env" -ForegroundColor Yellow
        $allPassed = $false
    }
} else {
    Write-Host "⚠️  .env file not found (copy from .env.example)" -ForegroundColor Yellow
    $allPassed = $false
}

if (Test-Path "frontend\.env.local") {
    Write-Host "✅ frontend\.env.local exists" -ForegroundColor Green
    
    $frontendEnv = Get-Content "frontend\.env.local" -Raw
    if ($frontendEnv -match "VITE_GEMINI_API_KEY=.+") {
        Write-Host "✅ VITE_GEMINI_API_KEY is set" -ForegroundColor Green
    } else {
        Write-Host "⚠️  VITE_GEMINI_API_KEY not set" -ForegroundColor Yellow
        $allPassed = $false
    }
} else {
    Write-Host "⚠️  frontend\.env.local not found" -ForegroundColor Yellow
    $allPassed = $false
}

Write-Host ""
Write-Host "📦 Dependencies Verification" -ForegroundColor Yellow
Write-Host "───────────────────────────" -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 9) {
            Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Python 3.9+ required, found: $pythonVersion" -ForegroundColor Yellow
            $allPassed = $false
        }
    }
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    $allPassed = $false
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+)\.") {
        $majorVersion = [int]$matches[1]
        if ($majorVersion -ge 18) {
            Write-Host "✅ Node.js installed: $nodeVersion" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Node.js 18+ required, found: $nodeVersion" -ForegroundColor Yellow
            $allPassed = $false
        }
    }
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
    $allPassed = $false
}

# Check if node_modules exists
if (Test-Path "frontend\node_modules") {
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Run 'npm install' in frontend directory" -ForegroundColor Yellow
}

# Check if venv exists
if (Test-Path "backend\venv") {
    Write-Host "✅ Python virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Run 'python -m venv venv' in backend directory" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔬 Quick Syntax Check" -ForegroundColor Yellow
Write-Host "────────────────────" -ForegroundColor Yellow

# Check TypeScript compilation
try {
    Push-Location frontend
    $tsCheck = npx tsc --noEmit 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ TypeScript compilation successful" -ForegroundColor Green
    } else {
        Write-Host "❌ TypeScript errors found:" -ForegroundColor Red
        Write-Host $tsCheck -ForegroundColor Red
        $allPassed = $false
    }
    Pop-Location
} catch {
    Write-Host "⚠️  Could not verify TypeScript (npm not installed?)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Ready to run:" -ForegroundColor Cyan
    Write-Host "   cd frontend && npm run dev" -ForegroundColor White
} else {
    Write-Host "⚠️  SOME CHECKS FAILED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Fix the issues listed above" -ForegroundColor White
    Write-Host "   2. Run this script again" -ForegroundColor White
    Write-Host "   3. See TEST_GUIDE.md for detailed testing" -ForegroundColor White
}

Write-Host ""
