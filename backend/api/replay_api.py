"""
API endpoints for Replay Engine
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.replay_engine import replay_engine, ReplayStatus

router = APIRouter(prefix="/api/replay", tags=["Replay Engine"])

class RecordingRequest(BaseModel):
    description: Optional[str] = ""

class ReplayRequest(BaseModel):
    session_id: str
    playback_speed: float = 1.0

class DisasterScenarioRequest(BaseModel):
    scenario_name: str
    events: List[Dict[str, Any]]

@router.post("/start-recording")
async def start_recording(request: RecordingRequest):
    """Start recording a new session"""
    try:
        session_id = await replay_engine.start_recording(request.description)
        
        return {
            "session_id": session_id,
            "status": "recording_started",
            "description": request.description,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start recording: {str(e)}")

@router.post("/stop-recording/{session_id}")
async def stop_recording(session_id: str):
    """Stop recording and save session"""
    try:
        session = await replay_engine.stop_recording(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        return {
            "session": session.to_dict(),
            "status": "recording_stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop recording: {str(e)}")

@router.post("/start")
async def start_replay(request: ReplayRequest):
    """Start replaying a session"""
    try:
        success = await replay_engine.start_replay(request.session_id, request.playback_speed)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be replayed")
        
        return {
            "session_id": request.session_id,
            "playback_speed": request.playback_speed,
            "status": "replay_started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start replay: {str(e)}")

@router.post("/pause/{session_id}")
async def pause_replay(session_id: str):
    """Pause replay"""
    try:
        success = await replay_engine.pause_replay(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Replay session not found or cannot be paused")
        
        return {
            "session_id": session_id,
            "status": "replay_paused",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause replay: {str(e)}")

@router.post("/resume/{session_id}")
async def resume_replay(session_id: str):
    """Resume replay"""
    try:
        success = await replay_engine.resume_replay(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Replay session not found or cannot be resumed")
        
        return {
            "session_id": session_id,
            "status": "replay_resumed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume replay: {str(e)}")

@router.post("/stop/{session_id}")
async def stop_replay(session_id: str):
    """Stop replay"""
    try:
        success = await replay_engine.stop_replay(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Replay session not found")
        
        return {
            "session_id": session_id,
            "status": "replay_stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop replay: {str(e)}")

@router.get("/sessions")
async def get_active_sessions():
    """Get active recording and replay sessions"""
    try:
        sessions = replay_engine.get_active_sessions()
        
        return {
            "active_sessions": sessions,
            "total_active": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")

@router.get("/sessions/completed")
async def get_completed_sessions(limit: int = 50):
    """Get completed sessions"""
    try:
        sessions = replay_engine.get_completed_sessions(limit)
        
        return {
            "completed_sessions": sessions,
            "total_completed": len(sessions),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completed sessions: {str(e)}")

@router.get("/events/{session_id}")
async def get_session_events(session_id: str, limit: int = 100):
    """Get events from a session"""
    try:
        events = replay_engine.get_session_events(session_id, limit)
        
        if not events:
            raise HTTPException(status_code=404, detail="Session not found or no events")
        
        return {
            "session_id": session_id,
            "events": events,
            "total_events": len(events),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session events: {str(e)}")

@router.get("/events/recent")
async def get_recent_events(limit: int = 100, event_type: Optional[str] = None):
    """Get recent events"""
    try:
        events = replay_engine.get_recent_events(limit, event_type)
        
        return {
            "events": events,
            "event_type": event_type,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent events: {str(e)}")

@router.get("/status/{session_id}")
async def get_replay_status(session_id: str):
    """Get replay status"""
    try:
        status = replay_engine.get_replay_status(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Replay session not found")
        
        return {
            "replay_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get replay status: {str(e)}")

@router.post("/create-disaster-scenario")
async def create_disaster_scenario(request: DisasterScenarioRequest):
    """Create a replay session from disaster scenario"""
    try:
        session_id = await replay_engine.create_disaster_scenario_replay(request.events)
        
        return {
            "session_id": session_id,
            "scenario_name": request.scenario_name,
            "event_count": len(request.events),
            "status": "scenario_created",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create disaster scenario: {str(e)}")

@router.get("/analytics")
async def get_replay_analytics():
    """Get replay analytics and statistics"""
    try:
        active_sessions = replay_engine.get_active_sessions()
        completed_sessions = replay_engine.get_completed_sessions(1000)
        recent_events = replay_engine.get_recent_events(1000)
        
        # Calculate statistics
        total_sessions = len(active_sessions) + len(completed_sessions)
        
        # Event type distribution
        event_types = {}
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Session status distribution
        session_statuses = {}
        for session in active_sessions:
            status = session.get("status", "unknown")
            session_statuses[status] = session_statuses.get(status, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": len(active_sessions),
            "completed_sessions": len(completed_sessions),
            "recent_events": len(recent_events),
            "event_type_distribution": event_types,
            "session_status_distribution": session_statuses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/record-event")
async def record_system_event(event_data: Dict[str, Any]):
    """Record a system event"""
    try:
        from backend.services.replay_engine import EventType
        
        # Convert event type string to enum
        try:
            event_type = EventType(event_data.get("event_type", "system_alert"))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_data.get('event_type')}")
        
        await replay_engine.record_event(
            event_type,
            event_data.get("data", {}),
            event_data.get("source", "api"),
            event_data.get("severity", "info")
        )
        
        return {
            "status": "event_recorded",
            "event_type": event_type.value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record event: {str(e)}")
