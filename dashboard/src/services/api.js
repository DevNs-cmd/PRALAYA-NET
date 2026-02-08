/**
 * API Service for PRALAYA-NET Frontend
 * Robust backend communication with auto-reconnect and error handling
 * Enhanced with drone fleet operations
 */

import { API_BASE, WS_URL } from '../config/api'

console.log('[API Service] Initializing with base URL:', API_BASE)

// ============== Health Check ==============

export async function checkBackendHealth() {
  try {
    console.log('[API] Checking backend health...')
    const response = await fetch(`${API_BASE}/api/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000
    })
    
    if (response.ok) {
      console.log('[API] Backend is healthy')
      return true
    } else {
      console.error('[API] Backend health check failed:', response.status)
      return false
    }
  } catch (error) {
    console.error('[API] Backend unreachable:', error.message)
    return false
  }
}

// ============== Weather API ==============

export async function fetchWeather(lat, lon) {
  try {
    const url = `${API_BASE}/api/weather?lat=${lat}&lon=${lon}`
    console.log('[API] Fetching weather for:', lat, lon)
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Weather API failed: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[API] Weather data received')
    return data
  } catch (error) {
    console.error('[API] Weather fetch error:', error)
    throw error
  }
}

// ============== Geo-Intelligence API ==============

export async function fetchGeoIntel(lat, lon) {
  try {
    const url = `${API_BASE}/api/geo-intel?lat=${lat}&lon=${lon}`
    console.log('[API] Fetching geo-intel for:', lat, lon)
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Geo-intel API failed: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[API] Geo-intel data received, risk score:', data.risk_score)
    return data
  } catch (error) {
    console.error('[API] Geo-intel fetch error:', error)
    throw error
  }
}

// ============== Infrastructure API ==============

export async function fetchInfrastructure(lat, lon) {
  try {
    const url = lat && lon 
      ? `${API_BASE}/api/infrastructure?lat=${lat}&lon=${lon}`
      : `${API_BASE}/api/infrastructure`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Infrastructure API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Infrastructure fetch error:', error)
    throw error
  }
}

// ============== Risk Prediction API ==============

export async function fetchRiskPrediction(lat, lon) {
  try {
    const url = lat && lon
      ? `${API_BASE}/api/risk/predict?lat=${lat}&lon=${lon}`
      : `${API_BASE}/api/risk/predict`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Risk prediction API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Risk prediction error:', error)
    throw error
  }
}

// ============== System Status API ==============

export async function fetchSystemStatus() {
  try {
    const response = await fetch(`${API_BASE}/api/system-status`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`System status API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] System status error:', error)
    throw error
  }
}

// ============== Stability Index API ==============

export async function fetchStabilityIndex() {
  try {
    const response = await fetch(`${API_BASE}/api/stability/current`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Stability index API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Stability index error:', error)
    throw error
  }
}

// ============== Drone Fleet API ==============

/**
 * Get complete drone fleet status
 */
export async function getDroneStatus() {
  try {
    const response = await fetch(`${API_BASE}/api/drones/fleet-status`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Drone fleet status API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Drone status error:', error)
    throw error
  }
}

/**
 * Get safe drone count for deployment based on weather/risk
 */
export async function getSafeDroneCount(lat, lon, riskScore, apiKey = null) {
  try {
    const url = new URL(`${API_BASE}/api/drones/safe-count`)
    url.searchParams.append('lat', lat.toString())
    url.searchParams.append('lon', lon.toString())
    url.searchParams.append('risk_score', riskScore.toString())
    if (apiKey) {
      url.searchParams.append('openweather_key', apiKey)
    }
    
    console.log('[API] Fetching safe drone count for:', lat, lon)
    
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Safe drone count API failed: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[API] Safe drone count:', data.safe_drone_count)
    return data
  } catch (error) {
    console.error('[API] Safe drone count error:', error)
    throw error
  }
}

/**
 * Get comprehensive drone operations conditions
 */
export async function getDroneConditions(lat, lon) {
  try {
    const url = `${API_BASE}/api/drones/conditions/${lat}/${lon}`
    console.log('[API] Fetching drone conditions for:', lat, lon)
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Drone conditions API failed: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('[API] Drone conditions error:', error)
    throw error
  }
}

/**
 * Get drone position estimate (GPS fallback)
 */
export async function estimateDronePosition(lat, lon, weatherData = null) {
  try {
    const url = `${API_BASE}/api/drones/position-estimate`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        weather_data: weatherData || {}
      })
    })
    
    if (!response.ok) {
      throw new Error(`Position estimate API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Position estimate error:', error)
    throw error
  }
}

/**
 * Generate prediction with confidence scoring
 */
export async function generatePrediction(lat, lon, weather, historicalData = null) {
  try {
    const url = `${API_BASE}/api/drones/prediction`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        weather,
        historical_data: historicalData || {}
      })
    })
    
    if (!response.ok) {
      throw new Error(`Prediction API failed: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[API] Prediction generated with confidence:', data.prediction?.confidence)
    return data
  } catch (error) {
    console.error('[API] Prediction error:', error)
    throw error
  }
}

