"""
Autonomous Simulation-Driven Training Mode
Background synthetic disaster scenario generation and strategy training
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import random
from collections import defaultdict

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    CYCLONE = "cyclone"
    FIRE = "fire"
    TERRORISM = "terrorism"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    WEATHER_EXTREME = "weather_extreme"
    CHEMICAL_SPILL = "chemical_spill"

class ScenarioComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class TrainingMode(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"

@dataclass
class DisasterScenario:
    """Synthetic disaster scenario for training"""
    scenario_id: str
    name: str
    disaster_type: DisasterType
    complexity: ScenarioComplexity
    epicenter: Dict[str, float]
    severity: float  # 0-1
    affected_area_km2: float
    population_density: float  # people per km2
    infrastructure_impact: Dict[str, float]
    weather_conditions: Dict[str, Any]
    time_constraints: Dict[str, Any]
    resource_constraints: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    training_objectives: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "disaster_type": self.disaster_type.value,
            "complexity": self.complexity.value,
            "epicenter": self.epicenter,
            "severity": self.severity,
            "affected_area_km2": self.affected_area_km2,
            "population_density": self.population_density,
            "infrastructure_impact": self.infrastructure_impact,
            "weather_conditions": self.weather_conditions,
            "time_constraints": self.time_constraints,
            "resource_constraints": self.resource_constraints,
            "expected_outcomes": self.expected_outcomes,
            "training_objectives": self.training_objectives,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class SimulationResult:
    """Result of scenario simulation"""
    simulation_id: str
    scenario_id: str
    start_time: datetime
    end_time: datetime
    execution_strategy: Dict[str, Any]
    actual_outcomes: Dict[str, Any]
    success_metrics: Dict[str, float]
    learning_insights: List[str]
    performance_score: float
    training_value: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "scenario_id": self.scenario_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "execution_strategy": self.execution_strategy,
            "actual_outcomes": self.actual_outcomes,
            "success_metrics": self.success_metrics,
            "learning_insights": self.learning_insights,
            "performance_score": self.performance_score,
            "training_value": self.training_value
        }

@dataclass
class StrategyUpdate:
    """Strategy learning update"""
    update_id: str
    strategy_type: str
    performance_delta: float
    new_parameters: Dict[str, Any]
    confidence: float
    scenario_context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "update_id": self.update_id,
            "strategy_type": self.strategy_type,
            "performance_delta": self.performance_delta,
            "new_parameters": self.new_parameters,
            "confidence": self.confidence,
            "scenario_context": self.scenario_context,
            "timestamp": self.timestamp.isoformat()
        }

class AutonomousSimulationTraining:
    """Autonomous simulation-driven training system"""
    
    def __init__(self):
        self.scenarios: Dict[str, DisasterScenario] = {}
        self.simulation_results: List[SimulationResult] = []
        self.strategy_updates: List[StrategyUpdate] = []
        self.training_mode = TrainingMode.HYBRID
        self.scenario_templates: Dict[str, Dict] = {}
        self.strategy_performance_history: Dict[str, List[float]] = defaultdict(list)
        self.active_simulations: Dict[str, asyncio.Task] = {}
        
        # Training parameters
        self.training_frequency_minutes = 15  # Generate scenarios every 15 minutes
        self.max_concurrent_simulations = 3
        self.performance_threshold = 0.7
        
        # Initialize scenario templates
        self._initialize_scenario_templates()
        
        # Start background training
        asyncio.create_task(self._continuous_training())
    
    def _initialize_scenario_templates(self):
        """Initialize disaster scenario templates"""
        
        # Earthquake scenarios
        self.scenario_templates["earthquake_low"] = {
            "disaster_type": DisasterType.EARTHQUAKE,
            "complexity": ScenarioComplexity.LOW,
            "severity_range": (0.3, 0.5),
            "magnitude_range": (4.0, 5.5),
            "depth_range": (5, 15),
            "infrastructure_focus": ["buildings", "roads"],
            "population_impact": "low"
        }
        
        self.scenario_templates["earthquake_high"] = {
            "disaster_type": DisasterType.EARTHQUAKE,
            "complexity": ScenarioComplexity.HIGH,
            "severity_range": (0.7, 0.9),
            "magnitude_range": (6.5, 8.0),
            "depth_range": (2, 10),
            "infrastructure_focus": ["buildings", "roads", "power", "telecom"],
            "population_impact": "high"
        }
        
        # Flood scenarios
        self.scenario_templates["flood_medium"] = {
            "disaster_type": DisasterType.FLOOD,
            "complexity": ScenarioComplexity.MEDIUM,
            "severity_range": (0.4, 0.6),
            "water_level_range": (2, 5),
            "duration_range": (12, 48),
            "infrastructure_focus": ["roads", "buildings", "water"],
            "population_impact": "medium"
        }
        
        self.scenario_templates["flood_extreme"] = {
            "disaster_type": DisasterType.FLOOD,
            "complexity": ScenarioComplexity.EXTREME,
            "severity_range": (0.8, 1.0),
            "water_level_range": (5, 10),
            "duration_range": (48, 168),
            "infrastructure_focus": ["roads", "buildings", "power", "telecom", "water"],
            "population_impact": "extreme"
        }
        
        # Cyclone scenarios
        self.scenario_templates["cyclone_medium"] = {
            "disaster_type": DisasterType.CYCLONE,
            "complexity": ScenarioComplexity.MEDIUM,
            "severity_range": (0.5, 0.7),
            "wind_speed_range": (100, 150),
            "pressure_range": (980, 1000),
            "infrastructure_focus": ["buildings", "power", "telecom"],
            "population_impact": "medium"
        }
        
        self.scenario_templates["cyclone_extreme"] = {
            "disaster_type": DisasterType.CYCLONE,
            "complexity": ScenarioComplexity.EXTREME,
            "severity_range": (0.8, 1.0),
            "wind_speed_range": (150, 250),
            "pressure_range": (950, 980),
            "infrastructure_focus": ["buildings", "power", "telecom", "roads"],
            "population_impact": "extreme"
        }
        
        # Fire scenarios
        self.scenario_templates["fire_industrial"] = {
            "disaster_type": DisasterType.FIRE,
            "complexity": ScenarioComplexity.HIGH,
            "severity_range": (0.6, 0.8),
            "temperature_range": (500, 1000),
            "area_range": (1, 10),
            "infrastructure_focus": ["industrial", "power"],
            "population_impact": "medium"
        }
        
        # Infrastructure failure scenarios
        self.scenario_templates["power_grid"] = {
            "disaster_type": DisasterType.INFRASTRUCTURE_FAILURE,
            "complexity": ScenarioComplexity.MEDIUM,
            "severity_range": (0.4, 0.7),
            "affected_nodes": (5, 15),
            "recovery_time_range": (2, 24),
            "infrastructure_focus": ["power"],
            "population_impact": "high"
        }
        
        self.scenario_templates["telecom_failure"] = {
            "disaster_type": DisasterType.INFRASTRUCTURE_FAILURE,
            "complexity": ScenarioComplexity.MEDIUM,
            "severity_range": (0.5, 0.8),
            "affected_nodes": (3, 10),
            "recovery_time_range": (1, 12),
            "infrastructure_focus": ["telecom"],
            "population_impact": "medium"
        }
    
    async def _continuous_training(self):
        """Continuous background training loop"""
        while True:
            try:
                # Generate new scenarios
                await self._generate_training_scenarios()
                
                # Process completed simulations
                await self._process_simulation_results()
                
                # Update strategies based on learning
                await self._update_training_strategies()
                
                # Wait for next training cycle
                await asyncio.sleep(self.training_frequency_minutes * 60)
                
            except Exception as e:
                print(f"Training error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _generate_training_scenarios(self):
        """Generate new training scenarios"""
        # Check if we have capacity for more simulations
        active_count = len(self.active_simulations)
        if active_count >= self.max_concurrent_simulations:
            return
        
        # Generate scenarios based on training needs
        scenarios_to_generate = min(
            self.max_concurrent_simulations - active_count,
            2  # Generate up to 2 scenarios per cycle
        )
        
        for _ in range(scenarios_to_generate):
            scenario = await self._create_synthetic_scenario()
            if scenario:
                self.scenarios[scenario.scenario_id] = scenario
                
                # Start simulation
                simulation_task = asyncio.create_task(self._run_simulation(scenario))
                self.active_simulations[scenario.scenario_id] = simulation_task
    
    async def _create_synthetic_scenario(self) -> Optional[DisasterScenario]:
        """Create synthetic disaster scenario"""
        try:
            # Select scenario template
            template_name = random.choice(list(self.scenario_templates.keys()))
            template = self.scenario_templates[template_name]
            
            # Generate scenario parameters
            scenario_id = f"scenario_{uuid.uuid4().hex[:12]}"
            
            # Generate epicenter (Mumbai area with variation)
            base_lat, base_lon = 19.0760, 72.8777
            epicenter = {
                "lat": base_lat + random.uniform(-0.2, 0.2),
                "lon": base_lon + random.uniform(-0.2, 0.2)
            }
            
            # Generate severity
            severity = random.uniform(*template["severity_range"])
            
            # Generate affected area
            affected_area = random.uniform(10, 100) * severity  # Scale with severity
            
            # Generate population density
            population_density = random.uniform(1000, 10000)  # people per km2
            
            # Generate infrastructure impact
            infrastructure_impact = {}
            for infra_type in template["infrastructure_focus"]:
                infrastructure_impact[infra_type] = random.uniform(0.3, 0.9) * severity
            
            # Generate weather conditions
            weather_conditions = {
                "temperature": random.uniform(15, 35),
                "humidity": random.uniform(40, 90),
                "wind_speed": random.uniform(0, 50),
                "visibility": random.uniform(1, 10),
                "precipitation": random.uniform(0, 50)
            }
            
            # Adjust weather based on disaster type
            if template["disaster_type"] == DisasterType.CYCLONE:
                weather_conditions.update({
                    "wind_speed": random.uniform(*template.get("wind_speed_range", (50, 100)),
                    "pressure": random.uniform(*template.get("pressure_range", (980, 1000)),
                    "precipitation": random.uniform(50, 200)
                })
            elif template["disaster_type"] == DisasterType.FLOOD:
                weather_conditions.update({
                    "precipitation": random.uniform(100, 300),
                    "humidity": random.uniform(80, 100)
                })
            
            # Generate time constraints
            time_constraints = {
                "response_time_minutes": random.randint(30, 180),
                "evacuation_time_minutes": random.randint(60, 300),
                "recovery_time_hours": random.randint(24, 168),
                "critical_window_hours": random.randint(6, 48)
            }
            
            # Generate resource constraints
            resource_constraints = {
                "available_teams": random.randint(5, 20),
                "available_vehicles": random.randint(10, 50),
                "available_equipment": random.randint(20, 100),
                "budget_limit_usd": random.randint(100000, 1000000),
                "personnel_limit": random.randint(50, 500)
            }
            
            # Generate expected outcomes
            expected_outcomes = {
                "casualties_estimate": int(affected_area * population_density * severity * 0.001),
                "infrastructure_damage_estimate": sum(infrastructure_impact.values()) / len(infrastructure_impact),
                "economic_impact_estimate": random.uniform(1000000, 10000000) * severity,
                "recovery_time_estimate": random.randint(24, 720)
            }
            
            # Generate training objectives
            training_objectives = [
                "improve_response_time",
                "optimize_resource_allocation",
                "enhance_coordination_efficiency",
                "reduce_casualties",
                "minimize_infrastructure_damage"
            ]
            
            # Add specific objectives based on disaster type
            if template["disaster_type"] == DisasterType.EARTHQUAKE:
                training_objectives.extend(["improve_search_rescue_efficiency", "enhance_structural_assessment"])
            elif template["disaster_type"] == DisasterType.FLOOD:
                training_objectives.extend(["improve_evacuation_planning", "enhance_water_management"])
            elif template["disaster_type"] == DisasterType.CYCLONE:
                training_objectives.extend(["improve_early_warning_response", "enhance_wind_damage_assessment"])
            
            scenario = DisasterScenario(
                scenario_id=scenario_id,
                name=f"{template['disaster_type'].value.title()} Training Scenario {scenario_id[-6:]}",
                disaster_type=template["disaster_type"],
                complexity=template["complexity"],
                epicenter=epicenter,
                severity=severity,
                affected_area_km2=affected_area,
                population_density=population_density,
                infrastructure_impact=infrastructure_impact,
                weather_conditions=weather_conditions,
                time_constraints=time_constraints,
                resource_constraints=resource_constraints,
                expected_outcomes=expected_outcomes,
                training_objectives=training_objectives,
                created_at=datetime.now()
            )
            
            return scenario
            
        except Exception as e:
            print(f"Scenario generation error: {str(e)}")
            return None
    
    async def _run_simulation(self, scenario: DisasterScenario) -> SimulationResult:
        """Run simulation for scenario"""
        simulation_id = f"sim_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now()
        
        try:
            # Generate execution strategy
            execution_strategy = await self._generate_execution_strategy(scenario)
            
            # Simulate execution
            actual_outcomes = await self._simulate_execution(scenario, execution_strategy)
            
            # Calculate success metrics
            success_metrics = await self._calculate_success_metrics(scenario, actual_outcomes)
            
            # Generate learning insights
            learning_insights = await self._generate_learning_insights(scenario, execution_strategy, actual_outcomes)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(success_metrics)
            
            # Calculate training value
            training_value = await self._calculate_training_value(scenario, performance_score, learning_insights)
            
            end_time = datetime.now()
            
            result = SimulationResult(
                simulation_id=simulation_id,
                scenario_id=scenario.scenario_id,
                start_time=start_time,
                end_time=end_time,
                execution_strategy=execution_strategy,
                actual_outcomes=actual_outcomes,
                success_metrics=success_metrics,
                learning_insights=learning_insights,
                performance_score=performance_score,
                training_value=training_value
            )
            
            # Store result
            self.simulation_results.append(result)
            
            # Keep only recent results
            if len(self.simulation_results) > 1000:
                self.simulation_results = self.simulation_results[-1000]
            
            # Remove from active simulations
            if scenario.scenario_id in self.active_simulations:
                del self.active_simulations[scenario.scenario_id]
            
            return result
            
        except Exception as e:
            print(f"Simulation error for {scenario.scenario_id}: {str(e)}")
            
            # Return failed result
            end_time = datetime.now()
            return SimulationResult(
                simulation_id=simulation_id,
                scenario_id=scenario.scenario_id,
                start_time=start_time,
                end_time=end_time,
                execution_strategy={},
                actual_outcomes={"error": str(e)},
                success_metrics={},
                learning_insights=[f"Simulation failed: {str(e)}"],
                performance_score=0.0,
                training_value=0.0
            )
    
    async def _generate_execution_strategy(self, scenario: DisasterScenario) -> Dict[str, Any]:
        """Generate execution strategy for scenario"""
        strategy = {
            "approach": "autonomous_coordination",
            "resource_allocation": {},
            "timeline": {},
            "coordination_protocol": "multi_agent_negotiation",
            "decision_making": "ai_optimized",
            "risk_tolerance": "adaptive"
        }
        
        # Resource allocation based on constraints
        available_teams = scenario.resource_constraints["available_teams"]
        strategy["resource_allocation"]["teams"] = {
            "search_rescue": max(1, available_teams // 3),
            "medical": max(1, available_teams // 4),
            "engineering": max(1, available_teams // 5),
            "logistics": max(1, available_teams // 6)
        }
        
        # Timeline based on time constraints
        strategy["timeline"] = {
            "initial_response": scenario.time_constraints["response_time_minutes"],
            "full_deployment": scenario.time_constraints["response_time_minutes"] * 2,
            "peak_operations": scenario.time_constraints["evacuation_time_minutes"],
            "recovery_start": scenario.time_constraints["recovery_time_hours"] * 60
        }
        
        # Adjust strategy based on disaster type
        if scenario.disaster_type == DisasterType.EARTHQUAKE:
            strategy["priority_focus"] = ["search_rescue", "medical_aid", "structural_assessment"]
            strategy["coordination_protocol"] = "centralized_command"
        elif scenario.disaster_type == DisasterType.FLOOD:
            strategy["priority_focus"] = ["evacuation", "water_management", "infrastructure_protection"]
            strategy["coordination_protocol"] = "distributed_coordination"
        elif scenario.disaster_type == DisasterType.CYCLONE:
            strategy["priority_focus"] = ["early_warning", "infrastructure_hardening", "evacuation"]
            strategy["coordination_protocol"] = "predictive_coordination"
        
        return strategy
    
    async def _simulate_execution(self, scenario: DisasterScenario, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate scenario execution"""
        
        # Simulate execution with some randomness
        execution_success = random.uniform(0.6, 1.0)
        
        # Adjust based on strategy quality
        strategy_quality = random.uniform(0.7, 0.9)
        execution_success *= strategy_quality
        
        # Adjust based on scenario severity
        severity_factor = 1.0 - (scenario.severity * 0.3)
        execution_success *= severity_factor
        
        # Calculate actual outcomes
        actual_outcomes = {
            "casualties": int(scenario.expected_outcomes["casualties_estimate"] * (2 - execution_success)),
            "infrastructure_damage": scenario.expected_outcomes["infrastructure_damage_estimate"] * (2 - execution_success),
            "economic_impact": scenario.expected_outcomes["economic_impact_estimate"] * (2 - execution_success),
            "response_time_minutes": scenario.time_constraints["response_time_minutes"] * (1 + (1 - execution_success)),
            "resource_utilization": random.uniform(0.6, 0.95),
            "coordination_efficiency": execution_success,
            "public_satisfaction": random.uniform(0.5, 0.9) * execution_success
        }
        
        return actual_outcomes
    
    async def _calculate_success_metrics(self, scenario: DisasterScenario, outcomes: Dict[str, Any]) -> Dict[str, float]:
        """Calculate success metrics"""
        
        # Response time metric
        target_response_time = scenario.time_constraints["response_time_minutes"]
        actual_response_time = outcomes["response_time_minutes"]
        response_time_score = max(0, 1 - (actual_response_time - target_response_time) / target_response_time)
        
        # Casualty reduction metric
        expected_casualties = scenario.expected_outcomes["casualties_estimate"]
        actual_casualties = outcomes["casualties"]
        casualty_reduction = max(0, 1 - (actual_casualties - expected_casualties) / max(expected_casualties, 1))
        
        # Infrastructure protection metric
        expected_damage = scenario.expected_outcomes["infrastructure_damage_estimate"]
        actual_damage = outcomes["infrastructure_damage"]
        infrastructure_protection = max(0, 1 - (actual_damage - expected_damage) / max(expected_damage, 1))
        
        # Resource efficiency metric
        resource_efficiency = outcomes["resource_utilization"]
        
        # Coordination efficiency metric
        coordination_efficiency = outcomes["coordination_efficiency"]
        
        # Overall success score
        overall_success = (
            response_time_score * 0.25 +
            casualty_reduction * 0.3 +
            infrastructure_protection * 0.2 +
            resource_efficiency * 0.15 +
            coordination_efficiency * 0.1
        )
        
        return {
            "response_time_score": response_time_score,
            "casualty_reduction": casualty_reduction,
            "infrastructure_protection": infrastructure_protection,
            "resource_efficiency": resource_efficiency,
            "coordination_efficiency": coordination_efficiency,
            "overall_success": overall_success
        }
    
    async def _generate_learning_insights(self, scenario: DisasterScenario, strategy: Dict[str, Any], outcomes: Dict[str, Any]) -> List[str]:
        """Generate learning insights from simulation"""
        insights = []
        
        # Response time insights
        if outcomes["response_time_minutes"] > scenario.time_constraints["response_time_minutes"]:
            insights.append("Response time exceeded target - consider faster deployment protocols")
        
        # Resource utilization insights
        if outcomes["resource_utilization"] < 0.7:
            insights.append("Resource utilization was low - optimize resource allocation")
        elif outcomes["resource_utilization"] > 0.9:
            insights.append("Resource utilization was high - risk of resource exhaustion")
        
        # Coordination insights
        if outcomes["coordination_efficiency"] < 0.7:
            insights.append("Coordination efficiency was low - improve communication protocols")
        
        # Strategy-specific insights
        if strategy["approach"] == "autonomous_coordination" and outcomes["coordination_efficiency"] > 0.8:
            insights.append("Autonomous coordination performed well - can be expanded to similar scenarios")
        
        # Severity-based insights
        if scenario.severity > 0.7 and outcomes["overall_success"] > 0.8:
            insights.append("High severity scenario handled successfully - strategy is robust")
        elif scenario.severity > 0.7 and outcomes["overall_success"] < 0.5:
            insights.append("High severity scenario poorly handled - strategy needs improvement")
        
        return insights
    
    async def _calculate_performance_score(self, success_metrics: Dict[str, float]) -> float:
        """Calculate overall performance score"""
        return success_metrics["overall_success"]
    
    async def _calculate_training_value(self, scenario: DisasterScenario, performance_score: float, insights: List[str]) -> float:
        """Calculate training value of scenario"""
        
        # Base value from performance
        base_value = performance_score
        
        # Complexity bonus
        complexity_bonus = {
            ScenarioComplexity.LOW: 0.1,
            ScenarioComplexity.MEDIUM: 0.2,
            ScenarioComplexity.HIGH: 0.3,
            ScenarioComplexity.EXTREME: 0.4
        }
        base_value += complexity_bonus.get(scenario.complexity, 0.2)
        
        # Insight value
        insight_value = len(insights) * 0.05
        base_value += min(insight_value, 0.2)
        
        # Novelty value (new scenario types)
        novelty_value = 0.1 if scenario.scenario_id not in [r.scenario_id for r in self.simulation_results[-10:]] else 0
        base_value += novelty_value
        
        return min(1.0, base_value)
    
    async def _process_simulation_results(self):
        """Process completed simulation results"""
        if not self.simulation_results:
            return
        
        # Get recent results
        recent_results = self.simulation_results[-20:]
        
        # Analyze performance trends
        for result in recent_results:
            success_score = result.performance_score
            
            # Update strategy performance history
            strategy_type = result.execution_strategy.get("approach", "unknown")
            self.strategy_performance_history[strategy_type].append(success_score)
            
            # Keep only recent history
            if len(self.strategy_performance_history[strategy_type]) > 100:
                self.strategy_performance_history[strategy_type] = self.strategy_performance_history[strategy_type][-100:]
    
    async def _update_training_strategies(self):
        """Update training strategies based on learning"""
        
        # Analyze strategy performance
        strategy_performance = {}
        for strategy_type, scores in self.strategy_performance_history.items():
            if scores:
                strategy_performance[strategy_type] = {
                    "average_score": np.mean(scores),
                    "recent_trend": np.mean(scores[-10:]) - np.mean(scores[-20:-10]) if len(scores) >= 20 else 0,
                    "stability": 1.0 - np.std(scores) if len(scores) > 1 else 1.0
                }
        
        # Generate strategy updates
        for strategy_type, performance in strategy_performance.items():
            if performance["recent_trend"] < -0.1:  # Declining performance
                update = StrategyUpdate(
                    update_id=f"update_{uuid.uuid4().hex[:12]}",
                    strategy_type=strategy_type,
                    performance_delta=performance["recent_trend"],
                    new_parameters={
                        "adjustment_reason": "performance_decline",
                        "recommended_changes": ["increase_coordination_frequency", "enhance_resource_allocation"],
                        "new_weights": {"response_speed": 0.3, "resource_efficiency": 0.3, "coordination": 0.4}
                    },
                    confidence=0.7,
                    scenario_context={
                        "average_score": performance["average_score"],
                        "trend": performance["recent_trend"],
                        "stability": performance["stability"]
                    },
                    timestamp=datetime.now()
                )
                
                self.strategy_updates.append(update)
                
                # Keep only recent updates
                if len(self.strategy_updates) > 500:
                    self.strategy_updates = self.strategy_updates[-500]
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get training system status"""
        return {
            "training_mode": self.training_mode.value,
            "active_simulations": len(self.active_simulations),
            "total_scenarios": len(self.scenarios),
            "completed_simulations": len(self.simulation_results),
            "strategy_updates": len(self.strategy_updates),
            "average_performance": np.mean([r.performance_score for r in self.simulation_results[-50:]]) if self.simulation_results else 0,
            "training_frequency_minutes": self.training_frequency_minutes,
            "max_concurrent_simulations": self.max_concurrent_simulations,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_scenarios(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent training scenarios"""
        recent_scenarios = sorted(self.scenarios.values(), key=lambda x: x.created_at, reverse=True)
        return [scenario.to_dict() for scenario in recent_scenarios[:limit]]
    
    def get_simulation_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent simulation results"""
        recent_results = sorted(self.simulation_results, key=lambda x: x.end_time, reverse=True)
        return [result.to_dict() for result in recent_results[:limit]]
    
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy performance analysis"""
        performance_analysis = {}
        
        for strategy_type, scores in self.strategy_performance_history.items():
            if scores:
                performance_analysis[strategy_type] = {
                    "total_simulations": len(scores),
                    "average_score": np.mean(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "recent_average": np.mean(scores[-10:]),
                    "trend": np.mean(scores[-10:]) - np.mean(scores[-20:-10]) if len(scores) >= 20 else 0,
                    "stability": 1.0 - np.std(scores) if len(scores) > 1 else 1.0
                }
        
        return performance_analysis
    
    def get_learning_insights(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent learning insights"""
        all_insights = []
        
        for result in self.simulation_results[-limit:]:
            for insight in result.learning_insights:
                all_insights.append({
                    "simulation_id": result.simulation_id,
                    "scenario_id": result.scenario_id,
                    "insight": insight,
                    "performance_score": result.performance_score,
                    "timestamp": result.end_time.isoformat()
                })
        
        return sorted(all_insights, key=lambda x: x["timestamp"], reverse=True)

# Global training system instance
autonomous_training = AutonomousSimulationTraining()
