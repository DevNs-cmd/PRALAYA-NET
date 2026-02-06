import React, { useState, useEffect, useRef } from 'react';
import { API_BASE } from '../services/api';

const VSLAMCameraFeed = ({ drone }) => {
    const isGpsLost = drone.gps_status === 'lost' || drone.status === 'gps_lost';
    const [imageSrc, setImageSrc] = useState('');
    const [error, setError] = useState(false);
    const [tacticalSwarmMode, setTacticalSwarmMode] = useState(false);
    const [streamConnected, setStreamConnected] = useState(false);
    const [cameraMode, setCameraMode] = useState('independent'); // 'independent' or 'broadcast'
    const imgRef = useRef(null);
    const pollingIntervalRef = useRef(null);

    // Polling mechanism to detect tactical swarm status and stream appropriately
    useEffect(() => {
        let isMounted = true;
        
        const initializeStream = async () => {
            try {
                // Check if tactical swarm is enabled
                const statusResponse = await fetch(`${API_BASE}/api/drones/tactical-swarm/status`);
                if (statusResponse.ok) {
                    const status = await statusResponse.json();
                    const isSwarmEnabled = status.tactical_swarm_enabled;
                    setTacticalSwarmMode(isSwarmEnabled);
                    setCameraMode(isSwarmEnabled ? 'broadcast' : 'independent');
                }
            } catch (err) {
                console.warn('Could not fetch tactical swarm status');
                setCameraMode('independent');
            }
        };

        initializeStream();

        if (tacticalSwarmMode) {
            // In tactical swarm mode, use MJPEG streaming for synchronized broadcast
            const img = imgRef.current;
            if (img) {
                const streamUrl = `${API_BASE}/api/drones/slam/${drone.id}/stream`;
                img.src = streamUrl;
                setStreamConnected(true);
                setError(false);
            }
        } else {
            // In independent mode, use polling for each drone's own camera feed
            const updateFrame = () => {
                if (!isMounted) return;
                setError(false);
                // Add timestamp to bypass caching
                setImageSrc(`${API_BASE}/api/drones/slam/${drone.id}/live?t=${Date.now()}`);
            };

            // Stagger updates slightly based on drone ID to reduce spike load
            const delay = parseInt(drone.id.split('_')[1] || 0) * 50;
            const initialTimeout = setTimeout(() => {
                updateFrame();
                pollingIntervalRef.current = setInterval(updateFrame, 500); // 2 FPS refresh
                return () => clearInterval(pollingIntervalRef.current);
            }, delay);

            return () => {
                isMounted = false;
                clearTimeout(initialTimeout);
                if (pollingIntervalRef.current) {
                    clearInterval(pollingIntervalRef.current);
                }
            };
        }

        return () => {
            isMounted = false;
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
            }
        };
    }, [drone.id, tacticalSwarmMode]);

    const handleImageError = () => {
        setError(true);
    };

    const handleStreamLoad = () => {
        setStreamConnected(true);
    };

    const borderColor = isGpsLost 
        ? '#ff4444' 
        : cameraMode === 'broadcast' 
            ? '#00d4ff' 
            : '#00ff66';
    
    const borderWidth = cameraMode === 'broadcast' ? '2px' : '1px';

    return (
        <div className={`intel-card drone-panel ${isGpsLost ? 'gps-lost' : ''}`} style={{
            border: `${borderWidth} solid ${borderColor}`,
            position: 'relative',
            overflow: 'hidden',
            boxShadow: cameraMode === 'broadcast' ? '0 0 10px rgba(0, 212, 255, 0.3)' : 'none'
        }}>
            {/* HUD Header */}
            <div className="feed-header" style={{ marginBottom: '4px', display: 'flex', justifyContent: 'space-between' }}>
                <span className="feed-label">
                    {drone.id}
                    {cameraMode === 'broadcast' && <span style={{ marginLeft: '6px', color: '#00d4ff', fontSize: '10px' }}>🛰️ BROADCAST</span>}
                    {cameraMode === 'independent' && <span style={{ marginLeft: '6px', color: '#00ff66', fontSize: '10px' }}>📷 OWN FEED</span>}
                </span>
                <div style={{ display: 'flex', gap: '6px' }}>
                    <span className={`status-badge ${isGpsLost ? 'bf-red' : 'bf-green'}`}>
                        {isGpsLost ? 'GPS_LOST' : 'GPS'}
                    </span>
                    <span className="status-badge bf-blue">REC</span>
                    {cameraMode === 'broadcast' && streamConnected && (
                        <span className="status-badge" style={{ backgroundColor: '#00d4ff', color: '#000' }}>STREAM</span>
                    )}
                    {cameraMode === 'independent' && (
                        <span className="status-badge" style={{ backgroundColor: '#00ff66', color: '#000' }}>LIVE</span>
                    )}
                </div>
            </div>

            {/* Main Video Feed */}
            <div className="feed-canvas" style={{ height: '140px', position: 'relative' }}>
                {cameraMode === 'broadcast' ? (
                    // MJPEG Stream mode for tactical swarm broadcast
                    <img
                        ref={imgRef}
                        alt={`Broadcast - ${drone.id}`}
                        className="live-stream-image"
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            filter: isGpsLost ? 'grayscale(100%) contrast(1.2) brightness(0.8)' : 'sepia(1) hue-rotate(60deg) brightness(1.2)',
                            display: streamConnected ? 'block' : 'none'
                        }}
                        onLoad={handleStreamLoad}
                        onError={() => {
                            setStreamConnected(false);
                            setError(true);
                        }}
                    />
                ) : (
                    // Polling mode for independent operation
                    imageSrc && !error ? (
                        <img
                            src={imageSrc}
                            alt={`View - ${drone.id}`}
                            className="live-stream-image"
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover',
                                filter: isGpsLost ? 'grayscale(100%) contrast(1.2) brightness(0.8)' : 'sepia(1) hue-rotate(60deg) brightness(1.2)'
                            }}
                            onError={handleImageError}
                        />
                    ) : null
                )}

                {(!streamConnected && cameraMode === 'broadcast') || ((!imageSrc || error) && cameraMode === 'independent') ? (
                    <div style={{
                        width: '100%', height: '100%',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: '#444', fontSize: '10px'
                    }}>
                        NO SIGNAL
                    </div>
                ) : null}

                {/* V-SLAM Overlay HUD */}
                <div className="feed-overlay">
                    <div className="corner tl"></div><div className="corner tr"></div>
                    <div className="corner bl"></div><div className="corner br"></div>

                    <div className="tracking-stats" style={{ top: 'auto', bottom: '5px', right: '5px' }}>
                        KPI: {drone.slam_points || 0}
                    </div>

                    {cameraMode === 'broadcast' && (
                        <div style={{
                            position: 'absolute',
                            top: '5px', right: '5px',
                            border: '1px solid #00d4ff',
                            color: '#00d4ff',
                            padding: '2px 6px',
                            fontWeight: 'bold',
                            fontSize: '9px',
                            backgroundColor: 'rgba(0,0,0,0.7)'
                        }}>
                            TACTICAL BROADCAST
                        </div>
                    )}

                    {cameraMode === 'independent' && (
                        <div style={{
                            position: 'absolute',
                            top: '5px', right: '5px',
                            border: '1px solid #00ff66',
                            color: '#00ff66',
                            padding: '2px 6px',
                            fontWeight: 'bold',
                            fontSize: '9px',
                            backgroundColor: 'rgba(0,0,0,0.7)'
                        }}>
                            OWN CAMERA
                        </div>
                    )}

                    {isGpsLost && (
                        <div style={{
                            position: 'absolute',
                            top: '50%', left: '50%',
                            transform: 'translate(-50%, -50%)',
                            border: '2px solid red',
                            color: 'red',
                            padding: '4px 8px',
                            fontWeight: 'bold',
                            fontSize: '12px',
                            backgroundColor: 'rgba(0,0,0,0.7)'
                        }}>
                            V-SLAM NAV ONLY
                        </div>
                    )}
                </div>
            </div>

            {/* Telemetry Footer */}
            <div className="intel-grid" style={{ marginTop: '8px', gap: '4px' }}>
                <div className="intel-item">
                    <span className="label">ALT</span>
                    <span className="value">{Math.round(drone.altitude || 0)}m</span>
                </div>
                <div className="intel-item">
                    <span className="label">SPD</span>
                    <span className="value">{Math.round(drone.speed || 0)}m/s</span>
                </div>
                <div className="intel-item">
                    <span className="label">BAT</span>
                    <span className="value">{Math.round(drone.battery || 0)}%</span>
                </div>
            </div>
        </div>
    );
};

export default VSLAMCameraFeed;
