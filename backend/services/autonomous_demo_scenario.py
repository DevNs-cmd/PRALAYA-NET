"""
Demo-Ready Autonomous Scenario
End-to-end autonomous disaster response demonstration
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import numpy as np

class AutonomousDemoScenario:
    """End-to-end autonomous disaster response demonstration"""
    
    def __init__(self):
        self.demo_active = False
        self.demo_start_time = None
        self.demo_events = []
        self.current_phase = "idle"
        self.disaster_risk = 0.0
        self.infrastructure_risk = 0.0
        self.agent_coordination_active = False
        self.stabilization_actions = []
        self.evidence_artifacts = []
        
        # Import services for demo
        try:
            from backend.services.autonomous_policy_engine import autonomous_policy_engine
            from backend.services.closed_loop_stabilization import closed_loop_stabilization
            from backend.services.digital_twin_cascade_forecast import cascade_forecast_engine
            from backend.services.multi_agent_negotiation import multi_agent_negotiation
            from backend.services.execution_verification_layer import execution_verification
            from backend.services.live_system_reliability import live_reliability_metrics
            
            self.policy_engine = autonomous_policy_engine
            self.stabilization_system = closed_loop_stabilization
            self.cascade_engine = cascade_forecast_engine
            self.agent_system = multi_agent_negotiation
            self.verification_system = execution_verification
            self.reliability_system = live_reliability_metrics
            
        except ImportError as e:
            print(f"Demo import error: {str(e)}")
            self.policy_engine = None
            self.stabilization_system = None
            self.cascade_engine = None
            self.agent_system = None
            self.verification_system = None
            self.reliability_system = None
    
    async def start_autonomous_demo(self) -> Dict[str, Any]:
        """Start the autonomous demo scenario"""
        try:
            self.demo_active = True
            self.demo_start_time = datetime.now()
            demo_id = f"demo_{uuid.uuid4().hex[:12]}"
            
            # Record demo start
            await self._record_demo_event("demo_started", {
                "demo_id": demo_id,
                "timestamp": self.demo_start_time.isoformat(),
                "components_ready": self._check_components_ready()
            })
            
            # Phase 1: Simulate disaster risk appearance
            await self._simulate_disaster_risk_appearance()
            
            # Phase 2: Autonomous response intent generation
            await self._autonomous_intent_generation()
            
            # Phase 3: Multi-agent coordination
            await self._multi_agent_coordination()
            
            # Phase 4: Infrastructure stabilization
            await self._infrastructure_stabilization()
            
            # Phase 5: Risk reduction visualization
            await self._risk_reduction_visualization()
            
            # Phase 6: Execution proof recording
            await self._execution_proof_recording()
            
            # Complete demo
            await self._complete_demo(demo_id)
            
            return {
                "demo_id": demo_id,
                "status": "completed",
                "duration_minutes": (datetime.now() - self.demo_start_time).total_seconds() / 60,
                "phases_completed": len(self.demo_events),
                "final_risk_level": self.disaster_risk
            }
            
        except Exception as e:
            await self._record_demo_event("demo_error", {"error": str(e)})
            return {"status": "error", "error": str(e)}
    
    async def _record_demo_event(self, event_type: str, data: Dict[str, Any]):
        """Record demo event"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase,
            "data": data
        }
        self.demo_events.append(event)
        print(f"🎭 DEMO EVENT: {event_type} - {data}")
    
    def _check_components_ready(self) -> Dict[str, bool]:
        """Check if all components are ready"""
        return {
            "policy_engine": self.policy_engine is not None,
            "stabilization_system": self.stabilization_system is not None,
            "cascade_engine": self.cascade_engine is not None,
            "agent_system": self.agent_system is not None,
            "verification_system": self.verification_system is not None,
            "reliability_system": self.reliability_system is not None
        }
    
    async def _simulate_disaster_risk_appearance(self):
        """Phase 1: Simulate disaster risk appearance"""
        self.current_phase = "risk_appearance"
        
        await self._record_demo_event("phase_start", {
            "phase": "disaster_risk_appearance",
            "description": "Simulating disaster risk appearance"
        })
        
        # Simulate increasing disaster risk
        risk_increases = [
            (0.2, "initial_risk_detected"),
            (0.4, "risk_escalating"),
            (0.6, "risk_critical"),
            (0.8, "risk_severe")
        ]
        
        for risk_level, event_name in risk_increases:
            await asyncio.sleep(2)  # Wait 2 seconds between increases
            
            self.disaster_risk = risk_level
            self.infrastructure_risk = risk_level * 0.9
            
            # Update policy engine with new risk metrics
            if self.policy_engine:
                await self.policy_engine.update_metrics({
                    "cascade_probability": risk_level,
                    "infrastructure_load": risk_level * 0.8,
                    "failure_rate": risk_level * 0.3
                })
            
            await self._record_demo_event(event_name, {
                "disaster_risk": risk_level,
                "infrastructure_risk": self.infrastructure_risk,
                "risk_level": self._get_risk_level_description(risk_level)
            })
    
    def _get_risk_level_description(self, risk: float) -> str:
        """Get risk level description"""
        if risk < 0.3:
            return "low"
        elif risk < 0.5:
            return "moderate"
        elif risk < 0.7:
            return "high"
        elif risk < 0.9:
            return "severe"
        else:
            return "critical"
    
    async def _autonomous_intent_generation(self):
        """Phase 2: Autonomous response intent generation"""
        self.current_phase = "intent_generation"
        
        await self._record_demo_event("phase_start", {
            "phase": "autonomous_intent_generation",
            "description": "System autonomously generates response intents"
        })
        
        # Wait for policy engine to trigger
        await asyncio.sleep(3)
        
        # Simulate intent generation
        intents_generated = []
        
        # High-risk stabilization intent
        intent_1 = {
            "intent_id": f"intent_{uuid.uuid4().hex[:12]}",
            "intent_type": "infrastructure_stabilization",
            "target_outcome": "Reduce cascade probability below 0.3",
            "risk_tolerance": "moderate",
            "authority_level": "autonomous",
            "confidence": 0.85,
            "resource_permissions": ["infrastructure_control", "emergency_power"],
            "expiration_hours": 6
        }
        intents_generated.append(intent_1)
        
        # Emergency response intent
        intent_2 = {
            "intent_id": f"intent_{uuid.uuid4().hex[:12]}",
            "intent_type": "emergency_response",
            "target_outcome": "Deploy agents for damage assessment",
            "risk_tolerance": "high",
            "authority_level": "autonomous",
            "confidence": 0.9,
            "resource_permissions": ["agent_deployment", "emergency_resources"],
            "expiration_hours": 4
        }
        intents_generated.append(intent_2)
        
        await self._record_demo_event("intents_generated", {
            "total_intents": len(intents_generated),
            "intents": intents_generated,
            "trigger_condition": "cascade_probability > 0.7"
        })
    
    async def _multi_agent_coordination(self):
        """Phase 3: Multi-agent coordination"""
        self.current_phase = "agent_coordination"
        
        await self._record_demo_event("phase_start", {
            "phase": "multi_agent_coordination",
            "description": "Agents coordinate through negotiation protocol"
        })
        
        # Create task for agents
        if self.agent_system:
            task_data = {
                "task_type": "infrastructure_assessment",
                "priority": 5,
                "location": {"lat": 19.0760, "lon": 72.8777},
                "required_capabilities": ["surveillance", "infrastructure_repair"],
                "minimum_capability_scores": {"surveillance": 0.7, "infrastructure_repair": 0.6},
                "estimated_duration_minutes": 45,
                "deadline": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            task_id = await self.agent_system.create_task(task_data)
            
            await self._record_demo_event("task_created", {
                "task_id": task_id,
                "task_type": task_data["task_type"],
                "priority": task_data["priority"]
            })
            
            # Wait for agent coordination
            await asyncio.sleep(4)
            
            # Simulate coalition formation
            coalition = {
                "coalition_id": f"coalition_{uuid.uuid4().hex[:12]}",
                "member_agents": ["drone_surveillance_1", "rescue_team_1", "medical_unit_1"],
                "lead_agent": "drone_surveillance_1",
                "formation_time": datetime.now().isoformat(),
                "success_probability": 0.85
            }
            
            self.agent_coordination_active = True
            
            await self._record_demo_event("coalition_formed", {
                "coalition_id": coalition["coalition_id"],
                "member_count": len(coalition["member_agents"]),
                "lead_agent": coalition["lead_agent"],
                "success_probability": coalition["success_probability"]
            })
    
    async def _infrastructure_stabilization(self):
        """Phase 4: Infrastructure stabilization"""
        self.current_phase = "infrastructure_stabilization"
        
        await self._record_demo_event("phase_start", {
            "phase": "infrastructure_stabilization",
            "description": "System executes autonomous stabilization actions"
        })
        
        # Simulate stabilization actions
        stabilization_actions = [
            {
                "action_id": f"action_{uuid.uuid4().hex[:8]}",
                "action_type": "load_redistribution",
                "target_nodes": ["power_main_mumbai", "telecom_main_mumbai"],
                "execution_time": datetime.now().isoformat(),
                "expected_risk_reduction": 0.3,
                "status": "executing"
            },
            {
                "action_id": f"action_{uuid.uuid4().hex[:8]}",
                "action_type": "backup_activation",
                "target_nodes": ["hospital_main"],
                "execution_time": datetime.now().isoformat(),
                "expected_risk_reduction": 0.2,
                "status": "executing"
            },
            {
                "action_id": f"action_{uuid.uuid4().hex[:8]}",
                "action_type": "emergency_repair",
                "target_nodes": ["bridge_sealink"],
                "execution_time": datetime.now().isoformat(),
                "expected_risk_reduction": 0.15,
                "status": "executing"
            }
        ]
        
        self.stabilization_actions = stabilization_actions
        
        await self._record_demo_event("stabilization_started", {
            "actions_count": len(stabilization_actions),
            "actions": stabilization_actions,
            "total_expected_risk_reduction": sum(a["expected_risk_reduction"] for a in stabilization_actions)
        })
        
        # Wait for stabilization execution
        await asyncio.sleep(5)
        
        # Update risk levels
        total_reduction = sum(a["expected_risk_reduction"] for a in stabilization_actions)
        self.disaster_risk = max(0.1, self.disaster_risk - total_reduction)
        self.infrastructure_risk = max(0.1, self.infrastructure_risk - total_reduction * 0.9)
        
        # Mark actions as completed
        for action in stabilization_actions:
            action["status"] = "completed"
            action["completion_time"] = datetime.now().isoformat()
        
        await self._record_demo_event("stabilization_completed", {
            "actions_completed": len(stabilization_actions),
            "final_disaster_risk": self.disaster_risk,
            "final_infrastructure_risk": self.infrastructure_risk,
            "risk_reduction_achieved": total_reduction
        })
    
    async def _risk_reduction_visualization(self):
        """Phase 5: Risk reduction visualization"""
        self.current_phase = "risk_visualization"
        
        await self._record_demo_event("phase_start", {
            "phase": "risk_reduction_visualization",
            "description": "Visualizing risk reduction on dashboard"
        })
        
        # Generate visualization data
        visualization_data = {
            "initial_risk": 0.8,
            "final_risk": self.disaster_risk,
            "risk_reduction": 0.8 - self.disaster_risk,
            "timeline": [
                {"time": "T+0s", "risk": 0.8, "event": "Risk detected"},
                {"time": "T+30s", "risk": 0.6, "event": "Intent generated"},
                {"time": "T+90s", "risk": 0.4, "event": "Agents coordinated"},
                {"time": "T+180s", "risk": self.disaster_risk, "event": "Stabilization completed"}
            ],
            "infrastructure_nodes": {
                "healthy": 15,
                "stabilized": 2,
                "failed": 0
            }
        }
        
        await self._record_demo_event("visualization_ready", {
            "risk_reduction_percentage": (0.8 - self.disaster_risk) / 0.8 * 100,
            "infrastructure_health": "improved",
            "dashboard_metrics": visualization_data
        })
    
    async def _execution_proof_recording(self):
        """Phase 6: Execution proof recording"""
        self.current_phase = "execution_proof"
        
        await self._record_demo_event("phase_start", {
            "phase": "execution_proof_recording",
            "description": "Recording execution proof in forensic ledger"
        })
        
        # Simulate forensic ledger entry
        ledger_entry = {
            "entry_id": f"ledger_{uuid.uuid4().hex[:12]}",
            "event_type": "autonomous_stabilization_completed",
            "actor_id": "autonomous_system",
            "actor_type": "ai_system",
            "action_description": "Successfully stabilized infrastructure after cascade risk detection",
            "decision_context": {
                "initial_risk": 0.8,
                "trigger_conditions": ["cascade_probability > 0.7"],
                "policies_executed": 2
            },
            "evidence_artifacts": [
                {
                    "artifact_id": f"evidence_{uuid.uuid4().hex[:8]}",
                    "evidence_type": "sensor_data",
                    "source": "infrastructure_monitoring",
                    "confidence": 0.95
                },
                {
                    "artifact_id": f"evidence_{uuid.uuid4().hex[:8]}",
                    "evidence_type": "agent_report",
                    "source": "multi_agent_system",
                    "confidence": 0.9
                }
            ],
            "outcome": {
                "success": True,
                "risk_reduction": 0.8 - self.disaster_risk,
                "infrastructure_nodes_stabilized": 2,
                "execution_time_minutes": 3
            },
            "immutable_hash": f"hash_{uuid.uuid4().hex[:16]}"
        }
        
        self.evidence_artifacts = ledger_entry["evidence_artifacts"]
        
        await self._record_demo_event("forensic_proof_recorded", {
            "ledger_entry_id": ledger_entry["entry_id"],
            "evidence_artifacts_count": len(ledger_entry["evidence_artifacts"]),
            "immutable_hash": ledger_entry["immutable_hash"],
            "verification_status": "verified"
        })
    
    async def _complete_demo(self, demo_id: str):
        """Complete the demo scenario"""
        self.current_phase = "completed"
        
        demo_duration = (datetime.now() - self.demo_start_time).total_seconds()
        
        await self._record_demo_event("demo_completed", {
            "demo_id": demo_id,
            "duration_seconds": demo_duration,
            "phases_completed": len(self.demo_events),
            "final_disaster_risk": self.disaster_risk,
            "final_infrastructure_risk": self.infrastructure_risk,
            "stabilization_actions": len(self.stabilization_actions),
            "evidence_artifacts": len(self.evidence_artifacts),
            "success": True
        })
        
        self.demo_active = False
        
        print(f"🎉 DEMO COMPLETED: {demo_id}")
        print(f"   Duration: {demo_duration:.1f} seconds")
        print(f"   Risk reduction: {(0.8 - self.disaster_risk) / 0.8 * 100:.1f}%")
        print(f"   Actions executed: {len(self.stabilization_actions)}")
        print(f"   Evidence artifacts: {len(self.evidence_artifacts)}")
    
    def get_demo_status(self) -> Dict[str, Any]:
        """Get current demo status"""
        return {
            "demo_active": self.demo_active,
            "current_phase": self.current_phase,
            "demo_start_time": self.demo_start_time.isoformat() if self.demo_start_time else None,
            "disaster_risk": self.disaster_risk,
            "infrastructure_risk": self.infrastructure_risk,
            "agent_coordination_active": self.agent_coordination_active,
            "stabilization_actions_count": len(self.stabilization_actions),
            "evidence_artifacts_count": len(self.evidence_artifacts),
            "events_count": len(self.demo_events),
            "components_ready": self._check_components_ready()
        }
    
    def get_demo_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get demo events"""
        return self.demo_events[-limit:] if self.demo_events else []
    
    def get_demo_summary(self) -> Dict[str, Any]:
        """Get demo summary"""
        if not self.demo_events:
            return {"status": "no_demo_data"}
        
        return {
            "demo_completed": not self.demo_active,
            "total_events": len(self.demo_events),
            "phases_executed": len(set(e["phase"] for e in self.demo_events)),
            "final_risk_level": self.disaster_risk,
            "risk_reduction_achieved": 0.8 - self.disaster_risk if self.disaster_risk > 0 else 0,
            "stabilization_success": len(self.stabilization_actions) > 0,
            "forensic_proof_generated": len(self.evidence_artifacts) > 0,
            "demo_events": self.demo_events
        }

# Global demo scenario instance
autonomous_demo_scenario = AutonomousDemoScenario()
