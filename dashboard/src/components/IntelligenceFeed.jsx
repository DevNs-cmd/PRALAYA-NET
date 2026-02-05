import { useEffect, useState } from "react";
import { getSystemStatus, getDroneStatus, getDroneTelemetry } from "../services/api";

const IntelligenceFeed = ({ systemStatus }) => {
  const [status, setStatus] = useState(systemStatus);
  const [drones, setDrones] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusData, droneData] = await Promise.all([
          getSystemStatus().catch(err => {
            console.error("Error fetching system status:", err);
            return null;
          }),
          getDroneStatus().catch(err => {
            console.error("Error fetching drone status:", err);
            return { drones: [] };
          })
        ]);

        if (statusData) {
          setStatus(statusData);

          // Fetch latest decision for alerts
          if (statusData.active_disasters && statusData.active_disasters.length > 0) {
            // Alerts would come from the decision engine
            setAlerts([
              {
                type: "disaster_detected",
                severity: statusData.active_disasters[0].severity,
                message: `${statusData.active_disasters[0].type.toUpperCase()} detected at ${statusData.active_disasters[0].location?.name || 'location'}`,
                timestamp: statusData.active_disasters[0].detected_at,
                reasoning: `Satellite detection confidence: ${(statusData.active_disasters[0].severity * 100).toFixed(0)}%. Risk analysis triggered.`
              }
            ]);
          } else {
            setAlerts([]);
          }
        }

        if (droneData) {
          setDrones(droneData.drones || []);
        }
      } catch (error) {
        console.error("Error fetching intelligence data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getAlertSeverity = (severity) => {
    if (severity >= 0.8) return "critical";
    if (severity >= 0.6) return "warning";
    return "info";
  };

  const cascadingAnalysis = status?.cascading_analysis;
  const nextFailure = cascadingAnalysis?.next_failure_prediction;

  return (
    <>
      {/* Predictive Failure Insight */}
      <div className="panel-section prediction-highlight">
        <div className="section-header">
          <span className="section-title">Failure Intelligence</span>
          <span className="section-badge red">LIVE AI</span>
        </div>
        {nextFailure ? (
          <div className="prediction-card">
            <div className="prediction-label">Next Likely Component Failure:</div>
            <div className="prediction-target">{nextFailure.name}</div>
            <div className="prediction-metrics">
              <div className="prediction-metric">
                <span className="label">Probability</span>
                <span className="value">{(nextFailure.probability * 100).toFixed(0)}%</span>
              </div>
              <div className="prediction-metric">
                <span className="label">Est. Time</span>
                <span className="value">{nextFailure.estimated_time_min}m</span>
              </div>
            </div>
            <div className="prediction-status">
              <div className="status-dot pulsing"></div>
              <span>PREDICTIVE ENGINE MONITORING</span>
            </div>
          </div>
        ) : (
          <div className="empty-state">No current failure predictions</div>
        )}
      </div>

      {/* Cascading Risk Analysis */}
      <div className="panel-section">
        <div className="section-header">
          <span className="section-title">Cascading Risk Analysis</span>
        </div>
        {!cascadingAnalysis || !cascadingAnalysis.graph ? (
          <div className="empty-state">No active risk propagation</div>
        ) : (
          <>
            {cascadingAnalysis.graph.nodes
              .filter(node => node.risk > 0)
              .sort((a, b) => b.risk - a.risk)
              .map((node) => (
                <div key={node.id} className={`risk-card ${node.risk >= 0.8 ? 'critical' : ''}`}>
                  <div className="risk-card-header">
                    <span className="risk-card-title">{node.name}</span>
                    <span className={`risk-badge ${node.risk_level}`}>
                      {node.risk_level.toUpperCase()}
                    </span>
                  </div>
                  <div className="risk-metrics">
                    <div className="risk-metric">
                      <div className="risk-metric-label">Risk Level</div>
                      <div className="risk-metric-value">{(node.risk * 100).toFixed(1)}%</div>
                    </div>
                    <div className="risk-metric">
                      <div className="risk-metric-label">Type</div>
                      <div className="risk-metric-value">{node.type}</div>
                    </div>
                  </div>
                  {node.risk >= 0.8 && (
                    <div className="alert-reasoning mt-8">
                      Critical threshold exceeded. Protection protocols initiated.
                    </div>
                  )}
                </div>
              ))}

            {cascadingAnalysis.cascade_timeline && cascadingAnalysis.cascade_timeline.length > 0 && (
              <div className="timeline mt-8">
                <div className="section-title mb-8">Propagation Timeline</div>
                {cascadingAnalysis.cascade_timeline.slice(0, 5).map((event, idx) => (
                  <div key={idx} className="timeline-item">
                    <span className="timeline-time">T+{event.time_minutes}m</span>
                    <span className="timeline-event">
                      {event.node} risk: {(event.risk * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Active Alerts */}
      <div className="panel-section">
        <div className="section-header">
          <span className="section-title">Active Alerts</span>
          <span className="section-badge">{alerts.length}</span>
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">No active alerts</div>
        ) : (
          alerts.map((alert, idx) => (
            <div key={idx} className={`alert-item ${getAlertSeverity(alert.severity)}`}>
              <div className="alert-header">
                <span className="alert-type">{alert.type.replace(/_/g, ' ')}</span>
                <span className="alert-time">
                  {new Date(alert.timestamp).toLocaleTimeString('en-US', { hour12: false })}
                </span>
              </div>
              <div className="alert-message">{alert.message}</div>
              {alert.reasoning && (
                <div className="alert-reasoning">{alert.reasoning}</div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Drone Fleet */}
      <div className="panel-section">
        <div className="section-header">
          <span className="section-title">Drone Fleet</span>
          <span className="section-badge">{drones.length}</span>
        </div>
        {drones.length === 0 ? (
          <div className="empty-state">No drones deployed</div>
        ) : (
          drones.map((drone) => (
            <DroneCard key={drone.id} drone={drone} />
          ))
        )}
      </div>
    </>
  );
};

const DroneCard = ({ drone }) => {
  const [telemetry, setTelemetry] = useState(null);

  useEffect(() => {
    if (!drone.id) return;

    const fetchTelemetry = async () => {
      try {
        const data = await getDroneTelemetry(drone.id);
        setTelemetry(data);
      } catch (error) {
        console.error("Error fetching telemetry:", error);
        // Don't show error, just log it
      }
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2000);
    return () => clearInterval(interval);
  }, [drone.id]);

  const getNavigationMode = () => {
    if (drone.slam_enabled) {
      return "V-SLAM";
    }
    return "GPS";
  };

  const getSlamReasoning = () => {
    if (drone.slam_enabled) {
      return "GPS degraded → Switching to V-SLAM navigation";
    }
    return null;
  };

  return (
    <div className="telemetry-card">
      <div className="telemetry-header">
        <span className="telemetry-id">{drone.id}</span>
        <span className={`telemetry-status ${drone.slam_enabled ? 'slam' : 'active'}`}>
          {getNavigationMode()}
        </span>
      </div>
      {telemetry && (
        <>
          <div className="telemetry-grid">
            <div className="telemetry-item">
              <span className="telemetry-label">Altitude</span>
              <span className="telemetry-value">{telemetry.altitude?.toFixed(0)}m</span>
            </div>
            <div className="telemetry-item">
              <span className="telemetry-label">Speed</span>
              <span className="telemetry-value">{telemetry.speed?.toFixed(1)}m/s</span>
            </div>
            <div className="telemetry-item">
              <span className="telemetry-label">Battery</span>
              <span className="telemetry-value">{telemetry.battery?.toFixed(0)}%</span>
            </div>
            <div className="telemetry-item">
              <span className="telemetry-label">Signal</span>
              <span className="telemetry-value">{telemetry.signal_strength?.toFixed(0)}%</span>
            </div>
          </div>
          <div className="drone-visual-feed">
            <div className="feed-header">
              <span className="feed-label">V-SLAM Visual Field</span>
              <span className="feed-meta">ORB Keypoints: {telemetry.slam_points || 0}</span>
            </div>
            <div className="feed-canvas">
              {/* In a real production environment, this would be an <img src="/api/drone/stream" /> */}
              <div className="feed-overlay">
                <div className="corner tl"></div><div className="corner tr"></div>
                <div className="corner bl"></div><div className="corner br"></div>
                <div className="tracking-stats">REC ● LIVE</div>
              </div>
            </div>
          </div>
          {getSlamReasoning() && (
            <div className="alert-reasoning mt-8">
              {getSlamReasoning()}
            </div>
          )}
        </>
      )}
      {!telemetry && (
        <div className="text-muted" style={{ fontSize: '10px', marginTop: '8px' }}>
          Initializing telemetry...
        </div>
      )}
    </div>
  );
};

export default IntelligenceFeed;