/**
 * Deploy a drone to a target location
 */
export async function deployDrone(droneId, targetLat, targetLon, missionType = 'surveillance', altitude = 100) {
  try {
    const url = `${API_BASE}/api/drones/deploy`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        drone_id: droneId,
        target_lat: targetLat,
        target_lon: targetLon,
        mission_type: missionType,
        altitude
      })
    })
    
    if (!response.ok) {
      throw new Error(`Deploy drone API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Deploy drone error:', error)
    throw error
  }
}

/**
 * Recall a drone to base
 */
export async function recallDrone(droneId) {
  try {
    const url = `${API_BASE}/api/drones/recall?drone_id=${droneId}`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Recall drone API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Recall drone error:', error)
    throw error
  }
}

/**
 * Get specific drone status
 */
export async function getSingleDroneStatus(droneId) {
  try {
    const response = await fetch(`${API_BASE}/api/drones/${droneId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Drone status API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Single drone status error:', error)
    throw error
  }
}

/**
 * Get available drone types
 */
export async function getDroneTypes() {
  try {
    const response = await fetch(`${API_BASE}/api/drones/types`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      throw new Error(`Drone types API failed: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('[API] Drone types error:', error)
    throw error
  }
}

// ============== WebSocket Connection ==============

export function connectWebSocket(onMessage, onError, onClose) {
  console.log('[WS] Connecting to:', WS_URL)
  
  const socket = new WebSocket(WS_URL)
  
  socket.onopen = () => {
    console.log('[WS] ✅ Connected to real-time stream')
  }
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (err) {
      console.error('[WS] ❌ Error parsing message:', err)
    }
  }
  
  socket.onerror = (error) => {
    console.error('[WS] ❌ Connection error:', error)
    if (onError) onError(error)
  }
  
  socket.onclose = (event) => {
    console.warn('[WS] ❌ Connection closed:', event.code, event.reason)
    if (onClose) onClose(event)
    
    // Auto-reconnect after 5 seconds
    console.log('[WS] Reconnecting in 5 seconds...')
    setTimeout(() => {
      connectWebSocket(onMessage, onError, onClose)
    }, 5000)
  }
  
  return socket
}

// ============== Helper Functions ==============

/**
 * API call with retry logic
 */
export async function apiCallWithRetry(url, options = {}, retries = 3) {
  let lastError
  
  for (let i = 0; i < retries; i++) {
    try {
      if (i > 0) {
        console.log(`[API] Retry attempt ${i}/${retries} for ${url}`)
      }
      
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (error) {
      lastError = error
      
      if (i < retries - 1) {
        const backoff = Math.pow(2, i) * 1000
        await new Promise(resolve => setTimeout(resolve, backoff))
      }
    }
  }
  
  console.error(`[API] ❌ All ${retries} attempts failed for: ${url}`)
  throw lastError
}

// Export API_BASE for use in components
export { API_BASE }

