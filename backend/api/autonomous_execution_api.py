"""
API endpoints for Autonomous Self-Healing National Infrastructure Network
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.autonomous_execution_engine import autonomous_execution_engine
from backend.services.multi_agent_negotiation_engine import multi_agent_negotiation_engine

router = APIRouter(prefix="/autonomous", tags=["autonomous_execution"])

class IntentCreateRequest(BaseModel):
    target_infrastructure_node: str
    risk_level: float
    allowed_interventions: List[str]
    authority_level: str
    expiration_deadline: str
    evidence_requirements: List[str]

class DisasterSimulationRequest(BaseModel):
    disaster_type: str
    affected_nodes: List[str]
    severity: float

class SystemStatusResponse(BaseModel):
    national_stability_index: float
    active_intents_count: int
    total_infrastructure_nodes: int
    high_risk_nodes_count: int
    system_mode: str
    timestamp: str

@router.get("/status", response_model=SystemStatusResponse)
async def get_autonomous_status():
    """Get autonomous execution system status"""
    try:
        stability_index = autonomous_execution_engine.get_national_stability_index()
        active_intents = autonomous_execution_engine.get_active_intents()
        infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
        
        return SystemStatusResponse(
            national_stability_index=stability_index,
            active_intents_count=len(active_intents),
            total_infrastructure_nodes=infrastructure_status["total_nodes"],
            high_risk_nodes_count=infrastructure_status["high_risk_nodes"],
            system_mode="autonomous",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/stability-index")
async def get_stability_index():
    """Get current national stability index"""
    try:
        stability_index = autonomous_execution_engine.get_national_stability_index()
        
        return {
            "stability_index": stability_index,
            "status": "critical" if stability_index < 0.4 else "warning" if stability_index < 0.7 else "healthy",
            "color": "red" if stability_index < 0.4 else "yellow" if stability_index < 0.7 else "green",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stability index retrieval failed: {str(e)}")

@router.get("/infrastructure")
async def get_infrastructure_status():
    """Get infrastructure node status"""
    try:
        infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
        
        return {
            "infrastructure": infrastructure_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Infrastructure status retrieval failed: {str(e)}")

@router.get("/intents")
async def get_active_intents():
    """Get active autonomous intents"""
    try:
        active_intents = autonomous_execution_engine.get_active_intents()
        
        return {
            "active_intents": active_intents,
            "total_count": len(active_intents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active intents retrieval failed: {str(e)}")

@router.get("/execution-ledger")
async def get_execution_ledger(limit: int = 50):
    """Get execution ledger"""
    try:
        ledger = autonomous_execution_engine.get_execution_ledger(limit)
        
        return {
            "execution_ledger": ledger,
            "total_entries": len(ledger),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution ledger retrieval failed: {str(e)}")

@router.post("/simulate-disaster")
async def simulate_disaster_cascade(request: DisasterSimulationRequest):
    """Simulate disaster cascade for demonstration"""
    try:
        # Trigger disaster simulation
        cascade_result = await autonomous_execution_engine.simulate_disaster_cascade()
        
        # Create tasks for multi-agent negotiation
        for node_id in request.affected_nodes:
            task_id = multi_agent_negotiation_engine.create_task(
                task_type="power_stabilization" if "power" in node_id else "telecom_restoration",
                infrastructure_node=node_id,
                risk_level=request.severity,
                resource_requirements=[
                    {"resource_type": "technicians", "quantity": 10, "priority": 1, "urgency": request.severity}
                ]
            )
        
        return {
            "status": "disaster_simulated",
            "cascade_result": cascade_result,
            "tasks_created": len(request.affected_nodes),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disaster simulation failed: {str(e)}")

@router.get("/agents/status")
async def get_agent_status():
    """Get multi-agent status"""
    try:
        agents = multi_agent_negotiation_engine.get_agent_status()
        
        return {
            "agents": agents,
            "total_agents": len(agents),
            "available_agents": len([a for a in agents if a["status"] == "idle"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")

@router.get("/tasks/active")
async def get_active_tasks():
    """Get active negotiation tasks"""
    try:
        tasks = multi_agent_negotiation_engine.get_active_tasks()
        
        return {
            "active_tasks": tasks,
            "total_count": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active tasks retrieval failed: {str(e)}")

@router.get("/negotiation/history")
async def get_negotiation_history(limit: int = 50):
    """Get negotiation history"""
    try:
        history = multi_agent_negotiation_engine.get_negotiation_history(limit)
        
        return {
            "negotiation_history": history,
            "total_entries": len(history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation history retrieval failed: {str(e)}")

@router.get("/system-metrics")
async def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        # Get execution engine metrics
        stability_index = autonomous_execution_engine.get_national_stability_index()
        active_intents = autonomous_execution_engine.get_active_intents()
        infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
        
        # Get negotiation engine metrics
        agent_metrics = multi_agent_negotiation_engine.get_system_metrics()
        
        return {
            "autonomous_execution": {
                "stability_index": stability_index,
                "active_intents": len(active_intents),
                "infrastructure_nodes": infrastructure_status["total_nodes"],
                "high_risk_nodes": infrastructure_status["high_risk_nodes"],
                "average_risk": infrastructure_status["average_risk"]
            },
            "multi_agent_negotiation": agent_metrics,
            "overall_health": "healthy" if stability_index > 0.7 else "warning" if stability_index > 0.4 else "critical",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics retrieval failed: {str(e)}")

@router.post("/start-autonomous-demo")
async def start_autonomous_demo(background_tasks: BackgroundTasks):
    """Start full autonomous demonstration"""
    try:
        # Trigger disaster simulation in background
        background_tasks.add_task(simulate_full_demo_sequence)
        
        return {
            "status": "demo_started",
            "message": "Full autonomous demonstration started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo start failed: {str(e)}")

@router.get("/demo/status")
async def get_demo_status():
    """Get demonstration status"""
    try:
        # Get current system status as demo status
        stability_index = autonomous_execution_engine.get_national_stability_index()
        active_intents = autonomous_execution_engine.get_active_intents()
        active_tasks = multi_agent_negotiation_engine.get_active_tasks()
        
        return {
            "demo_active": True,
            "phase": "autonomous_execution",
            "stability_index": stability_index,
            "active_intents": len(active_intents),
            "active_tasks": len(active_tasks),
            "infrastructure_stabilizing": len([i for i in active_intents if i["status"] == "executing"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo status retrieval failed: {str(e)}")

@router.get("/command-center/data")
async def get_command_center_data():
    """Get comprehensive data for command center dashboard"""
    try:
        # Get all system data
        stability_index = autonomous_execution_engine.get_national_stability_index()
        infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
        active_intents = autonomous_execution_engine.get_active_intents()
        execution_ledger = autonomous_execution_engine.get_execution_ledger(20)
        agents = multi_agent_negotiation_engine.get_agent_status()
        active_tasks = multi_agent_negotiation_engine.get_active_tasks()
        
        # Prepare command center data
        return {
            "national_stability_index": {
                "value": stability_index,
                "status": "critical" if stability_index < 0.4 else "warning" if stability_index < 0.7 else "healthy",
                "color": "red" if stability_index < 0.4 else "yellow" if stability_index < 0.7 else "green"
            },
            "infrastructure": {
                "nodes": infrastructure_status["nodes"],
                "total_nodes": infrastructure_status["total_nodes"],
                "high_risk_nodes": infrastructure_status["high_risk_nodes"],
                "average_risk": infrastructure_status["average_risk"]
            },
            "autonomous_actions": {
                "active_intents": active_intents,
                "total_active": len(active_intents),
                "executing": len([i for i in active_intents if i["status"] == "executing"]),
                "completed_today": len(execution_ledger)
            },
            "agent_coordination": {
                "agents": agents,
                "total_agents": len(agents),
                "available": len([a for a in agents if a["status"] == "idle"]),
                "active_tasks": active_tasks
            },
            "execution_proof": {
                "recent_ledger": execution_ledger,
                "total_executions": len(execution_ledger)
            },
            "system_mode": "autonomous",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command center data retrieval failed: {str(e)}")

async def simulate_full_demo_sequence():
    """Simulate full autonomous demonstration sequence"""
    try:
        # Phase 1: Simulate disaster
        print("🚨 Starting disaster simulation...")
        cascade_result = await autonomous_execution_engine.simulate_disaster_cascade()
        
        # Wait for system to detect and respond
        await asyncio.sleep(5)
        
        # Phase 2: Monitor autonomous response
        print("🤖 Monitoring autonomous response...")
        for i in range(30):  # Monitor for 30 seconds
            stability_index = autonomous_execution_engine.get_national_stability_index()
            active_intents = autonomous_execution_engine.get_active_intents()
            
            print(f"Stability: {stability_index:.2f}, Active Intents: {len(active_intents)}")
            await asyncio.sleep(1)
        
        print("✅ Demo sequence completed")
        
    except Exception as e:
        print(f"Demo sequence error: {str(e)}")

# Import asyncio for demo sequence
import asyncio
