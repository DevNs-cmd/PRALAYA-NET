"""
API endpoints for Execution Verification Layer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.execution_verification_layer import execution_verification

router = APIRouter(prefix="/verification", tags=["execution_verification"])

class DecisionSnapshotRequest(BaseModel):
    decision_id: Optional[str] = None
    decision_type: str
    decision_maker: str
    context: Dict[str, Any]
    confidence: Optional[float] = 0.7
    risk_tolerance: Optional[str] = "moderate"
    selected_action: Optional[str] = None
    involves_agents: Optional[bool] = False

class DecisionSnapshotResponse(BaseModel):
    decision_id: str
    timestamp: str
    decision_type: str
    decision_maker: str
    confidence_score: float
    risk_assessment: Dict[str, Any]
    reasoning_process: List[str]
    evidence_sources: List[str]

class MeasuredOutcomeRequest(BaseModel):
    decision_id: str
    metrics: Dict[str, float]
    method: Optional[str] = "automated"
    data_sources: Optional[List[str]] = None
    confidence: Optional[float] = 0.8

class MeasuredOutcomeResponse(BaseModel):
    measurement_id: str
    decision_id: str
    measured_metrics: Dict[str, float]
    measurement_time: str
    measurement_method: str
    measurement_confidence: float

class VerificationReportResponse(BaseModel):
    report_id: str
    decision_id: str
    verification_status: str
    verification_method: str
    verification_timestamp: str
    overall_confidence: float
    evidence_count: int
    deviation_score: float

class SystemMetricsResponse(BaseModel):
    total_decisions: int
    verified_decisions: int
    failed_decisions: int
    pending_verification: int
    verification_rate: float
    average_confidence: float
    average_deviation: float
    evidence_artifacts: int
    timestamp: str

@router.post("/capture-decision", response_model=DecisionSnapshotResponse)
async def capture_decision_snapshot(request: DecisionSnapshotRequest):
    """Capture complete decision reasoning snapshot"""
    try:
        decision_data = request.dict()
        decision_data["decision_id"] = decision_data.get("decision_id", f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        decision_id = await execution_verification.capture_decision_snapshot(decision_data)
        
        # Get the captured snapshot
        snapshot = execution_verification.decision_snapshots.get(decision_id)
        
        return DecisionSnapshotResponse(
            decision_id=snapshot.decision_id,
            timestamp=snapshot.timestamp.isoformat(),
            decision_type=snapshot.decision_type,
            decision_maker=snapshot.decision_maker,
            confidence_score=snapshot.confidence_score,
            risk_assessment=snapshot.risk_assessment,
            reasoning_process=snapshot.reasoning_process,
            evidence_sources=snapshot.evidence_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision snapshot capture failed: {str(e)}")

@router.post("/record-outcome", response_model=MeasuredOutcomeResponse)
async def record_measured_outcome(request: MeasuredOutcomeRequest):
    """Record measured actual outcome"""
    try:
        outcome_data = request.dict()
        measurement_id = await execution_verification.record_measured_outcome(
            request.decision_id, 
            outcome_data
        )
        
        # Get the recorded outcome
        outcome = execution_verification.measured_outcomes.get(request.decision_id)
        
        return MeasuredOutcomeResponse(
            measurement_id=outcome.measurement_id,
            decision_id=outcome.decision_id,
            measured_metrics=outcome.measured_metrics,
            measurement_time=outcome.measurement_time.isoformat(),
            measurement_method=outcome.measurement_method,
            measurement_confidence=outcome.measurement_confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Measured outcome recording failed: {str(e)}")

@router.get("/report/{decision_id}", response_model=VerificationReportResponse)
async def get_verification_report(decision_id: str):
    """Get verification report for decision"""
    try:
        report = execution_verification.get_verification_report(decision_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Verification report not found")
        
        return VerificationReportResponse(**report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification report retrieval failed: {str(e)}")

@router.get("/status/{decision_id}")
async def get_verification_status(decision_id: str):
    """Get verification status for decision"""
    try:
        status = execution_verification.get_verification_status(decision_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Verification status not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification status retrieval failed: {str(e)}")

@router.get("/reports/all")
async def get_all_verification_reports():
    """Get all verification reports"""
    try:
        reports = []
        for report in execution_verification.verification_reports.values():
            reports.append(VerificationReportResponse(
                report_id=report.report_id,
                decision_id=report.decision_id,
                verification_status=report.verification_status.value,
                verification_method=report.verification_method.value,
                verification_timestamp=report.verification_timestamp.isoformat(),
                overall_confidence=report.overall_confidence,
                evidence_count=len(report.evidence_artifacts),
                deviation_score=report.deviation_analysis.overall_deviation
            ))
        
        return {
            "verification_reports": reports,
            "total_reports": len(reports),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"All verification reports retrieval failed: {str(e)}")

@router.get("/system-metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """Get verification system metrics"""
    try:
        metrics = execution_verification.get_system_metrics()
        return SystemMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics retrieval failed: {str(e)}")

@router.get("/evidence-artifacts")
async def get_evidence_artifacts():
    """Get all evidence artifacts"""
    try:
        artifacts = []
        for artifact in execution_verification.evidence_artifacts.values():
            artifacts.append({
                "artifact_id": artifact.artifact_id,
                "evidence_type": artifact.evidence_type.value,
                "source": artifact.source,
                "collection_time": artifact.collection_time.isoformat(),
                "verification_status": artifact.verification_status.value,
                "confidence": artifact.confidence,
                "metadata": artifact.metadata
            })
        
        return {
            "evidence_artifacts": artifacts,
            "total_artifacts": len(artifacts),
            "verification_distribution": {
                status: len([a for a in artifacts if a["verification_status"] == status])
                for status in ["verified", "failed", "pending", "requires_review"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence artifacts retrieval failed: {str(e)}")

@router.get("/decision/{decision_id}/snapshot")
async def get_decision_snapshot(decision_id: str):
    """Get decision snapshot"""
    try:
        snapshot = execution_verification.decision_snapshots.get(decision_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Decision snapshot not found")
        
        return {
            "decision_id": snapshot.decision_id,
            "timestamp": snapshot.timestamp.isoformat(),
            "decision_type": snapshot.decision_type,
            "decision_maker": snapshot.decision_maker,
            "decision_context": snapshot.decision_context,
            "reasoning_process": snapshot.reasoning_process,
            "evidence_sources": snapshot.evidence_sources,
            "confidence_score": snapshot.confidence_score,
            "risk_assessment": snapshot.risk_assessment,
            "alternatives_considered": snapshot.alternatives_considered
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision snapshot retrieval failed: {str(e)}")

@router.get("/alerts/active")
async def get_active_verification_alerts():
    """Get active verification alerts"""
    try:
        alerts = []
        for alert in execution_verification.active_alerts.values():
            alerts.append({
                "alert_id": alert.alert_id,
                "metric_type": alert.metric_type.value,
                "alert_level": alert.alert_level.value,
                "message": alert.message,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            })
        
        return {
            "active_alerts": alerts,
            "total_alerts": len(alerts),
            "alert_levels": {
                level: len([a for a in alerts if a["alert_level"] == level])
                for level in ["info", "warning", "error", "critical"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active alerts retrieval failed: {str(e)}")

@router.get("/integrity-check")
async def perform_integrity_check():
    """Perform integrity check on evidence artifacts"""
    try:
        # Trigger integrity check
        await execution_verification._integrity_checks()
        
        # Count failed artifacts
        failed_artifacts = [
            artifact for artifact in execution_verification.evidence_artifacts.values()
            if artifact.verification_status.value == "failed"
        ]
        
        return {
            "integrity_check_completed": True,
            "total_artifacts": len(execution_verification.evidence_artifacts),
            "failed_artifacts": len(failed_artifacts),
            "failed_artifacts_list": [
                {
                    "artifact_id": artifact.artifact_id,
                    "evidence_type": artifact.evidence_type.value,
                    "source": artifact.source
                }
                for artifact in failed_artifacts
            ],
            "check_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity check failed: {str(e)}")

@router.get("/health")
async def get_verification_health():
    """Get verification system health"""
    try:
        metrics = execution_verification.get_system_metrics()
        
        return {
            "system_status": "healthy",
            "total_decisions": metrics["total_decisions"],
            "verification_rate": metrics["verification_rate"],
            "average_confidence": metrics["average_confidence"],
            "pending_verification": metrics["pending_verification"],
            "active_alerts": len(execution_verification.active_alerts),
            "last_update": datetime.now().isoformat(),
            "components": {
                "decision_capture": "operational",
                "evidence_collection": "operational",
                "verification_processing": "operational",
                "integrity_monitoring": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
