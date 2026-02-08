import { useState, useEffect } from 'react'
import { fetchGeoIntel, fetchSafeDroneCount, fetchPrediction } from '../services/geoIntelligenceService'

const RiskPopup = ({ lat, lon, onClose }) => {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [safeDroneCount, setSafeDroneCount] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const getIntelligence = async () => {
      setLoading(true)
      try {
        console.log('[RiskPopup] Fetching geo-intel for:', lat, lon)
        
        // Fetch geo-intel (includes weather, risk, infrastructure)
        const geoData = await fetchGeoIntel(lat, lon)
        setData(geoData)
        
        // Fetch safe drone count using risk score
        const droneData = await fetchSafeDroneCount(lat, lon, geoData.risk_score)
        setSafeDroneCount(droneData)
        
        // Fetch prediction
        const predData = await fetchPrediction(lat, lon, geoData.weather)
        setPrediction(predData)
        
        setError(null)
      } catch (err) {
        console.error('[RiskPopup] Error:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (lat && lon) {
      getIntelligence()
    }
  }, [lat, lon])

  // Calculate high risk indicator
  const isHighRisk = data?.risk_score >= 70 || data?.risk_level === 'critical'

  const getBadgeColor = (score, level) => {
    if (level === 'critical' || score >= 80) return 'red'
    if (level === 'high' || score >= 60) return 'orange'
    if (level === 'elevated' || score >= 40) return 'yellow'
    return 'green'
  }

  const badgeColor = data ? getBadgeColor(data.risk_score, data.risk_level) : 'green'

  if (loading) {
    return (
      <div className="risk-popup-loading" style={{ 
        padding: '30px', 
        textAlign: 'center',
        minWidth: '280px',
        background: 'linear-gradient(180deg, #1a1d29 0%, #232633 100%)',
        borderRadius: '8px'
      }}>
        <div className="spinner" style={{
          width: '36px',
          height: '36px',
          border: '3px solid rgba(74, 144, 226, 0.2)',
          borderTopColor: '#4a90e2',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 15px'
        }}></div>
        <div style={{ color: '#e8e9ea', fontSize: '13px', marginBottom: '8px' }}>
          Analyzing Geo-Intelligence...
        </div>
        <div style={{ color: '#8a8d94', fontSize: '10px' }}>
          Fetching weather, risk, and drone conditions
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="risk-popup-error" style={{ 
        padding: '24px', 
        textAlign: 'center',
        minWidth: '240px',
        background: 'linear-gradient(180deg, #1a1d29 0%, #232633 100%)',
        borderRadius: '8px'
      }}>
        <div style={{ fontSize: '28px', marginBottom: '12px' }}>⚠️</div>
        <div style={{ fontSize: '13px', color: '#c45a5a', marginBottom: '6px' }}>Service Unavailable</div>
        <div style={{ fontSize: '10px', color: '#8a8d94' }}>
          Using demo data
        </div>
      </div>
    )
  }

  const weather = data.weather || {}
  const nasa = data.nasa_data || {}

  return (
    <div className="intel-card" style={{ 
      minWidth: '300px',
      maxWidth: '340px',
      background: 'linear-gradient(180deg, #1a1d29 0%, #232633 100%)',
      borderRadius: '8px',
      padding: '16px',
      color: '#e8e9ea',
      fontFamily: 'Inter, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '14px', borderBottom: '1px solid #3a3d4a', paddingBottom: '10px' }}>
        <div style={{ fontSize: '14px', fontWeight: '700', marginBottom: '2px', color: '#fff' }}>
          🌍 Geo-Intelligence Report
        </div>
        <div style={{ fontSize: '10px', color: '#8a8d94' }}>
          {data.coordinates?.lat?.toFixed(4)}°N, {Math.abs(data.coordinates?.lon?.toFixed(4))}°E
        </div>
      </div>

      {/* Risk Badge */}
      <div className={`intel-badge ${badgeColor}`} style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '6px 12px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: '700',
        background: badgeColor === 'red' ? 'rgba(196, 90, 90, 0.2)' :
                    badgeColor === 'orange' ? 'rgba(212, 165, 116, 0.2)' :
                    badgeColor === 'yellow' ? 'rgba(212, 190, 116, 0.2)' :
                    'rgba(90, 138, 90, 0.2)',
        color: badgeColor === 'red' ? '#c45a5a' :
               badgeColor === 'orange' ? '#d4a574' :
               badgeColor === 'yellow' ? '#d4be74' :
               '#5a8a5a',
        border: `1px solid ${badgeColor === 'red' ? 'rgba(196, 90, 90, 0.3)' :
                              badgeColor === 'orange' ? 'rgba(212, 165, 116, 0.3)' :
                              badgeColor === 'yellow' ? 'rgba(212, 190, 116, 0.3)' :
                              'rgba(90, 138, 90, 0.3)'}`,
        marginBottom: '14px'
      }}>
        🚨 AI RISK: {data.risk_level.toUpperCase()} ({data.risk_score}%)
      </div>

      {/* Safe Drone Count Section */}
      {safeDroneCount && (
        <div style={{ 
          marginBottom: '14px',
          padding: '12px',
          background: 'rgba(0, 0, 0, 0.2)',
          borderRadius: '6px',
          border: '1px solid #3a3d4a'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '12px', fontWeight: '600', color: '#8a8d94' }}>
              🚁 Safe Drone Count
            </span>
            <span style={{ 
              fontSize: '20px', 
              fontWeight: '800',
              color: safeDroneCount.safe_drone_count === 0 ? '#c45a5a' :
                     safeDroneCount.safe_drone_count < 6 ? '#d4a574' :
                     '#5a8a5a'
            }}>
              {safeDroneCount.safe_drone_count}<span style={{ fontSize: '12px', color: '#8a8d94' }}>/{safeDroneCount.max_drones}</span>
            </span>
          </div>
          
          {/* Deployment Progress Bar */}
          <div style={{
            width: '100%',
            height: '6px',
            background: '#3a3d4a',
            borderRadius: '3px',
            overflow: 'hidden',
            marginBottom: '8px'
          }}>
            <div style={{
              width: `${safeDroneCount.deployment_ratio * 100}%`,
              height: '100%',
              background: safeDroneCount.safe_drone_count === 0 ? '#c45a5a' :
                         safeDroneCount.safe_drone_count < 6 ? '#d4a574' :
                         '#5a8a5a',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
          
          {/* Conditions Summary */}
          <div style={{ display: 'flex', gap: '8px', fontSize: '9px', color: '#8a8d94' }}>
            <span title="Wind">💨 {safeDroneCount.conditions?.wind_speed_kmh} km/h</span>
            <span title="Precipitation">🌧️ {safeDroneCount.conditions?.precipitation_mm} mm</span>
            <span title="Temperature">🌡️ {safeDroneCount.conditions?.temperature_c}°C</span>
          </div>
        </div>
      )}

      {/* Weather Section */}
      <div className="intel-section" style={{ marginBottom: '14px' }}>
        <div className="section-label" style={{ 
          fontSize: '10px', 
          fontWeight: '600', 
          color: '#4a90e2',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '8px'
        }}>
          ☁️ Atmospheric Intelligence
        </div>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gap: '8px'
        }}>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(0,0,0,0.15)', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>
              {weather.main?.temp?.toFixed(1) || '--'}°C
            </div>
            <div style={{ fontSize: '9px', color: '#8a8d94' }}>Temperature</div>
          </div>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(0,0,0,0.15)', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>
              {(weather.wind?.speed * 3.6).toFixed(1) || '--'}
            </div>
            <div style={{ fontSize: '9px', color: '#8a8d94' }}>Wind (km/h)</div>
          </div>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(0,0,0,0.15)', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>
              {weather.main?.humidity || '--'}%
            </div>
            <div style={{ fontSize: '9px', color: '#8a8d94' }}>Humidity</div>
          </div>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(0,0,0,0.15)', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '10px', fontWeight: '600', color: '#fff', textTransform: 'capitalize' }}>
              {weather.weather?.[0]?.description || '--'}
            </div>
            <div style={{ fontSize: '9px', color: '#8a8d94' }}>Condition</div>
          </div>
        </div>
      </div>

      {/* NASA Section */}
      {nasa && (nasa.temperature || nasa.precipitation) && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ 
            fontSize: '10px', 
            fontWeight: '600', 
            color: '#8b7fa8',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px'
          }}>
            🛰️ NASA Environmental
          </div>
          <div style={{ display: 'flex', gap: '10px', fontSize: '11px' }}>
            <div style={{ 
              flex: 1, 
              padding: '8px', 
              background: 'rgba(0,0,0,0.15)', 
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontWeight: '600', color: '#fff' }}>{nasa.temperature?.toFixed(1) || '--'}°C</div>
              <div style={{ fontSize: '8px', color: '#8a8d94' }}>SFC Temp</div>
            </div>
            <div style={{ 
              flex: 1, 
              padding: '8px', 
              background: 'rgba(0,0,0,0.15)', 
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontWeight: '600', color: '#fff' }}>{nasa.precipitation?.toFixed(2) || '--'} mm</div>
              <div style={{ fontSize: '8px', color: '#8a8d94' }}>Precipitation</div>
            </div>
          </div>
        </div>
      )}

      {/* Prediction Confidence */}
      {prediction && (
        <div style={{ 
          marginBottom: '14px',
          padding: '10px',
          background: 'rgba(90, 138, 90, 0.1)',
          borderRadius: '6px',
          border: '1px solid rgba(90, 138, 90, 0.2)'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '6px'
          }}>
            <span style={{ fontSize: '10px', fontWeight: '600', color: '#5a8a5a', textTransform: 'uppercase' }}>
              📈 Prediction Model
            </span>
            <span style={{ 
              fontSize: '14px', 
              fontWeight: '700',
              color: '#5a8a5a'
            }}>
              {(prediction.prediction?.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div style={{ fontSize: '10px', color: '#8a8d94' }}>
            Trend: <span style={{ 
              color: prediction.prediction?.trend === 'escalating' ? '#c45a5a' :
                     prediction.prediction?.trend === 'fluctuating' ? '#d4a574' :
                     '#5a8a5a',
              fontWeight: '600'
            }}>
              {prediction.prediction?.trend?.toUpperCase()}
            </span>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {safeDroneCount && safeDroneCount.recommendations && safeDroneCount.recommendations.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ 
            fontSize: '10px', 
            fontWeight: '600', 
            color: '#8a8d94',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '6px'
          }}>
            💡 Recommendations
          </div>
          {safeDroneCount.recommendations.slice(0, 2).map((rec, idx) => (
            <div key={idx} style={{
              padding: '6px 8px',
              background: rec.type === 'critical' ? 'rgba(196, 90, 90, 0.1)' :
                         rec.type === 'warning' ? 'rgba(212, 165, 116, 0.1)' :
                         'rgba(90, 138, 90, 0.1)',
              borderRadius: '4px',
              borderLeft: `3px solid ${rec.type === 'critical' ? '#c45a5a' :
                                    rec.type === 'warning' ? '#d4a574' :
                                    '#5a8a5a'}`,
              marginBottom: '4px',
              fontSize: '10px',
              color: '#b4b6ba'
            }}>
              {rec.message}
            </div>
          ))}
        </div>
      )}

      {/* Infrastructure */}
      {data.infrastructure && data.infrastructure.length > 0 && (
        <div style={{ 
          marginBottom: '12px',
          padding: '10px',
          background: 'rgba(0,0,0,0.15)',
          borderRadius: '6px'
        }}>
          <div style={{ 
            fontSize: '10px', 
            fontWeight: '600', 
            color: '#8a8d94',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '6px'
          }}>
            🏛️ Nearby Infrastructure
          </div>
          {data.infrastructure.slice(0, 3).map((facility) => (
            <div key={facility.id} style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              padding: '4px 0',
              fontSize: '10px',
              borderBottom: '1px solid rgba(255,255,255,0.05)'
            }}>
              <span style={{ color: '#e8e9ea' }}>{facility.name}</span>
              <span style={{ color: '#8a8d94' }}>{facility.distance_km} km</span>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div style={{ 
        paddingTop: '10px', 
        borderTop: '1px solid #3a3d4a',
        fontSize: '8px',
        color: '#6b7280',
        textAlign: 'right',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ color: '#8a8d94' }}>
          {safeDroneCount?.data_sources?.weather === 'simulated' ? '📡 Demo Mode' : '📡 Live Data'}
        </span>
        <span>
          {new Date(data.timestamp).toLocaleTimeString()}
        </span>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default RiskPopup

