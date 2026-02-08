/**
 * PRALAYA-NET Demo API Configuration
 * Uses process.env.REACT_APP_API_URL with fallback to demo mode
 */

// Browser compatibility shim for process
if (typeof process === 'undefined') {
    window.process = { env: {} };
}

// Get API URL from environment with multiple fallbacks
const API_URL = process.env.REACT_APP_API_URL || 
                 import.meta.env.VITE_API_URL || 
                 import.meta.env.REACT_APP_API_URL || 
                 'http://127.0.0.1:8000';

// WebSocket URL (same as API but with ws protocol)
const WS_URL = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');

// Demo API endpoints - simplified for hackathon
export const API_ENDPOINTS = {
  // Health and System
  HEALTH: `${API_URL}/health`,
  API_HEALTH: `${API_URL}/api/health`,
  DEMO_STATUS: `${API_URL}/demo/status`,
  
  // Core functionality
  RISK_PREDICT: `${API_URL}/risk/predict`,
  API_RISK_PREDICT: `${API_URL}/api/risk/predict`,
  STABILITY_CURRENT: `${API_URL}/api/stability/current`,
  
  // Demo endpoints
  ALERTS_ACTIVE: `${API_URL}/api/alerts/active`,
  TIMELINE_EVENTS: `${API_URL}/api/timeline/events`,
  SYSTEM_STATUS: `${API_URL}/api/system/status`,
  
  // Documentation
  DOCS: `${API_URL}/docs`
};

// WebSocket endpoints
export const WS_ENDPOINTS = {
  GENERAL: `${WS_URL}/ws`,
  RISK_STREAM: `${WS_URL}/ws/risk-stream`,
  STABILITY_STREAM: `${WS_URL}/ws/stability-stream`,
  ACTIONS_STREAM: `${WS_URL}/ws/actions-stream`,
  TIMELINE_STREAM: `${WS_URL}/ws/timeline-stream`
};

// Configuration
export const CONFIG = {
  API_URL,
  WS_URL,
  RECONNECT_INTERVAL: 3000, // 3 seconds
  CONNECTION_TIMEOUT: 10000, // 10 seconds
  MAX_RECONNECT_ATTEMPTS: 5,
  UPDATE_INTERVAL: 5000, // 5 seconds for auto-refresh
  HEALTH_CHECK_INTERVAL: 5000, // 5 seconds
  DEMO_MODE: true // Always use demo mode for hackathon
};

// Export default API URL for backward compatibility
export default API_URL;
