import { useState } from "react";
import { triggerDisaster, clearDisasters } from "../services/api";
import TacticalSwarmControl from "./TacticalSwarmControl";

const ControlPanel = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleTriggerDisaster = async (type, severity = 0.7) => {
    setLoading(true);
    setMessage("");
    setError("");
    
    try {
      const result = await triggerDisaster(type, severity);
      setMessage(`Disaster scenario triggered: ${type.toUpperCase()}`);
      
      setTimeout(() => setMessage(""), 5000);
    } catch (error) {
      console.error("Error triggering disaster:", error);
      setError(error.message || "Failed to trigger disaster scenario");
      setTimeout(() => setError(""), 8000);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    
    try {
      await clearDisasters();
      setMessage("All scenarios cleared");
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      console.error("Error clearing disasters:", error);
      setError(error.message || "Failed to clear scenarios");
      setTimeout(() => setError(""), 8000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel-section">
      {/* Tactical Swarm Control */}
      <TacticalSwarmControl />

      <div className="section-header">
        <span className="section-title">Disaster Scenario Control</span>
      </div>
      
      {error && (
        <div className="status-item" style={{ 
          marginBottom: '12px', 
          padding: '8px', 
          background: 'rgba(196, 90, 90, 0.15)', 
          border: '1px solid var(--status-critical)',
          borderRadius: '2px' 
        }}>
          <span style={{ fontSize: '10px', color: 'var(--status-critical)' }}>{error}</span>
        </div>
      )}

      {message && (
        <div className="status-item" style={{ 
          marginBottom: '12px', 
          padding: '8px', 
          background: 'var(--bg-tertiary)', 
          borderRadius: '2px' 
        }}>
          <span className="text-secondary" style={{ fontSize: '10px' }}>{message}</span>
        </div>
      )}

      <div className="button-group">
        <button
          onClick={() => handleTriggerDisaster("flood", 0.8)}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? "Processing..." : "Flood Scenario"}
        </button>
        
        <button
          onClick={() => handleTriggerDisaster("fire", 0.75)}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? "Processing..." : "Fire Scenario"}
        </button>
        
        <button
          onClick={() => handleTriggerDisaster("earthquake", 0.85)}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? "Processing..." : "Earthquake Scenario"}
        </button>
        
        <button
          onClick={() => handleTriggerDisaster("cyclone", 0.7)}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? "Processing..." : "Cyclone Scenario"}
        </button>
      </div>

      <div className="button-group" style={{ marginTop: '16px' }}>
        <button
          onClick={handleClear}
          disabled={loading}
          className="btn"
        >
          {loading ? "Processing..." : "Clear All Scenarios"}
        </button>
      </div>

      <div className="panel-section" style={{ marginTop: '16px', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '2px' }}>
        <div className="section-title" style={{ fontSize: '10px', marginBottom: '8px' }}>
          System Response
        </div>
        <div className="text-muted" style={{ fontSize: '10px', lineHeight: '1.6' }}>
          When a scenario is triggered, the system will:
          <br />• Analyze cascading infrastructure risks
          <br />• Deploy reconnaissance assets
          <br />• Generate prioritized alerts
          <br />• Initiate response protocols
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;
