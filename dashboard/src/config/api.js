/**
 * API Configuration for PRALAYA-NET Frontend
 * Robust environment variable detection for development and production
 */

// Environment variable detection priority order:
const ENV_PRIORITY = [
  // Vercel/Netlify production
  'NEXT_PUBLIC_API_URL',
  // Vite environment
  'VITE_API_URL',
  // React environment (for CRA compatibility)
  'REACT_APP_API_URL',
  // Legacy Vite
  'VITE_REACT_APP_API_URL',
  // Window fallback
  'VITE_API_URL'
]

// Get the best available API URL
function getApiUrl() {
  // Check environment variables
  for (const key of ENV_PRIORITY) {
    const value = import.meta.env[key]
    if (value && typeof value === 'string' && value.trim()) {
      console.log(`[API] Using ${key}: ${value}`)
      return value.trim()
    }
  }
  
  // Check window object (for inline script configuration)
  if (typeof window !== 'undefined') {
    const windowUrl = window.NEXT_PUBLIC_API_URL || window.VITE_API_URL || window.REACT_APP_API_URL
    if (windowUrl) {
      console.log(`[API] Using window config: ${windowUrl}`)
      return windowUrl
    }
  }
  
  // Default fallback
  const defaultUrl = 'http://127.0.0.1:8000'
  console.log(`[API] Using default URL: ${defaultUrl}`)
  return defaultUrl
}

// Build WebSocket URL from API URL
function getWsUrl() {
  const apiUrl = getApiUrl()
  return apiUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
}

export const API_BASE = getApiUrl()
export const WS_URL = getWsUrl()

// API Endpoints configuration
export const API_ENDPOINTS = {
  health: `${API_BASE}/api/health`,
  weather: `${API_BASE}/api/weather`,
  geoIntel: `${API_BASE}/api/geo-intel`,
  infrastructure: `${API_BASE}/api/infrastructure`,
  riskPrediction: `${API_BASE}/api/risk/predict`,
  systemStatus: `${API_BASE}/api/system-status`,
  stabilityIndex: `${API_BASE}/api/stability/current`,
  droneStatus: `${API_BASE}/api/drones/fleet-status`,
  droneSafeCount: `${API_BASE}/api/drones/safe-count`,
  droneConditions: `${API_BASE}/api/drones/conditions`,
  dronePositionEstimate: `${API_BASE}/api/drones/position-estimate`,
  dronePrediction: `${API_BASE}/api/drones/prediction`,
  droneDeploy: `${API_BASE}/api/drones/deploy`,
  droneRecall: `${API_BASE}/api/drones/recall`,
  droneTypes: `${API_BASE}/api/drones/types`,
  disasterTrigger: `${API_BASE}/api/disaster/trigger`,
  disasterClear: `${API_BASE}/api/disaster/clear`
}

// WebSocket Endpoints
export const WS_ENDPOINTS = {
  realtime: WS_URL
}

// Configuration object
export const CONFIG = {
  apiBase: API_BASE,
  wsUrl: WS_URL,
  mode: import.meta.env.MODE || 'development',
  debug: import.meta.env.DEV || false
}

// Log configuration on load
console.log('═'.repeat(50))
console.log('[API] PRALAYA-NET Frontend Configuration')
console.log('═'.repeat(50))
console.log(`[API] Mode: ${CONFIG.mode}`)
console.log(`[API] API Base URL: ${API_BASE}`)
console.log(`[API] WebSocket URL: ${WS_URL}`)
console.log('═'.repeat(50))

// Export for use in other modules
export default API_BASE

