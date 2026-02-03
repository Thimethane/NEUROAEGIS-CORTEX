"""
API Routes - RESTful endpoints for AegisAI
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import base64
import logging
from datetime import datetime

from services.database_service import db_service
from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from api.email_routes import email_router

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])
router.include_router(email_router) 

# Initialize agents (singleton pattern - initialized once)
vision_agent = VisionAgent()
planner_agent = PlannerAgent()


# ============================================================================ 
# Request/Response Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    image: str  # Base64 encoded image


class AnalyzeResponse(BaseModel):
    incident: bool
    type: str
    severity: str
    confidence: float
    reasoning: str
    # Added default empty lists to prevent ResponseValidationError
    subjects: List[str] = []
    recommended_actions: List[str] = []


class IncidentResponse(BaseModel):
    id: int
    timestamp: str
    type: str
    severity: str
    confidence: float
    reasoning: str
    subjects: List[str]
    evidence_path: str
    status: str
    created_at: str


class StatsResponse(BaseModel):
    total_incidents: int
    active_incidents: int
    severity_breakdown: dict
    recent_24h: int
    system_status: str


class HealthResponse(BaseModel):
    status: str
    components: dict
    timestamp: str


# ============================================================================ 
# Endpoints
# ============================================================================

@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "AegisAI API",
        "version": "2.5.0",
        "status": "operational"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check returns status of all components
    """
    components = {
        "database": "ok",
        "vision_agent": "ok",
        "planner_agent": "ok"
    }
    
    try:
        db_service.get_statistics()
    except Exception as e:
        components["database"] = f"error: {str(e)}"
    
    status = "healthy" if all(
        v == "ok" for v in components.values()
    ) else "degraded"
    
    return {
        "status": status,
        "components": components,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_frame(request: AnalyzeRequest):
    """
    Analyze a video frame for security threats
    """
    try:
        # Analyze frame using the singleton VisionAgent
        result = await vision_agent.process(
            base64_image=request.image,
            frame_number=0
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Analysis failed: No result returned from VisionAgent"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Route error during analysis: {str(e)}")
        # Return a structured error that matches AnalyzeResponse to avoid 500 crashes
        return {
            "incident": False,
            "type": "error",
            "severity": "low",
            "confidence": 0,
            "reasoning": f"Analysis error: {str(e)}",
            "subjects": [],
            "recommended_actions": []
        }


@router.get("/incidents", response_model=List[IncidentResponse])
async def get_incidents(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$")
):
    """Get recent incidents with optional filtering"""
    try:
        return db_service.get_recent_incidents(limit=limit, severity=severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int):
    """Get single incident by ID"""
    incident = db_service.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get system statistics"""
    try:
        stats = db_service.get_statistics()
        return {**stats, "system_status": "operational"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    status: str = Query(..., pattern="^(active|resolved|escalated|dismissed)$")
):
    """Update incident status"""
    success = db_service.update_incident_status(incident_id, status)
    if not success:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return {"success": True, "incident_id": incident_id, "status": status}


@router.delete("/incidents/cleanup")
async def cleanup_old_incidents(days: int = Query(30, ge=7, le=365)):
    """Cleanup incidents older than specified days"""
    try:
        deleted_count = db_service.cleanup_old_incidents(days)
        return {"success": True, "deleted_count": deleted_count, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/stats")
async def get_agent_stats():
    """Get performance statistics for active agents"""
    # Use existing singleton instances to get real runtime stats
    return {
        "vision_agent": vision_agent.get_stats(),
        "planner_agent": planner_agent.get_stats()
    }
