"""
Command Replay System for Forensic Analysis and Training
Records all mission events for post-mission analysis and simulation
"""
import json
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
import os
from enum import Enum

class EventType(Enum):
    DRONE_COMMAND = "drone_command"
    FRAME_CAPTURE = "frame_capture"
    AI_DETECTION = "ai_detection"
    GPS_UPDATE = "gps_update"
    EMERGENCY_ALERT = "emergency_alert"
    SYSTEM_EVENT = "system_event"
    MISSION_START = "mission_start"
    MISSION_END = "mission_end"
    NAVIGATION_UPDATE = "navigation_update"

@dataclass
class MissionEvent:
    """Recorded mission event"""
    event_id: str
    timestamp: float
    event_type: EventType
    drone_id: Optional[str]
    payload: Dict[str, Any]
    mission_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CommandReplaySystem:
    """Forensic command replay and analysis system"""
    
    def __init__(self, db_path: str = "mission_records.db"):
        self.db_path = db_path
        self.is_recording = False
        self.current_mission_id = None
        self.event_buffer = []
        self.buffer_lock = threading.Lock()
        self.flush_thread = None
        self.flush_interval = 5  # seconds
        
        # Initialize database
        self.init_database()
        
        print("🔍 Command Replay System Initialized")
    
    def init_database(self):
        """Initialize SQLite database for event storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_events (
                event_id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                drone_id TEXT,
                mission_id TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                payload TEXT NOT NULL,
                metadata TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create missions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                start_time REAL NOT NULL,
                end_time REAL,
                area_coordinates TEXT,
                disaster_type TEXT,
                drone_count INTEGER,
                total_events INTEGER DEFAULT 0,
                mission_status TEXT DEFAULT 'recording',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_timestamp ON mission_events(mission_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON mission_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_drone_id ON mission_events(drone_id)')
        
        conn.commit()
        conn.close()
        
        print("🗄️  Database initialized for mission recording")
    
    def start_mission_recording(self, mission_id: str, area_coordinates: List[tuple] = None, 
                              disaster_type: str = None, user_id: str = None) -> str:
        """Start recording a new mission"""
        self.current_mission_id = mission_id
        
        # Record mission start event
        start_event = MissionEvent(
            event_id=f"mission_start_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.MISSION_START,
            drone_id=None,
            payload={
                'area_coordinates': area_coordinates or [],
                'disaster_type': disaster_type,
                'user_id': user_id
            },
            mission_id=mission_id,
            user_id=user_id
        )
        
        self.record_event(start_event)
        
        # Store mission metadata
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO missions (mission_id, start_time, area_coordinates, disaster_type, drone_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            mission_id,
            time.time(),
            json.dumps(area_coordinates) if area_coordinates else '[]',
            disaster_type,
            0  # Will be updated
        ))
        conn.commit()
        conn.close()
        
        # Start background flushing
        self.is_recording = True
        self.start_flush_thread()
        
        print(f"🔴 Mission recording started: {mission_id}")
        return mission_id
    
    def stop_mission_recording(self) -> Dict:
        """Stop mission recording and return summary"""
        if not self.is_recording:
            return {}
        
        self.is_recording = False
        
        # Record mission end event
        end_event = MissionEvent(
            event_id=f"mission_end_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.MISSION_END,
            drone_id=None,
            payload={'status': 'completed'},
            mission_id=self.current_mission_id
        )
        
        self.record_event(end_event)
        
        # Update mission metadata
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total events count
        cursor.execute('''
            SELECT COUNT(*) FROM mission_events WHERE mission_id = ?
        ''', (self.current_mission_id,))
        total_events = cursor.fetchone()[0]
        
        # Update mission record
        cursor.execute('''
            UPDATE missions 
            SET end_time = ?, total_events = ?, mission_status = 'completed'
            WHERE mission_id = ?
        ''', (time.time(), total_events, self.current_mission_id))
        
        conn.commit()
        conn.close()
        
        # Stop flush thread
        if self.flush_thread:
            self.flush_thread.join(timeout=10)
        
        # Generate mission summary
        summary = self.generate_mission_summary(self.current_mission_id)
        
        print(f"⏹️  Mission recording stopped: {self.current_mission_id}")
        print(f"📊 Total events recorded: {total_events}")
        
        self.current_mission_id = None
        return summary
    
    def record_event(self, event: MissionEvent):
        """Record a mission event"""
        if not self.is_recording:
            return
        
        with self.buffer_lock:
            self.event_buffer.append(event)
    
    def start_flush_thread(self):
        """Start background thread for periodic database flushing"""
        self.flush_thread = threading.Thread(target=self.flush_loop, daemon=True)
        self.flush_thread.start()
    
    def flush_loop(self):
        """Background loop to flush events to database"""
        while self.is_recording:
            self.flush_events()
            time.sleep(self.flush_interval)
        
        # Final flush when stopping
        self.flush_events()
    
    def flush_events(self):
        """Flush buffered events to database"""
        if not self.event_buffer:
            return
        
        with self.buffer_lock:
            events_to_flush = self.event_buffer.copy()
            self.event_buffer.clear()
        
        if events_to_flush:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in events_to_flush:
                cursor.execute('''
                    INSERT INTO mission_events 
                    (event_id, timestamp, event_type, drone_id, mission_id, user_id, session_id, payload, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.timestamp,
                    event.event_type.value,
                    event.drone_id,
                    event.mission_id,
                    event.user_id,
                    event.session_id,
                    json.dumps(event.payload),
                    json.dumps(event.metadata) if event.metadata else None
                ))
            
            conn.commit()
            conn.close()
            
            print(f"💾 Flushed {len(events_to_flush)} events to database")
    
    def record_drone_command(self, drone_id: str, command: str, parameters: Dict = None, 
                           user_id: str = None, session_id: str = None):
        """Record drone command event"""
        event = MissionEvent(
            event_id=f"cmd_{drone_id}_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.DRONE_COMMAND,
            drone_id=drone_id,
            payload={
                'command': command,
                'parameters': parameters or {}
            },
            mission_id=self.current_mission_id,
            user_id=user_id,
            session_id=session_id
        )
        self.record_event(event)
    
    def record_frame_capture(self, drone_id: str, frame_metadata: Dict, 
                           detection_results: List[Dict] = None):
        """Record frame capture and AI detection results"""
        event = MissionEvent(
            event_id=f"frame_{drone_id}_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.FRAME_CAPTURE,
            drone_id=drone_id,
            payload={
                'frame_metadata': frame_metadata,
                'detections': detection_results or []
            },
            mission_id=self.current_mission_id
        )
        self.record_event(event)
    
    def record_gps_update(self, drone_id: str, gps_data: Dict, accuracy: float):
        """Record GPS position update"""
        event = MissionEvent(
            event_id=f"gps_{drone_id}_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.GPS_UPDATE,
            drone_id=drone_id,
            payload={
                'gps_data': gps_data,
                'accuracy_meters': accuracy
            },
            mission_id=self.current_mission_id
        )
        self.record_event(event)
    
    def record_emergency_alert(self, drone_id: str, alert_type: str, severity: str, 
                             details: Dict = None):
        """Record emergency alert event"""
        event = MissionEvent(
            event_id=f"emergency_{drone_id}_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.EMERGENCY_ALERT,
            drone_id=drone_id,
            payload={
                'alert_type': alert_type,
                'severity': severity,
                'details': details or {}
            },
            mission_id=self.current_mission_id
        )
        self.record_event(event)
    
    def record_system_event(self, event_name: str, details: Dict = None, 
                          severity: str = "info"):
        """Record system-level event"""
        event = MissionEvent(
            event_id=f"system_{int(time.time()*1000)}",
            timestamp=time.time(),
            event_type=EventType.SYSTEM_EVENT,
            drone_id=None,
            payload={
                'event_name': event_name,
                'details': details or {},
                'severity': severity
            },
            mission_id=self.current_mission_id
        )
        self.record_event(event)
    
    def get_mission_timeline(self, mission_id: str, start_time: float = None, 
                           end_time: float = None) -> List[Dict]:
        """Retrieve mission timeline for replay"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT event_id, timestamp, event_type, drone_id, payload, metadata
            FROM mission_events 
            WHERE mission_id = ?
        '''
        params = [mission_id]
        
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)
        
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)
        
        query += ' ORDER BY timestamp ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        timeline = []
        for row in rows:
            timeline.append({
                'event_id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'drone_id': row[3],
                'payload': json.loads(row[4]) if row[4] else {},
                'metadata': json.loads(row[5]) if row[5] else None
            })
        
        return timeline
    
    def generate_mission_summary(self, mission_id: str) -> Dict:
        """Generate comprehensive mission summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get mission metadata
        cursor.execute('''
            SELECT start_time, end_time, area_coordinates, disaster_type, total_events
            FROM missions WHERE mission_id = ?
        ''', (mission_id,))
        
        mission_data = cursor.fetchone()
        if not mission_data:
            return {}
        
        start_time, end_time, area_coords, disaster_type, total_events = mission_data
        
        # Get event statistics
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM mission_events 
            WHERE mission_id = ?
            GROUP BY event_type
            ORDER BY count DESC
        ''', (mission_id,))
        
        event_stats = cursor.fetchall()
        
        # Get drone activity
        cursor.execute('''
            SELECT drone_id, COUNT(*) as event_count
            FROM mission_events 
            WHERE mission_id = ? AND drone_id IS NOT NULL
            GROUP BY drone_id
            ORDER BY event_count DESC
        ''', (mission_id,))
        
        drone_activity = cursor.fetchall()
        
        # Get detection statistics
        cursor.execute('''
            SELECT payload
            FROM mission_events 
            WHERE mission_id = ? AND event_type = 'ai_detection'
        ''', (mission_id,))
        
        detection_events = cursor.fetchall()
        total_detections = 0
        detection_types = {}
        
        for event in detection_events:
            payload = json.loads(event[0])
            detections = payload.get('detections', [])
            total_detections += len(detections)
            
            for detection in detections:
                obj_type = detection.get('object_type', 'unknown')
                detection_types[obj_type] = detection_types.get(obj_type, 0) + 1
        
        conn.close()
        
        duration = (end_time or time.time()) - start_time
        
        return {
            'mission_id': mission_id,
            'duration_seconds': round(duration, 2),
            'total_events': total_events,
            'total_detections': total_detections,
            'disaster_type': disaster_type,
            'area_analyzed': json.loads(area_coords) if area_coords else [],
            'event_distribution': {event_type: count for event_type, count in event_stats},
            'drone_activity': {drone_id: count for drone_id, count in drone_activity},
            'detection_breakdown': detection_types,
            'performance_metrics': {
                'events_per_second': round(total_events / max(duration, 1), 2),
                'detections_per_minute': round(total_detections / max(duration / 60, 1), 2)
            }
        }
    
    def replay_mission(self, mission_id: str, speed_multiplier: float = 1.0, 
                      event_callback: callable = None) -> threading.Thread:
        """Replay mission events in real-time"""
        timeline = self.get_mission_timeline(mission_id)
        if not timeline:
            print(f"⚠️  No events found for mission {mission_id}")
            return None
        
        def replay_thread():
            print(f"🎬 Starting mission replay: {mission_id}")
            print(f"   Events: {len(timeline)}")
            print(f"   Duration: {timeline[-1]['timestamp'] - timeline[0]['timestamp']:.2f} seconds")
            
            start_real_time = time.time()
            start_mission_time = timeline[0]['timestamp']
            
            for i, event in enumerate(timeline):
                # Calculate timing
                mission_time_elapsed = event['timestamp'] - start_mission_time
                expected_real_time = start_real_time + (mission_time_elapsed / speed_multiplier)
                current_real_time = time.time()
                
                # Wait if needed
                if expected_real_time > current_real_time:
                    time.sleep(expected_real_time - current_real_time)
                
                # Execute callback
                if event_callback:
                    try:
                        event_callback(event)
                    except Exception as e:
                        print(f"⚠️  Callback error for event {event['event_id']}: {e}")
                
                # Progress indicator
                if i % max(1, len(timeline) // 20) == 0:  # Every 5%
                    progress = (i + 1) / len(timeline) * 100
                    print(f"\r🔄 Replay Progress: {progress:.1f}% ({i+1}/{len(timeline)} events)", end="")
            
            print(f"\n✅ Mission replay completed: {mission_id}")
        
        replay_thread_obj = threading.Thread(target=replay_thread, daemon=True)
        replay_thread_obj.start()
        return replay_thread_obj
    
    def get_mission_list(self) -> List[Dict]:
        """Get list of all recorded missions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mission_id, start_time, end_time, disaster_type, total_events, mission_status
            FROM missions
            ORDER BY start_time DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        missions = []
        for row in rows:
            missions.append({
                'mission_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'duration': (row[2] - row[1]) if row[2] else (time.time() - row[1]),
                'disaster_type': row[3],
                'total_events': row[4],
                'status': row[5]
            })
        
        return missions

# Global instance
replay_system = CommandReplaySystem()

def start_mission_recording(mission_id: str = None, area_coordinates: List[tuple] = None,
                          disaster_type: str = None, user_id: str = None) -> str:
    """Convenience function to start mission recording"""
    if mission_id is None:
        mission_id = f"mission_{int(time.time())}"
    
    print("\n" + "="*60)
    print("🔍 COMMAND REPLAY SYSTEM - MISSION RECORDING")
    print("="*60)
    print(f"Mission ID: {mission_id}")
    print(f"Disaster Type: {disaster_type}")
    print(f"Area Coordinates: {len(area_coordinates) if area_coordinates else 0} points")
    print(f"User ID: {user_id}")
    
    replay_system.start_mission_recording(mission_id, area_coordinates, disaster_type, user_id)
    
    print("🔴 Recording started - all events will be logged for forensic analysis")
    print("🎯 Features: Timeline replay, performance analysis, training simulation")
    
    return mission_id

def stop_mission_recording() -> Dict:
    """Stop mission recording and get summary"""
    summary = replay_system.stop_mission_recording()
    
    if summary:
        print("\n" + "="*60)
        print("📊 MISSION SUMMARY")
        print("="*60)
        print(f"Duration: {summary['duration_seconds']} seconds")
        print(f"Total Events: {summary['total_events']}")
        print(f"Total Detections: {summary['total_detections']}")
        print(f"Performance: {summary['performance_metrics']['events_per_second']} events/sec")
        
        print("\n📈 Event Distribution:")
        for event_type, count in summary['event_distribution'].items():
            print(f"   {event_type}: {count}")
        
        print("\n🤖 Detection Breakdown:")
        for obj_type, count in summary['detection_breakdown'].items():
            print(f"   {obj_type}: {count}")
    
    return summary

if __name__ == "__main__":
    # Test the replay system
    import random
    
    # Start recording
    mission_id = start_mission_recording(
        area_coordinates=[(28.6139, 77.2090), (28.7041, 77.1025)],
        disaster_type="earthquake",
        user_id="test_operator"
    )
    
    # Simulate some events
    print("\n🎬 Simulating mission events...")
    
    for i in range(20):
        # Record various events
        replay_system.record_drone_command(
            drone_id=f"drone_{i%3+1}",
            command="move_to_position",
            parameters={"x": random.randint(0, 1000), "y": random.randint(0, 1000)}
        )
        
        if i % 3 == 0:
            replay_system.record_frame_capture(
                drone_id=f"drone_{i%3+1}",
                frame_metadata={"frame_id": i, "quality": "high"},
                detection_results=[{"object_type": "person", "confidence": 0.92}]
            )
        
        if i % 7 == 0:
            replay_system.record_gps_update(
                drone_id=f"drone_{i%3+1}",
                gps_data={"lat": 28.6139 + random.uniform(-0.01, 0.01),
                         "lon": 77.2090 + random.uniform(-0.01, 0.01)},
                accuracy=random.uniform(1.0, 5.0)
            )
        
        time.sleep(0.1)  # Simulate real timing
    
    # Stop recording
    summary = stop_mission_recording()
    
    # Test replay
    print("\n🎬 Testing mission replay...")
    def event_handler(event):
        print(f"Replay: {event['event_type']} from {event['drone_id']}")
    
    replay_thread = replay_system.replay_mission(mission_id, speed_multiplier=2.0, 
                                               event_callback=event_handler)
    
    if replay_thread:
        replay_thread.join()
    
    # Show mission list
    print("\n📋 Recorded Missions:")
    missions = replay_system.get_mission_list()
    for mission in missions[:3]:  # Show last 3
        print(f"   {mission['mission_id']}: {mission['total_events']} events, "
              f"{mission['duration']:.1f}s duration")