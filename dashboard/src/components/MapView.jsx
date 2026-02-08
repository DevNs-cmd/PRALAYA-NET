import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents } from 'react-leaflet'
import { fetchGeoIntel, fetchInfrastructureLayer } from '../services/geoIntelligenceService'
import RiskPopup from './RiskPopup'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix for default marker icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const MapView = ({ apiUrl = 'http://127.0.0.1:8000' }) => {
  const [zones, setZones] = useState([])
  const [infrastructure, setInfrastructure] = useState([])
  const [center] = useState([28.6139, 77.2090]) // Delhi, India
  const [activePopup, setActivePopup] = useState(null)
  const [showIntelLayer, setShowIntelLayer] = useState(false)
  const [intelMarkers, setIntelMarkers] = useState([])
  const [mapReady, setMapReady] = useState(false)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('live') // 'live' or 'demo'
  const [backendReachable, setBackendReachable] = useState(true)
  const mapRef = useRef(null)

  // Map click handler
  const MapEvents = () => {
    useMapEvents({
      async click(e) {
        const { lat, lng } = e.latlng
        console.log('[MapView] Map clicked at:', lat, lng)
        setActivePopup({
          lat,
          lon: lng,
          source: 'map_click'
        })
      },
      load() {
        setMapReady(true)
        console.log('[MapView] Map loaded')
      }
    })
    return null
  }

  // Fetch disaster zones
  const fetchZones = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/satellite/zones`)
      if (response.ok) {
        const data = await response.json()
        setZones(data.zones || [])
      }
    } catch (error) {
      console.error('[MapView] Error fetching zones:', error)
      // Use simulated zones
      setZones([
        { id: 'zone_1', type: 'flood', location: { lat: 28.65, lon: 77.25 }, radius: 3000, severity: 0.6 },
        { id: 'zone_2', type: 'fire', location: { lat: 28.58, lon: 77.15 }, radius: 2000, severity: 0.4 }
      ])
    }
  }

  // Fetch infrastructure
  const fetchInfra = async () => {
    try {
      const data = await fetchInfrastructure(center[0], center[1])
      setInfrastructure(data.facilities || [])
    } catch (error) {
      console.error('[MapView] Error fetching infrastructure:', error)
      // Only use simulated data if backend is unreachable
      if (!backendReachable) {
        console.warn('[MapView] Backend unreachable, using simulated infrastructure data')
        setInfrastructure([
          { id: 'infra_1', name: 'Power Grid Station A', lat: 28.6139, lon: 77.2090, type: 'power', risk: 0.3 },
          { id: 'infra_2', name: 'City Hospital', lat: 28.7041, lon: 77.1025, type: 'healthcare', risk: 0.5 },
          { id: 'infra_3', name: 'Water Treatment Plant', lat: 28.5355, lon: 77.3910, type: 'water', risk: 0.2 }
        ])
      }
    }
  }

  // Fetch intel layer when enabled
  const fetchIntel = async () => {
    if (!showIntelLayer) {
      setIntelMarkers([])
      return
    }
    
    try {
      const data = await fetchGeoIntel(center[0], center[1])
      if (data.infrastructure) {
        setIntelMarkers(data.infrastructure)
      }
    } catch (error) {
      console.error('[MapView] Error fetching intel:', error)
    }
  }

  // Initial data fetch
  useEffect(() => {
    const loadData = async () => {
      // Only show loading for initial fetch
      if (zones.length === 0 && infrastructure.length === 0) {
        setLoading(true)
        await Promise.all([fetchZones(), fetchInfra()])
        setLoading(false)
      }
    }
    
    loadData()
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchZones()
      if (showIntelLayer) fetchIntel()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [center, showIntelLayer, zones.length, infrastructure.length])

  // Fetch intel when toggle changes
  useEffect(() => {
    fetchIntel()
  }, [showIntelLayer, center])

  // Get disaster color
  const getDisasterColor = (type) => {
    const colors = {
      flood: '#4a90e2',
      fire: '#c45a5a',
      earthquake: '#d4a574',
      cyclone: '#8b7fa8',
      landslide: '#8a6f5a'
    }
    return colors[type] || '#6b7280'
  }

  // Get risk color
  const getRiskColor = (risk) => {
    if (risk >= 0.8) return '#c45a5a'
    if (risk >= 0.6) return '#d4a574'
    if (risk >= 0.3) return '#d4be74'
    return '#5a8a5a'
  }

  return (
    <div className="map-container" style={{
      position: 'relative',
      height: '100%',
      width: '100%',
      background: '#f0f0f0' // Light background to prevent black interface if map fails to load
    }}>
      {/* Map Header */}
      <div className="map-header" style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 999,
        background: 'linear-gradient(180deg, rgba(26, 29, 41, 0.95) 0%, rgba(26, 29, 41, 0) 100%)',
        padding: '16px 20px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        pointerEvents: 'none'
      }}>
        <h2 className="map-title" style={{
          fontSize: '18px',
          fontWeight: '700',
          color: '#e8e9ea',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          pointerEvents: 'auto'
        }}>
          🗺️ Geospatial Command Map
        </h2>

        <div style={{
          display: 'flex',
          gap: '12px',
          pointerEvents: 'auto'
        }}>
      {/* Backend Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '25px',
            border: '1px solid #3a3d4a'
          }}>
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: backendReachable ? '#5a8a5a' : '#c45a5a',
              animation: backendReachable ? 'pulse 2s infinite' : 'none'
            }}></span>
            <span style={{
              fontSize: '12px',
              fontWeight: '600',
              color: backendReachable ? '#5a8a5a' : '#c45a5a'
            }}>
              {backendReachable ? 'LIVE' : 'BACKEND OFFLINE'}
            </span>
          </div>
        </div>
      </div>

      {/* Intel Toggle - Minimal Version */}
      <div className="infrastructure-toggle" style={{
        position: 'absolute',
        top: '80px',
        left: '12px',
        zIndex: 999,
        background: 'rgba(26, 29, 41, 0.6)',
        borderRadius: '8px',
        padding: '8px 12px',
        border: '1px solid rgba(74, 144, 226, 0.3)',
        pointerEvents: 'auto',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)'
      }}>
        <label className="toggle-label" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer'
        }}>
          <input
            type="checkbox"
            checked={showIntelLayer}
            onChange={(e) => setShowIntelLayer(e.target.checked)}
            style={{
              width: '16px',
              height: '16px',
              cursor: 'pointer',
              accentColor: '#4a90e2'
            }}
          />
          <span style={{
            fontSize: '12px',
            fontWeight: '500',
            color: '#e8e9ea'
          }}>
            Intel Layer
          </span>
        </label>
      </div>

      {/* Map Container */}
      <MapContainer
        ref={mapRef}
        center={center}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        whenReady={() => {
          setMapReady(true)
          setLoading(false)
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          eventHandlers={{
            tileerror: () => {
              console.warn('[MapView] Tile loading error - map may appear with missing tiles')
            }
          }}
        />

        <MapEvents />

        {/* Click Popup - Shows Geo-Intel */}
        {activePopup && (
          <Popup
            position={[activePopup.lat, activePopup.lon]}
            onClose={() => setActivePopup(null)}
            maxWidth={350}
            closeButton={true}
          >
            <RiskPopup
              lat={activePopup.lat}
              lon={activePopup.lon}
              onClose={() => setActivePopup(null)}
            />
          </Popup>
        )}

        {/* Disaster Zones */}
        {zones.map((zone) => (
          <Circle
            key={zone.id}
            center={[zone.location?.lat || center[0], zone.location?.lon || center[1]]}
            radius={zone.radius || 2000}
            pathOptions={{
              color: getDisasterColor(zone.type),
              fillColor: getDisasterColor(zone.type),
              fillOpacity: 0.2,
              weight: 2,
              dashArray: '5, 10'
            }}
          >
            <Popup>
              <div style={{ 
                fontSize: '12px', 
                fontFamily: 'Inter, sans-serif',
                padding: '8px'
              }}>
                <strong style={{ color: getDisasterColor(zone.type) }}>
                  ⚠️ {zone.type?.toUpperCase()} ALERT
                </strong>
                <br />
                <span style={{ color: '#666', fontSize: '11px' }}>
                  Severity: {(zone.severity * 100).toFixed(0)}%
                </span>
                <br />
                <span style={{ color: '#888', fontSize: '10px' }}>
                  Radius: {(zone.radius / 1000).toFixed(1)} km
                </span>
              </div>
            </Popup>
          </Circle>
        ))}

        {/* Infrastructure Nodes */}
        {infrastructure.map((node) => (
          <Marker
            key={node.id}
            position={[node.lat, node.lon]}
            icon={L.divIcon({
              className: 'infrastructure-marker',
              html: `<div style="
                background-color: ${getRiskColor(node.risk || 0.3)};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 3px solid #1a1d29;
                box-shadow: 0 0 8px rgba(0,0,0,0.5), 0 0 15px ${getRiskColor(node.risk || 0.3)}40;
              "></div>`,
              iconSize: [20, 20]
            })}
          >
            <Popup>
              <div style={{ 
                fontSize: '12px', 
                fontFamily: 'Inter, sans-serif',
                padding: '8px'
              }}>
                <strong style={{ color: '#e8e9ea' }}>{node.name}</strong>
                <br />
                <span style={{ color: '#888' }}>Type: {node.type}</span>
                <br />
                <span style={{ 
                  color: getRiskColor(node.risk || 0.3), 
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  fontSize: '11px'
                }}>
                  Risk: {((node.risk || 0.3) * 100).toFixed(0)}%
                </span>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Intel Layer Markers */}
        {intelMarkers.map((marker) => (
          <Marker
            key={marker.id}
            position={[marker.lat, marker.lon]}
            icon={L.divIcon({
              className: 'intel-marker',
              html: `<div style="
                background: #5a7aa5;
                width: 14px;
                height: 14px;
                transform: rotate(45deg);
                border: 2px solid #1a1d29;
                box-shadow: 0 0 6px rgba(90, 122, 165, 0.5);
              "></div>`,
              iconSize: [14, 14]
            })}
          >
            <Popup>
              <div style={{ fontSize: '11px', fontWeight: 'bold' }}>
                INTEL: {marker.name}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Center Marker - Command Center */}
        <Marker position={center} icon={L.divIcon({
          className: 'center-marker',
          html: `<div style="
            background: linear-gradient(135deg, #4a90e2, #c45a5a);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid #1a1d29;
            box-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
          ">🏛️</div>`,
          iconSize: [24, 24]
        })}>
          <Popup>
            <div style={{ 
              fontSize: '12px', 
              textAlign: 'center',
              fontFamily: 'Inter, sans-serif',
              padding: '8px'
            }}>
              <strong style={{ color: '#4a90e2' }}>📍 Command Center</strong>
              <br />
              <span style={{ color: '#666' }}>Delhi, India</span>
              <br />
              <span style={{ fontSize: '10px', color: '#4a90e2' }}>
                🖱️ Click anywhere for geo-intel
              </span>
            </div>
          </Popup>
        </Marker>
      </MapContainer>

      {/* Loading Indicator - Minimal */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          zIndex: 1000,
          background: 'rgba(26, 29, 41, 0.8)',
          borderRadius: '20px',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{
            width: '16px',
            height: '16px',
            border: '2px solid rgba(74, 144, 226, 0.3)',
            borderTopColor: '#4a90e2',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          <span style={{ 
            color: '#e8e9ea', 
            fontSize: '12px',
            fontWeight: '500'
          }}>
            Loading...
          </span>
        </div>
      )}

      {/* Risk Legend - Moved to top right corner */}
      <div style={{
        position: 'absolute',
        top: '80px',
        right: '12px',
        zIndex: 1000,
        background: 'rgba(26, 29, 41, 0.95)',
        border: '1px solid #3a3d4a',
        padding: '12px 16px',
        borderRadius: '8px',
        fontSize: '11px',
        color: '#b4b6ba',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        maxWidth: '180px'
      }}>
        <div style={{ 
          fontWeight: '600', 
          color: '#e8e9ea', 
          marginBottom: '8px',
          fontSize: '12px'
        }}>
          📊 Risk Levels
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <LegendItem color="#5a8a5a" label="Low (0-30%)" />
          <LegendItem color="#d4be74" label="Moderate (30-50%)" />
          <LegendItem color="#d4a574" label="Elevated (50-70%)" />
          <LegendItem color="#c45a5a" label="Critical (70%+)" />
        </div>
      </div>

      {/* Coordinates Display */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        background: 'rgba(0, 0, 0, 0.6)',
        borderRadius: '4px',
        padding: '6px 12px',
        fontSize: '11px',
        color: '#8a8d94',
        fontFamily: 'monospace'
      }}>
        Center: {center[0].toFixed(4)}°N, {center[1].toFixed(4)}°E
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .leaflet-container {
          background: #1a1d29;
        }
        .leaflet-popup-content-wrapper {
          background: transparent;
          box-shadow: none;
        }
        .leaflet-popup-content {
          margin: 0;
        }
      `}</style>
    </div>
  )
}

// Legend Item Component
const LegendItem = ({ color, label }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
    <span style={{
      width: '14px',
      height: '14px',
      borderRadius: '50%',
      background: color,
      border: '2px solid #1a1d29',
      boxShadow: `0 0 6px ${color}60`
    }}></span>
    <span>{label}</span>
  </div>
)

export default MapView

