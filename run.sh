#!/bin/bash
# ============================================================================
# run.sh - Unix/Linux/Mac Run Script
# ============================================================================

# Run backend
run_backend() {
    echo "🚀 Starting AegisAI Backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python main.py
}

# Run frontend
run_frontend() {
    echo "🎨 Starting AegisAI Frontend..."
    cd frontend
    npm run dev
}

# Run video processor
run_video() {
    echo "🎥 Starting Video Processor..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python -m services.video_processor
}

# Run demo
run_demo() {
    echo "🎬 Running Demo..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python -m services.video_processor demo
}

# Parse command
case "$1" in
    backend)
        run_backend
        ;;
    frontend)
        run_frontend
        ;;
    video)
        run_video
        ;;
    demo)
        run_demo
        ;;
    *)
        echo "Usage: ./run.sh {backend|frontend|video|demo}"
        exit 1
        ;;
esac


# ============================================================================
# run.bat - Windows Run Script
# ============================================================================
# Save this as run.bat

# @echo off
# 
# if "%1"=="backend" goto backend
# if "%1"=="frontend" goto frontend
# if "%1"=="video" goto video
# if "%1"=="demo" goto demo
# goto usage
# 
# :backend
# echo Starting AegisAI Backend...
# cd backend
# call venv\Scripts\activate
# python main.py
# goto end
# 
# :frontend
# echo Starting AegisAI Frontend...
# cd frontend
# npm run dev
# goto end
# 
# :video
# echo Starting Video Processor...
# cd backend
# call venv\Scripts\activate
# python -m services.video_processor
# goto end
# 
# :demo
# echo Running Demo...
# cd backend
# call venv\Scripts\activate
# python -m services.video_processor demo
# goto end
# 
# :usage
# echo Usage: run.bat {backend^|frontend^|video^|demo}
# 
# :end
