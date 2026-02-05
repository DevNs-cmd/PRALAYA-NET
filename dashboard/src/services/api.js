// dashboard/src/services/api.js

// Backend URL configuration - supports both development and production
const getBackendUrl = () => {
  // Try environment variable first
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    console.log("[API] Using VITE_API_URL:", envUrl);
    return envUrl;
  }

  // Try React App variable (for compatibility)
  const reactEnvUrl = window.REACT_APP_API_URL;
  if (reactEnvUrl) {
    console.log("[API] Using REACT_APP_API_URL:", reactEnvUrl);
    return reactEnvUrl;
  }

  // Default to localhost for development
  const defaultUrl = "http://127.0.0.1:8000";
  console.log("[API] Using default backend URL:", defaultUrl);
  return defaultUrl;
};

export const API_BASE = getBackendUrl();
export const WS_URL = API_BASE.replace(/^http/, "ws") + "/ws";
console.log("[API] Backend base URL:", API_BASE);
console.log("[API] WebSocket URL:", WS_URL);

/**
 * Initialize WebSocket connection with auto-reconnect logic
 */
export function connectWebSocket(onMessage, retryCount = 0) {
  const socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("[WS] ✅ Connected to Real-time Stream");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (err) {
      console.error("[WS] ❌ Error parsing socket message:", err);
    }
  };

  socket.onclose = () => {
    console.warn("[WS] ❌ Connection died. Retrying in 5s...");
    setTimeout(() => connectWebSocket(onMessage, retryCount + 1), 5000);
  };

  return socket;
}

// Backend health status cache
let backendHealthy = null;
let lastHealthCheck = 0;
const HEALTH_CHECK_INTERVAL = 30000; // Check every 30 seconds

/**
 * Check if backend is healthy
 * @returns {Promise<boolean>}
 */
export async function checkBackendHealth() {
  const now = Date.now();

  // Return cached result if recent
  if (lastHealthCheck && now - lastHealthCheck < HEALTH_CHECK_INTERVAL && backendHealthy !== null) {
    return backendHealthy;
  }

  try {
    console.log("[API] Checking backend health...");
    const response = await fetch(`${API_BASE}/api/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      timeout: 5000,
    });

    backendHealthy = response.ok;
    lastHealthCheck = now;

    if (backendHealthy) {
      console.log("[API] ✅ Backend is healthy");
    } else {
      console.error("[API] ❌ Backend health check failed:", response.status);
    }

    return backendHealthy;
  } catch (error) {
    console.error("[API] ❌ Backend unreachable:", error.message);
    backendHealthy = false;
    lastHealthCheck = now;
    return false;
  }
}

// Helper function for API calls with error handling and retries
async function apiCall(url, options = {}, retries = 3) {
  let lastError;

  for (let i = 0; i < retries; i++) {
    try {
      if (i > 0) console.log(`[API] Retry attempt ${i}/${retries} for ${url}`);

      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: response.statusText }));
        throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (i > 0) console.log(`[API] ✅ Connected on attempt ${i + 1}`);
      return data;
    } catch (error) {
      lastError = error;
      console.warn(`[API] ⚠️ Attempt ${i + 1} failed: ${error.message}`);

      // Don't wait on the last attempt
      if (i < retries - 1) {
        const backoff = Math.pow(2, i) * 1000;
        await new Promise(resolve => setTimeout(resolve, backoff));
      }
    }
  }

  console.error(`[API] ❌ All ${retries} attempts failed for: ${url}`);
  throw lastError;
}

// Trigger disaster
export async function triggerDisaster(disasterType, severity = 0.7, location = null) {
  return apiCall(`${API_BASE}/api/trigger/disaster`, {
    method: "POST",
    body: JSON.stringify({
      disaster_type: disasterType,
      severity: severity,
      location: location,
    }),
  });
}

// Get satellite zones
export async function fetchDisasterZones() {
  return apiCall(`${API_BASE}/api/satellite/zones`);
}

// Get cascading risk graph
export async function getRiskGraph() {
  return apiCall(`${API_BASE}/api/trigger/status`);
}

// Get drone status
export async function getDroneStatus() {
  return apiCall(`${API_BASE}/api/drones/status`);
}

// Get drone telemetry
export async function getDroneTelemetry(droneId) {
  return apiCall(`${API_BASE}/api/drones/telemetry/${droneId}`);
}

// Deploy drone
export async function deployDrone(location) {
  return apiCall(`${API_BASE}/api/drones/deploy`, {
    method: "POST",
    body: JSON.stringify(location),
  });
}

// Clear all disasters
export async function clearDisasters() {
  return apiCall(`${API_BASE}/api/trigger/clear`, {
    method: "POST",
  });
}

// Get system status
export async function getSystemStatus() {
  return apiCall(`${API_BASE}/api/trigger/status`);
}
