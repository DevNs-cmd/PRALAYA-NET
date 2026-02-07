"""
Replay Engine
Records and replays system events for timeline reconstruction
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque

class EventType(Enum):
    DISASTER_DETECTED = "disaster_detected"
    RISK_ASSESSMENT = "risk_assessment"
    INTENT_GENERATED = "intent_generated"
    AGENT_NEGOTIATION = "agent_negotiation"
    STABILIZATION_EXECUTED = "stabilization_executed"
    STABILITY_UPDATED = "stability_updated"
    DECISION_EXPLAINED = "decision_explained"
    SYSTEM_ALERT = "system_alert"

class ReplayStatus(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    REPLAYING = "replaying"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class SystemEvent:
    event_id: str
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    severity: str = "info"  # info, warning, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
            "severity": self.severity
        }

@dataclass
class ReplaySession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[SystemEvent] = field(default_factory=list)
    status: ReplayStatus = ReplayStatus.IDLE
    current_position: int = 0
    playback_speed: float = 1.0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "event_count": len(self.events),
            "status": self.status.value,
            "current_position": self.current_position,
            "playback_speed": self.playback_speed,
            "description": self.description,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None
        }

class ReplayEngine:
    """Records and replays system events for timeline reconstruction"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ReplaySession] = {}
        self.completed_sessions: List[ReplaySession] = []
        self.event_buffer: deque = deque(maxlen=10000)  # Keep last 10,000 events
        self.recording_session: Optional[ReplaySession] = None
        self.replay_session: Optional[ReplaySession] = None
        self.websocket_clients = set()
        
        # Start background recording
        asyncio.create_task(self._continuous_recording())
    
    async def start_recording(self, description: str = "") -> str:
        """Start recording a new session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        session = ReplaySession(
            session_id=session_id,
            start_time=datetime.now(),
            status=ReplayStatus.RECORDING,
            description=description or f"Recording started at {datetime.now().isoformat()}"
        )
        
        self.active_sessions[session_id] = session
        self.recording_session = session
        
        # Record start event
        await self.record_event(
            EventType.SYSTEM_ALERT,
            {"message": "Recording started", "session_id": session_id},
            "replay_engine",
            "info"
        )
        
        return session_id
    
    async def stop_recording(self, session_id: str) -> Optional[ReplaySession]:
        """Stop recording and save session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        session.status = ReplayStatus.COMPLETED
        session.end_time = datetime.now()
        
        # Record stop event
        await self.record_event(
            EventType.SYSTEM_ALERT,
            {"message": "Recording stopped", "session_id": session_id},
            "replay_engine",
            "info"
        )
        
        # Move to completed sessions
        self.completed_sessions.append(session)
        del self.active_sessions[session_id]
        
        if self.recording_session and self.recording_session.session_id == session_id:
            self.recording_session = None
        
        return session
    
    async def start_replay(self, session_id: str, playback_speed: float = 1.0) -> bool:
        """Start replaying a session"""
        # Find session
        session = None
        for s in self.completed_sessions:
            if s.session_id == session_id:
                session = s
                break
        
        if not session:
            return False
        
        # Create replay session
        replay_session = ReplaySession(
            session_id=f"replay_{uuid.uuid4().hex[:12]}",
            start_time=session.start_time,
            end_time=session.end_time,
            events=session.events.copy(),
            status=ReplayStatus.REPLAYING,
            current_position=0,
            playback_speed=playback_speed,
            description=f"Replaying session: {session.description}"
        )
        
        self.active_sessions[replay_session.session_id] = replay_session
        self.replay_session = replay_session
        
        # Start replay background task
        asyncio.create_task(self._replay_events(replay_session))
        
        return True
    
    async def pause_replay(self, session_id: str) -> bool:
        """Pause replay"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if session.status == ReplayStatus.REPLAYING:
                session.status = ReplayStatus.PAUSED
                return True
        return False
    
    async def resume_replay(self, session_id: str) -> bool:
        """Resume replay"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if session.status == ReplayStatus.PAUSED:
                session.status = ReplayStatus.REPLAYING
                asyncio.create_task(self._replay_events(session))
                return True
        return False
    
    async def stop_replay(self, session_id: str) -> bool:
        """Stop replay"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = ReplayStatus.COMPLETED
            del self.active_sessions[session_id]
            
            if self.replay_session and self.replay_session.session_id == session_id:
                self.replay_session = None
            
            return True
        return False
    
    async def record_event(self, event_type: EventType, data: Dict[str, Any], 
                          source: str, severity: str = "info"):
        """Record a system event"""
        event = SystemEvent(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source,
            severity=severity
        )
        
        # Add to buffer
        self.event_buffer.append(event)
        
        # Add to active recording session
        if self.recording_session:
            self.recording_session.events.append(event)
        
        # Broadcast to WebSocket clients
        await self._broadcast_event(event)
    
    async def _replay_events(self, session: ReplaySession):
        """Replay events from session"""
        if not session.events:
            return
        
        while (session.status == ReplayStatus.REPLAYING and 
               session.current_position < len(session.events)):
            
            event = session.events[session.current_position]
            
            # Broadcast replay event
            replay_event = SystemEvent(
                event_id=f"replay_{event.event_id}",
                event_type=event.event_type,
                timestamp=datetime.now(),
                data={**event.data, "replay": True, "original_timestamp": event.timestamp.isoformat()},
                source="replay_engine",
                severity=event.severity
            )
            
            await self._broadcast_event(replay_event)
            
            session.current_position += 1
            
            # Calculate delay based on playback speed
            if session.current_position < len(session.events):
                next_event = session.events[session.current_position]
                time_diff = (next_event.timestamp - event.timestamp).total_seconds()
                delay = max(0.1, time_diff / session.playback_speed)
                await asyncio.sleep(delay)
        
        # Mark as completed
        session.status = ReplayStatus.COMPLETED
        
        # Broadcast completion
        await self.record_event(
            EventType.SYSTEM_ALERT,
            {"message": "Replay completed", "session_id": session.session_id},
            "replay_engine",
            "info"
        )
    
    async def _continuous_recording(self):
        """Background continuous recording"""
        while True:
            try:
                # Auto-start recording if none active
                if not self.recording_session and len(self.event_buffer) > 0:
                    await self.start_recording("Continuous recording")
                
                # Auto-stop recording after certain duration or event count
                if self.recording_session:
                    duration = (datetime.now() - self.recording_session.start_time).total_seconds()
                    if duration > 3600 or len(self.recording_session.events) > 1000:  # 1 hour or 1000 events
                        await self.stop_recording(self.recording_session.session_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Recording error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _broadcast_event(self, event: SystemEvent):
        """Broadcast event to WebSocket clients"""
        if self.websocket_clients:
            message = {
                "type": "event",
                "event": event.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            # This would integrate with the WebSocket manager
            # await self._websocket_broadcast(message)
            pass
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get active recording/replay sessions"""
        return [session.to_dict() for session in self.active_sessions.values()]
    
    def get_completed_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get completed sessions"""
        sessions = sorted(self.completed_sessions, key=lambda s: s.start_time, reverse=True)
        return [session.to_dict() for session in sessions[:limit]]
    
    def get_session_events(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from a session"""
        # Find session
        session = None
        for s in self.completed_sessions:
            if s.session_id == session_id:
                session = s
                break
        
        if not session and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        
        if not session:
            return []
        
        events = session.events[-limit:] if len(session.events) > limit else session.events
        return [event.to_dict() for event in events]
    
    def get_recent_events(self, limit: int = 100, event_type: str = None) -> List[Dict[str, Any]]:
        """Get recent events"""
        events = list(self.event_buffer)
        
        if event_type:
            events = [e for e in events if e.event_type.value == event_type]
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        recent_events = events[:limit] if len(events) > limit else events
        return [event.to_dict() for event in recent_events]
    
    def get_replay_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get replay status"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session.session_id,
                "status": session.status.value,
                "current_position": session.current_position,
                "total_events": len(session.events),
                "progress": session.current_position / len(session.events) if session.events else 0,
                "playback_speed": session.playback_speed
            }
        return None
    
    async def create_disaster_scenario_replay(self, disaster_events: List[Dict[str, Any]]) -> str:
        """Create a replay session from disaster scenario events"""
        session_id = f"disaster_{uuid.uuid4().hex[:12]}"
        
        # Convert events to SystemEvent objects
        system_events = []
        for event_data in disaster_events:
            event = SystemEvent(
                event_id=event_data.get("event_id", f"event_{uuid.uuid4().hex[:12]}"),
                event_type=EventType(event_data.get("event_type", "system_alert")),
                timestamp=datetime.fromisoformat(event_data.get("timestamp", datetime.now().isoformat())),
                data=event_data.get("data", {}),
                source=event_data.get("source", "disaster_simulator"),
                severity=event_data.get("severity", "info")
            )
            system_events.append(event)
        
        # Sort by timestamp
        system_events.sort(key=lambda e: e.timestamp)
        
        # Create session
        start_time = system_events[0].timestamp if system_events else datetime.now()
        end_time = system_events[-1].timestamp if system_events else datetime.now()
        
        session = ReplaySession(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            events=system_events,
            status=ReplayStatus.COMPLETED,
            description="Disaster scenario replay"
        )
        
        self.completed_sessions.append(session)
        
        return session_id

# Global replay engine
replay_engine = ReplayEngine()
