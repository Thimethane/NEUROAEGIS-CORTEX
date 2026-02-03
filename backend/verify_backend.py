#!/usr/bin/env python3
"""
Backend Verification Script
Runs comprehensive health checks on the backend system

Usage:
    python verify_backend.py
"""

import sys
import asyncio
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def check_file_structure():
    """Verify all required files exist"""
    print_header("File Structure Verification")
    
    required_files = [
        'main.py',
        'requirements.txt',
        '__init__.py',
        'agents/__init__.py',
        'agents/base_agent.py',
        'agents/vision_agent.py',
        'agents/planner_agent.py',
        'services/__init__.py',
        'services/database_service.py',
        'services/action_executor.py',
        'services/video_processor.py',
        'config/__init__.py',
        'config/settings.py',
        'api/__init__.py',
        'api/routes.py',
        'utils/__init__.py',
        'utils/logger.py',
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print_success(f"{file}")
        else:
            print_error(f"{file} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Verify required packages are installed"""
    print_header("Dependency Verification")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'google.generativeai',
        'cv2',
        'numpy',
        'aiosqlite',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            elif package == 'google.generativeai':
                __import__('google.generativeai')
            else:
                __import__(package)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def check_configuration():
    """Verify configuration is valid"""
    print_header("Configuration Verification")
    
    try:
        from config.settings import settings
        
        # Check API key
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != 'your_gemini_api_key_here':
            print_success("GEMINI_API_KEY is set")
        else:
            print_error("GEMINI_API_KEY not set or using placeholder")
            return False
        
        # Check other settings
        print_success(f"API Host: {settings.API_HOST}")
        print_success(f"API Port: {settings.API_PORT}")
        print_success(f"Frame Rate: {settings.FRAME_SAMPLE_RATE}s")
        print_success(f"Model: {settings.GEMINI_MODEL}")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration error: {e}")
        return False


def check_database():
    """Verify database can be initialized"""
    print_header("Database Verification")
    
    try:
        from services.database_service import DatabaseService
        import tempfile
        
        # Create temp database
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        db = DatabaseService(temp_path)
        print_success("Database initialized")
        
        # Test save incident
        incident_id = db.save_incident({
            'timestamp': '2024-01-01T12:00:00',
            'type': 'test',
            'severity': 'low',
            'confidence': 75,
            'reasoning': 'Verification test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        if incident_id > 0:
            print_success(f"Incident saved (ID: {incident_id})")
        
        # Test retrieve
        incident = db.get_incident_by_id(incident_id)
        if incident:
            print_success("Incident retrieved")
        
        # Test stats
        stats = db.get_statistics()
        if stats:
            print_success("Statistics retrieved")
        
        # Cleanup
        temp_path.unlink()
        
        return True
        
    except Exception as e:
        print_error(f"Database error: {e}")
        return False


async def check_agents():
    """Verify agents can be initialized and work"""
    print_header("Agent Verification")
    
    try:
        from agents.vision_agent import VisionAgent
        from agents.planner_agent import PlannerAgent
        import numpy as np
        
        # Test VisionAgent
        vision = VisionAgent()
        print_success("VisionAgent initialized")
        
        # Test with sample frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = await vision.process(frame=frame, frame_number=1)
        
        if result and 'incident' in result:
            print_success(f"VisionAgent analysis: {result['type']}")
        else:
            print_warning("VisionAgent returned unexpected result")
        
        # Test PlannerAgent
        planner = PlannerAgent()
        print_success("PlannerAgent initialized")
        
        sample_incident = {
            'type': 'test',
            'severity': 'medium',
            'confidence': 80,
            'reasoning': 'Test incident'
        }
        
        plan = await planner.process(sample_incident)
        if plan and isinstance(plan, list):
            print_success(f"PlannerAgent created plan ({len(plan)} steps)")
        
        return True
        
    except Exception as e:
        print_error(f"Agent error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api():
    """Verify API can be imported"""
    print_header("API Verification")
    
    try:
        from main import app
        print_success("FastAPI app imported")
        
        from api.routes import router
        print_success("API router imported")
        
        return True
        
    except Exception as e:
        print_error(f"API error: {e}")
        return False


async def run_all_checks():
    """Run all verification checks"""
    print(f"\n{BLUE}🛡️  AegisAI Backend Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = {
        'File Structure': check_file_structure(),
        'Dependencies': check_dependencies(),
        'Configuration': check_configuration(),
        'Database': check_database(),
        'Agents': await check_agents(),
        'API': check_api(),
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}")
        else:
            print_error(f"{check}")
    
    print(f"\n{BLUE}Results: {passed}/{total} checks passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✅ ALL CHECKS PASSED!{RESET}")
        print(f"\n{GREEN}🚀 Backend is ready to run:{RESET}")
        print(f"{BLUE}   python main.py{RESET}\n")
        return 0
    else:
        print(f"\n{RED}❌ SOME CHECKS FAILED{RESET}")
        print(f"\n{YELLOW}📝 Fix the issues above and run again{RESET}\n")
        return 1


def main():
    """Main entry point"""
    try:
        exit_code = asyncio.run(run_all_checks())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verification cancelled{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
