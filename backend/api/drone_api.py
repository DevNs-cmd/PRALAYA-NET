"""
Drone API - Control and monitor drones
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import StreamingResponse, Response
from typing import List, Dict, Optional
from drone.drone_controller import drone_controller
from drone.telemetry import telemetry_gen
from pydantic import BaseModel
import asyncio
from datetime import datetime
import io

router = APIRouter()

class DroneCommand(BaseModel):
    action: str  # "takeoff", "land", "move", "slam_enable", "slam_disable"
    params: Optional[Dict] = None

@router.get("/status")
async def get_drone_status():
    """
    Get status of all drones
    """
    drones = drone_controller.get_all_drones()
    return {
        "drones": drones,
        "count": len(drones),
        "active": len([d for d in drones if d.get("status") == "active"])
    }

@router.get("/status/{drone_id}")
async def get_drone_status_by_id(drone_id: str):
    """Get status of a specific drone"""
    drone = drone_controller.get_drone(drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
    return drone

@router.get("/telemetry/{drone_id}")
async def get_drone_telemetry(drone_id: str):
    """Get real-time telemetry for a drone"""
    telemetry = telemetry_gen.get_telemetry(drone_id)
    if not telemetry:
        raise HTTPException(status_code=404, detail=f"Telemetry for {drone_id} not found")
    return telemetry

@router.post("/command/{drone_id}")
async def send_drone_command(drone_id: str, command: DroneCommand):
    """Send a command to a drone"""
    result = drone_controller.execute_command(drone_id, command.action, command.params or {})
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to execute command: {command.action}")
    return result

@router.post("/deploy")
async def deploy_drone(location: Dict):
    """
    Deploy a new drone to a location
    """
    drone_id = drone_controller.deploy_drone(location)
    return {
        "status": "deployed",
        "drone_id": drone_id,
        "location": location
    }

@router.get("/slam/{drone_id}")
async def get_slam_status(drone_id: str):
    """Get V-SLAM status for a drone"""
    slam_status = drone_controller.get_slam_status(drone_id)
    if slam_status is None:
        raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
    return slam_status

@router.post("/slam/{drone_id}/enable")
async def enable_slam(drone_id: str):
    """Enable V-SLAM for a drone"""
    result = drone_controller.enable_slam(drone_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to enable SLAM")
    return {"status": "slam_enabled", "drone_id": drone_id}

@router.post("/slam/{drone_id}/disable")
async def disable_slam(drone_id: str):
    """Disable V-SLAM for a drone"""
    result = drone_controller.disable_slam(drone_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to disable SLAM")
    return {"status": "slam_disabled", "drone_id": drone_id}

# Frame buffer for live streaming - synchronized across all drones
drone_frames = {}
tactical_swarm_enabled = False
shared_broadcast_frame = None

@router.post("/slam/{drone_id}/frame")
async def upload_slam_frame(drone_id: str, request: Request):
    """
    Upload a live frame from the drone vision module
    Accepts multipart/form-data with 'file' field containing JPEG bytes
    """
    global shared_broadcast_frame
    try:
        print(f"[DEBUG] Receiving frame upload for {drone_id}")
        print(f"[DEBUG] Content-Type: {request.headers.get('content-type')}")
        
        # Try to get raw body first to see if that works
        try:
            raw_body = await request.body()
            print(f"[DEBUG] Raw body size: {len(raw_body)} bytes")
            print(f"[DEBUG] Raw body first 50 bytes: {raw_body[:50]}")
        except Exception as e:
            print(f"[DEBUG] Error reading raw body: {e}")
        
        # Parse multipart form data
        print(f"[DEBUG] About to parse form data...")
        form = await request.form()
        print(f"[DEBUG] Form parsed, keys: {list(form.keys())}")
        
        file = form.get("file")
        if not file:
            print(f"[DEBUG] No 'file' field found in form")
            raise HTTPException(status_code=400, detail="Missing 'file' field in form data")
        
        print(f"[DEBUG] File field found: {type(file)}")
        print(f"[DEBUG] File filename: {getattr(file, 'filename', 'unknown')}")
        print(f"[DEBUG] File content_type: {getattr(file, 'content_type', 'unknown')}")
        
        # Read the file content
        content = await file.read()
        print(f"[DEBUG] Content read, size: {len(content)} bytes")
        print(f"[DEBUG] Content first 50 bytes: {content[:50]}")
        
        if not content:
            print(f"[DEBUG] Empty file content")
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Store frame
        drone_frames[drone_id] = content
        print(f"[DEBUG] Frame stored for {drone_id}")
        
        # In tactical swarm mode, all drones share the broadcast frame
        if tactical_swarm_enabled:
            shared_broadcast_frame = content
            print(f"[DEBUG] Broadcast frame updated")
        
        # Log frame storage for debugging
        print(f"[Frame] Stored for {drone_id}: {len(content)} bytes")
        
        return {"status": "ok", "tactical_swarm": tactical_swarm_enabled}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Frame] ERROR storing frame for {drone_id}: {str(e)}")
        print(f"[Frame] ERROR type: {type(e)}")
        import traceback
        print(f"[Frame] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Frame upload failed: {str(e)}")

@router.get("/slam/{drone_id}/live")
async def get_slam_frame(drone_id: str):
    """
    Get single latest frame (Snapshot mode for grid view)
    In tactical swarm, returns the shared broadcast frame
    """
    global shared_broadcast_frame
    
    frame_data = None
    if tactical_swarm_enabled and shared_broadcast_frame:
        frame_data = shared_broadcast_frame
    elif drone_id in drone_frames:
        frame_data = drone_frames[drone_id]
    else:
        raise HTTPException(status_code=404, detail="Frame not found")
    
    return Response(content=frame_data, media_type="image/jpeg")

@router.get("/slam/{drone_id}/stream")
async def stream_slam_vision(drone_id: str):
    """
    MJPEG Stream for the tactical dashboard
    In tactical swarm mode, all drones receive the shared broadcast frame
    """
    async def frame_generator():
        frame_sent = 0
        while True:
            global shared_broadcast_frame
            
            frame_data = None
            if tactical_swarm_enabled and shared_broadcast_frame:
                frame_data = shared_broadcast_frame
            elif drone_id in drone_frames:
                frame_data = drone_frames[drone_id]
            
            if frame_data:
                frame_sent += 1
                if frame_sent % 30 == 0:  # Log every 30 frames
                    print(f"[Stream] {drone_id}: sent frame #{frame_sent}")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            await asyncio.sleep(0.1)  # 10 FPS roughly

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/tactical-swarm/enable")
async def enable_tactical_swarm():
    """
    Enable tactical swarm mode - all drone screens connected to OpenCV network
    Real-time camera feeds broadcast to all drones simultaneously
    """
    global tactical_swarm_enabled, shared_broadcast_frame
    tactical_swarm_enabled = True
    shared_broadcast_frame = None
    
    print("\n✨ BACKEND: Tactical Swarm Mode ENABLED")
    print("   All drone screens will display synchronized broadcast")
    
    return {
        "status": "tactical_swarm_enabled",
        "mode": "synchronized_broadcast",
        "description": "All drone cameras displaying shared OpenCV network broadcast",
        "independent_feeds": False
    }

@router.post("/tactical-swarm/disable")
async def disable_tactical_swarm():
    """
    Disable tactical swarm mode - each drone displays its own independent camera
    """
    global tactical_swarm_enabled, shared_broadcast_frame
    tactical_swarm_enabled = False
    shared_broadcast_frame = None
    
    print("\n✨ BACKEND: Tactical Swarm Mode DISABLED")
    print("   All drone screens will display their own independent cameras")
    
    return {
        "status": "tactical_swarm_disabled",
        "mode": "independent_feeds",
        "description": "Each drone displays its own independent camera feed",
        "independent_feeds": True
    }

@router.get("/tactical-swarm/status")
async def get_tactical_swarm_status():
    """
    Get current tactical swarm status with detailed mode information
    """
    return {
        "tactical_swarm_enabled": tactical_swarm_enabled,
        "drones_connected": len(drone_frames),
        "broadcast_active": True if (tactical_swarm_enabled and shared_broadcast_frame) else False,
        "mode": "synchronized" if tactical_swarm_enabled else "independent",
        "independent_feeds": not tactical_swarm_enabled,
        "description": "Each drone has independent camera" if not tactical_swarm_enabled else "All drones display broadcast",
        "drone_ids_with_frames": list(drone_frames.keys())
    }

@router.post("/slam/{drone_id}/telemetry")
async def update_slam_telemetry(drone_id: str, telemetry: Dict):
    """
    Update SLAM telemetry for a drone from an external CV module
    """
    from drone.slam_mode import slam_controller
    from drone.telemetry import telemetry_gen
    
    if drone_id not in slam_controller.active_slam_drones:
        slam_controller.enable_slam(drone_id)
        print(f"📡 AUTO-ENABLING SLAM SESSION FOR: {drone_id}")
    
    status = slam_controller.active_slam_drones[drone_id]
    keypoints = telemetry.get("keypoints", status.get("map_points", 0))
    status["map_points"] = keypoints
    status["keyframes"] = telemetry.get("keyframes", 0)
    status["status"] = telemetry.get("status", status.get("status", "mapping"))
    status["last_update"] = datetime.now().isoformat()
    
    # Mark tactical swarm status
    status["tactical_swarm"] = telemetry.get("tactical_swarm", False)
    
    # Sync with main telemetry for UI visibility
    telemetry_gen.update_telemetry(drone_id, {
        "slam_points": keypoints,
        "slam_status": "active" if keypoints > 0 else "inactive",
        "tactical_swarm": telemetry.get("tactical_swarm", False)
    })
    
    return {"status": "updated", "tactical_swarm": telemetry.get("tactical_swarm", False)}
