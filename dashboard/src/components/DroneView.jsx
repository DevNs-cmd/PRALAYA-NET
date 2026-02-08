import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

const DroneView = () => {
  const navigate = useNavigate()
  const [cameraPermission, setCameraPermission] = useState('prompt')
  const [streamActive, setStreamActive] = useState(false)
  const [error, setError] = useState(null)
  const [droneId, setDroneId] = useState('DRONE-001')
  const [telemetry, setTelemetry] = useState({
    altitude: 120,
    speed: 15,
    heading: 45,
    battery: 85,
    signal: 98
  })
  const [activeView, setActiveView] = useState('grid') // 'grid' or 'single'
  const [selectedDrone, setSelectedDrone] = useState(0)
  
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  // Request camera permission
  const requestCameraPermission = async () => {
    try {
      console.log('[DroneView] Requesting camera permission...')
      setCameraPermission('prompt')
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setCameraPermission('granted')
        setStreamActive(true)
        setError(null)
        console.log('[DroneView] Camera permission granted')
        
        // Start telemetry simulation
        startTelemetrySimulation()
      }
    } catch (err) {
      console.error('[DroneView] Camera permission denied:', err)
      setCameraPermission('denied')
      setError('Camera access denied. Please enable camera permissions to view drone feeds.')
      setStreamActive(false)
    }
  }

  // Start simulated telemetry updates
  const startTelemetrySimulation = () => {
    intervalRef.current = setInterval(() => {
      setTelemetry(prev => ({
        altitude: Math.max(50, Math.min(150, prev.altitude + (Math.random() - 0.5) * 5)),
        speed: Math.max(5, Math.min(25, prev.speed + (Math.random() - 0.5) * 2)),
        heading: (prev.heading + (Math.random() - 0.5) * 10 + 360) % 360,
        battery: Math.max(10, prev.battery - 0.01),
        signal: Math.max(80, Math.min(100, prev.signal + (Math.random() - 0.5) * 2))
      }))
    }, 1000)
  }

  // Stop stream when component unmounts
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Auto-start camera on mount
  useEffect(() => {
    const autoStart = async () => {
      await requestCameraPermission()
    }
    autoStart()
  }, [])

  // Generate drone grid positions
  const dronePositions = Array.from({ length: 12 }, (_, i) => ({
    id: `DRONE-${String(i + 1).padStart(3, '0')}`,
    type: ['Surveillance', 'Rescue', 'Delivery'][i % 3],
    status: i === selectedDrone ? 'active' : 'stream',
    position: {
      lat: 28.6139 + (i - 6) * 0.001,
      lon: 77.2090 + (i % 3 - 1) * 0.001
    }
  }))

  const formatTime = () => {
    const now = new Date()
    return now.toISOString().split('T')[1].split('.')[0] + ' UTC'
  }

  const getHeadingDirection = (heading) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    return directions[Math.round(heading / 45) % 8]
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0b10',
      color: '#e8e9ea',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(180deg, #1a1d29 0%, #151720 100%)',
        borderBottom: '1px solid #3a3d4a',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'rgba(74, 144, 226, 0.15)',
              border: '1px solid rgba(74, 144, 226, 0.3)',
              color: '#4a90e2',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            ← Back
          </button>
          
          <div>
            <h1 style={{ 
              fontSize: '18px', 
              fontWeight: '700', 
              margin: 0,
              background: 'linear-gradient(90deg, #4a90e2, #c45a5a)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              🚁 PRALAYA-NET Drone Operations
            </h1>
            <div style={{ fontSize: '10px', color: '#8a8d94', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Live Multi-Drone Surveillance System
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Status Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '20px'
          }}>
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: streamActive ? '#00ff88' : '#ff4444',
              animation: streamActive ? 'pulse 2s infinite' : 'none'
            }}></span>
            <span style={{ fontSize: '12px', fontWeight: '600' }}>
              {streamActive ? 'LIVE FEED' : 'OFFLINE'}
            </span>
          </div>

          {/* Timestamp */}
          <div style={{ fontSize: '14px', fontFamily: 'monospace', color: '#8a8d94' }}>
            {formatTime()}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ display: 'flex', height: 'calc(100vh - 60px)' }}>
        {/* Left Sidebar - Drone List */}
        <aside style={{
          width: '280px',
          background: 'linear-gradient(180deg, #1a1d29 0%, #151720 100%)',
          borderRight: '1px solid #3a3d4a',
          overflowY: 'auto',
          padding: '16px'
        }}>
          <h2 style={{ 
            fontSize: '14px', 
            fontWeight: '600', 
            marginBottom: '16px',
            color: '#8a8d94',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            🛸 Fleet ({dronePositions.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {dronePositions.map((drone, index) => (
              <div
                key={drone.id}
                onClick={() => setSelectedDrone(index)}
                style={{
                  padding: '12px',
                  background: selectedDrone === index 
                    ? 'rgba(74, 144, 226, 0.15)' 
                    : 'rgba(0,0,0,0.2)',
                  border: selectedDrone === index 
                    ? '1px solid rgba(74, 144, 226, 0.4)' 
                    : '1px solid transparent',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '6px'
                }}>
                  <span style={{ fontWeight: '600', fontSize: '13px' }}>{drone.id}</span>
                  <span style={{
                    fontSize: '9px',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    background: selectedDrone === index ? '#4a90e2' : '#5a8a5a',
                    color: '#fff'
                  }}>
                    {selectedDrone === index ? 'ACTIVE' : 'STBY'}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: '#8a8d94' }}>
                  {drone.type} • {index % 3 === 0 ? 'Available' : index % 3 === 1 ? 'Mission' : 'Charging'}
                </div>
              </div>
            ))}
          </div>

          {/* Telemetry Panel */}
          <div style={{
            marginTop: '20px',
            padding: '16px',
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '8px',
            border: '1px solid #3a3d4a'
          }}>
            <h3 style={{ 
              fontSize: '12px', 
              fontWeight: '600', 
              marginBottom: '12px',
              color: '#4a90e2'
            }}>
              📊 {dronePositions[selectedDrone].id} Telemetry
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <TelemetryItem label="ALTITUDE" value={`${telemetry.altitude.toFixed(0)}m`} />
              <TelemetryItem label="SPEED" value={`${telemetry.speed.toFixed(1)}m/s`} />
              <TelemetryItem label="HEADING" value={`${getHeadingDirection(telemetry.heading)} ${telemetry.heading.toFixed(0)}°`} />
              <TelemetryItem label="BATTERY" value={`${telemetry.battery.toFixed(0)}%`} color={telemetry.battery < 30 ? '#c45a5a' : '#5a8a5a'} />
              <TelemetryItem label="SIGNAL" value={`${telemetry.signal.toFixed(0)}%`} />
              <TelemetryItem label="GPS" value="ACTIVE" color="#5a8a5a" />
            </div>
          </div>
        </aside>

        {/* Center - Video Feed */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* View Controls */}
          <div style={{
            padding: '12px 20px',
            background: 'rgba(0,0,0,0.3)',
            borderBottom: '1px solid #3a3d4a',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setActiveView('grid')}
                style={{
                  padding: '8px 16px',
                  background: activeView === 'grid' ? '#4a90e2' : 'rgba(255,255,255,0.1)',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Grid View (12)
              </button>
              <button
                onClick={() => setActiveView('single')}
                style={{
                  padding: '8px 16px',
                  background: activeView === 'single' ? '#4a90e2' : 'rgba(255,255,255,0.1)',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Single View
              </button>
            </div>

            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span style={{ fontSize: '11px', color: '#8a8d94' }}>
                {dronePositions[selectedDrone].id} LIVE
              </span>
              <button
                onClick={requestCameraPermission}
                style={{
                  padding: '6px 12px',
                  background: 'rgba(74, 144, 226, 0.2)',
                  border: '1px solid rgba(74, 144, 226, 0.4)',
                  borderRadius: '4px',
                  color: '#4a90e2',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                Reconnect
              </button>
            </div>
          </div>

          {/* Video Grid */}
          <div style={{
            flex: 1,
            padding: '16px',
            background: '#0a0b10',
            overflow: 'auto'
          }}>
            {error && (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: '#c45a5a'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>📷</div>
                <div style={{ fontSize: '16px', marginBottom: '8px' }}>{error}</div>
                <button
                  onClick={requestCameraPermission}
                  style={{
                    padding: '12px 24px',
                    background: '#4a90e2',
                    border: 'none',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '14px',
                    cursor: 'pointer',
                    marginTop: '16px'
                  }}
                >
                  Enable Camera Access
                </button>
              </div>
            )}

            {!error && (
              <div style={{
                display: activeView === 'grid' ? 'grid' : 'flex',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '12px',
                height: '100%'
              }}>
                {dronePositions.map((drone, index) => (
                  <div
                    key={drone.id}
                    style={{
                      position: 'relative',
                      background: '#1a1d29',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      border: selectedDrone === index 
                        ? '2px solid #4a90e2' 
                        : '1px solid #3a3d4a'
                    }}
                  >
                    {/* Video Feed */}
                    {selectedDrone === index ? (
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover'
                        }}
                      />
                    ) : (
                      <div style={{
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: 'linear-gradient(135deg, #1a1d29 0%, #232633 100%)'
                      }}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ 
                            fontSize: '24px', 
                            marginBottom: '8px',
                            opacity: 0.5
                          }}>
                            📷
                          </div>
                          <div style={{ fontSize: '10px', color: '#8a8d94' }}>
                            Mirroring DRONE-001
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Overlay Info */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      padding: '8px',
                      background: 'linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span style={{ 
                        fontSize: '10px', 
                        fontWeight: '700',
                        color: selectedDrone === index ? '#4a90e2' : '#8a8d94'
                      }}>
                        {drone.id}
                      </span>
                      <span style={{
                        fontSize: '9px',
                        padding: '2px 6px',
                        background: selectedDrone === index ? '#4a90e2' : 'rgba(0,0,0,0.5)',
                        borderRadius: '10px',
                        color: '#fff'
                      }}>
                        {selectedDrone === index ? 'LIVE' : 'MIRROR'}
                      </span>
                    </div>

                    {/* Recording Indicator */}
                    <div style={{
                      position: 'absolute',
                      bottom: '8px',
                      left: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '4px 8px',
                      background: 'rgba(0,0,0,0.7)',
                      borderRadius: '4px'
                    }}>
                      <span style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#ff4444',
                        animation: 'pulse 1s infinite'
                      }}></span>
                      <span style={{ fontSize: '9px', color: '#ff4444' }}>REC</span>
                    </div>

                    {/* Crosshair Overlay */}
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: '60%',
                      height: '60%',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '4px'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: '10px',
                        height: '10px',
                        border: '2px solid rgba(74, 144, 226, 0.8)',
                        borderRadius: '50%'
                      }}></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>

        {/* Right Sidebar - Mission Info */}
        <aside style={{
          width: '260px',
          background: 'linear-gradient(180deg, #1a1d29 0%, #151720 100%)',
          borderLeft: '1px solid #3a3d4a',
          padding: '16px',
          overflowY: 'auto'
        }}>
          {/* Mission Status */}
          <div style={{
            padding: '16px',
            background: 'rgba(90, 138, 90, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(90, 138, 90, 0.3)',
            marginBottom: '16px'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span style={{ fontWeight: '600', fontSize: '13px' }}>Mission Active</span>
            </div>
            <div style={{ fontSize: '11px', color: '#8a8d94' }}>
              Surveillance of Zone Alpha-7<br />
              Started: {new Date(Date.now() - 3600000).toLocaleTimeString()}
            </div>
          </div>

          {/* Safe Drone Count */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ 
              fontSize: '12px', 
              fontWeight: '600', 
              marginBottom: '10px',
              color: '#8a8d94',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              🚁 Zone Status
            </h3>
            <div style={{
              padding: '14px',
              background: 'rgba(0,0,0,0.3)',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ 
                fontSize: '32px', 
                fontWeight: '800',
                color: '#5a8a5a',
                marginBottom: '4px'
              }}>
                8<span style={{ fontSize: '16px', color: '#8a8d94' }}>/12</span>
              </div>
              <div style={{ fontSize: '11px', color: '#8a8d94' }}>
                Safe Drone Count
              </div>
              <div style={{ 
                fontSize: '10px', 
                color: '#d4a574',
                marginTop: '8px'
              }}>
                ⚠️ High wind - Limited deployment
              </div>
            </div>
          </div>

          {/* AI Prediction */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ 
              fontSize: '12px', 
              fontWeight: '600', 
              marginBottom: '10px',
              color: '#8a8d94',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              🤖 AI Prediction
            </h3>
            <div style={{
              padding: '12px',
              background: 'rgba(74, 144, 226, 0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(74, 144, 226, 0.2)'
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '11px', color: '#8a8d94' }}>Confidence</span>
                <span style={{ fontSize: '18px', fontWeight: '700', color: '#4a90e2' }}>94%</span>
              </div>
              <div style={{ fontSize: '10px', color: '#8a8d94' }}>
                Risk Trend: <span style={{ color: '#5a8a5a' }}>Stable ↓</span>
              </div>
            </div>
          </div>

          {/* GPS Fallback Status */}
          <div style={{
            padding: '12px',
            background: 'rgba(90, 138, 90, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(90, 138, 90, 0.2)'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '6px'
            }}>
              <span style={{ fontSize: '14px' }}>🛰️</span>
              <span style={{ fontSize: '12px', fontWeight: '600' }}>GPS Fallback</span>
            </div>
            <div style={{ fontSize: '10px', color: '#8a8d94' }}>
              Using NASA satellite weather estimation for position tracking
            </div>
          </div>
        </aside>
      </div>

      {/* Styles */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  )
}

// Telemetry Item Component
const TelemetryItem = ({ label, value, color = '#e8e9ea' }) => (
  <div>
    <div style={{ 
      fontSize: '9px', 
      color: '#8a8d94', 
      marginBottom: '2px',
      fontWeight: '600'
    }}>
      {label}
    </div>
    <div style={{ 
      fontSize: '13px', 
      fontWeight: '700',
      color: color
    }}>
      {value}
    </div>
  </div>
)

export default DroneView

