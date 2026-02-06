import React, { useState, useEffect } from 'react';
import { API_BASE } from '../services/api';

const TacticalSwarmControl = () => {
    const [swarmActive, setSwarmActive] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [dronesConnected, setDronesConnected] = useState(0);
    const [broadcastActive, setBroadcastActive] = useState(false);
    const [cameraMode, setCameraMode] = useState('independent'); // 'independent' or 'broadcast'

    // Check tactical swarm status on component mount and refresh
    useEffect(() => {
        const checkTacticalSwarmStatus = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/drones/tactical-swarm/status`);
                if (response.ok) {
                    const status = await response.json();
                    const isSwarmActive = status.tactical_swarm_enabled;
                    setSwarmActive(isSwarmActive);
                    setDronesConnected(status.drones_connected);
                    setBroadcastActive(status.broadcast_active);
                    setCameraMode(isSwarmActive ? 'broadcast' : 'independent');
                }
            } catch (err) {
                console.warn('Could not fetch tactical swarm status:', err);
            }
        };

        checkTacticalSwarmStatus();
        const interval = setInterval(checkTacticalSwarmStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const handleToggleTacticalSwarm = async () => {
        setLoading(true);
        setMessage("");

        try {
            const endpoint = swarmActive 
                ? `${API_BASE}/api/drones/tactical-swarm/disable`
                : `${API_BASE}/api/drones/tactical-swarm/enable`;

            const response = await fetch(endpoint, { method: 'POST' });
            
            if (response.ok) {
                const result = await response.json();
                setSwarmActive(!swarmActive);
                setCameraMode(!swarmActive ? 'broadcast' : 'independent');
                
                setMessage(
                    !swarmActive 
                        ? "✅ TACTICAL SWARM ACTIVATED - All drone screens display synchronized broadcast"
                        : "✅ INDEPENDENT MODE - Each drone displays its own camera feed"
                );
                setTimeout(() => setMessage(""), 4000);
            } else {
                setMessage("❌ Failed to toggle tactical swarm mode");
                setTimeout(() => setMessage(""), 4000);
            }
        } catch (error) {
            console.error("Error toggling tactical swarm:", error);
            setMessage("❌ Error: Could not communicate with server");
            setTimeout(() => setMessage(""), 4000);
        } finally {
            setLoading(false);
        }
    };

    const statusBoxStyle = (isActive) => ({
        background: isActive ? 'rgba(0, 212, 255, 0.1)' : isActive === false ? 'rgba(0, 255, 102, 0.1)' : 'rgba(100, 100, 100, 0.1)',
        padding: '8px',
        borderRadius: '2px',
        border: isActive ? '1px solid #00d4ff' : isActive === false ? '1px solid #00ff66' : '1px solid #555'
    });

    const statusColorStyle = (isActive) => ({
        color: isActive ? '#00d4ff' : isActive === false ? '#00ff66' : '#999'
    });

    return (
        <div className="intel-card" style={{
            background: swarmActive ? 'rgba(0, 212, 255, 0.05)' : 'rgba(0, 255, 102, 0.05)',
            border: swarmActive ? '2px solid #00d4ff' : '2px solid #00ff66',
            marginBottom: '12px'
        }}>
            <div className="section-header" style={{ marginBottom: '12px' }}>
                <span className="section-title" style={{ color: swarmActive ? '#00d4ff' : '#00ff66' }}>
                    {swarmActive ? '🛰️ Tactical Swarm' : '📷 Independent Cameras'}
                </span>
                {swarmActive ? (
                    <span style={{ 
                        marginLeft: '8px', 
                        fontSize: '9px', 
                        color: '#00d4ff',
                        animation: 'pulse 1s infinite'
                    }}>
                        ● BROADCAST MODE
                    </span>
                ) : (
                    <span style={{ 
                        marginLeft: '8px', 
                        fontSize: '9px', 
                        color: '#00ff66',
                        animation: 'pulse 1s infinite'
                    }}>
                        ● INDEPENDENT MODE
                    </span>
                )}
            </div>

            {message && (
                <div style={{
                    padding: '8px',
                    marginBottom: '12px',
                    background: swarmActive ? 'rgba(0, 212, 255, 0.1)' : 'rgba(0, 255, 102, 0.1)',
                    border: swarmActive ? '1px solid #00d4ff' : '1px solid #00ff66',
                    borderRadius: '2px',
                    fontSize: '10px',
                    color: swarmActive ? '#00d4ff' : '#00ff66'
                }}>
                    {message}
                </div>
            )}

            <div style={{ marginBottom: '12px' }}>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '8px',
                    marginBottom: '10px',
                    fontSize: '10px'
                }}>
                    <div style={statusBoxStyle(swarmActive !== false)}>
                        <div style={{ color: '#888', marginBottom: '4px' }}>Drones Connected</div>
                        <div style={{ ...statusColorStyle(swarmActive), fontSize: '14px', fontWeight: 'bold' }}>
                            {dronesConnected}
                        </div>
                    </div>
                    <div style={statusBoxStyle(broadcastActive)}>
                        <div style={{ color: '#888', marginBottom: '4px' }}>
                            {swarmActive ? 'Broadcast Status' : 'All Feeds Active'}
                        </div>
                        <div style={{ 
                            ...statusColorStyle(broadcastActive),
                            fontSize: '12px', 
                            fontWeight: 'bold' 
                        }}>
                            {swarmActive 
                                ? (broadcastActive ? '📡 LIVE' : 'Standby')
                                : '✅ ACTIVE'
                            }
                        </div>
                    </div>
                </div>
            </div>

            <button
                onClick={handleToggleTacticalSwarm}
                disabled={loading}
                style={{
                    width: '100%',
                    padding: '10px',
                    background: swarmActive ? '#d4003d' : '#00aa00',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.6 : 1,
                    transition: 'all 0.3s ease'
                }}
            >
                {loading ? (
                    'Processing...'
                ) : swarmActive ? (
                    '📷 SWITCH TO INDEPENDENT CAMERAS'
                ) : (
                    '🛰️ ACTIVATE TACTICAL SWARM'
                )}
            </button>

            <div style={{
                marginTop: '12px',
                padding: '10px',
                background: 'rgba(0, 100, 200, 0.05)',
                borderRadius: '2px',
                fontSize: '9px',
                color: '#999',
                lineHeight: '1.5'
            }}>
                <div style={{ marginBottom: '6px', fontWeight: 'bold', color: swarmActive ? '#00d4ff' : '#00ff66' }}>
                    {swarmActive ? 'Tactical Swarm (Broadcast Mode):' : 'Independent Mode:'}
                </div>
                {swarmActive ? (
                    <>
                        • All drone screens display synchronized broadcast<br />
                        • Real-time unified video feed across fleet<br />
                        • Enhanced tactical coordination<br />
                        • Unified visual intelligence
                    </>
                ) : (
                    <>
                        • Each drone has its own independent camera<br />
                        • Unique feed per drone visible on each screen<br />
                        • Individual SLAM processing per drone<br />
                        • Independent reconnaissance capability
                    </>
                )}
            </div>
        </div>
    );
};

export default TacticalSwarmControl;
