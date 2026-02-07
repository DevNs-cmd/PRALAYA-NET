/**
 * API Configuration for PRALAYA-NET Frontend
 * Automatically detects environment and sets appropriate API URL
 */

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// WebSocket URL (same as API but with ws protocol)
const WS_URL = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');

// API endpoints
export const API_ENDPOINTS = {
  // Health and System
  HEALTH: `${API_URL}/api/health`,
  
  // Autonomous Execution
  AUTONOMOUS_STATUS: `${API_URL}/api/autonomous/status`,
  AUTONOMOUS_STABILITY: `${API_URL}/api/autonomous/stability-index`,
  AUTONOMOUS_INFRASTRUCTURE: `${API_URL}/api/autonomous/infrastructure-status`,
  AUTONOMOUS_INTENTS: `${API_URL}/api/autonomous/intents`,
  AUTONOMOUS_LEDGER: `${API_URL}/api/autonomous/execution-ledger`,
  AUTONOMOUS_SIMULATE: `${API_URL}/api/autonomous/simulate-disaster`,
  AUTONOMOUS_DEMO: `${API_URL}/api/autonomous/start-autonomous-demo`,
  COMMAND_CENTER_DATA: `${API_URL}/api/autonomous/command-center/data`,
  
  // Stability Index
  STABILITY_CURRENT: `${API_URL}/api/stability/current`,
  STABILITY_HISTORY: `${API_URL}/api/stability/history`,
  STABILITY_FACTORS: `${API_URL}/api/stability/factors`,
  STABILITY_ALERTS: `${API_URL}/api/stability/alerts`,
  STABILITY_SIMULATE: `${API_URL}/api/stability/simulate-impact`,
  STABILITY_DASHBOARD: `${API_URL}/api/stability/dashboard`,
  
  // Decision Explainability
  DECISION_EXPLAIN: `${API_URL}/api/decision/explain`,
  DECISION_EXPLAINATIONS: `${API_URL}/api/decision/explanations`,
  DECISION_PATTERNS: `${API_URL}/api/decision/patterns`,
  DECISION_SIGNALS: `${API_URL}/api/decision/signals`,
  DECISION_ANALYTICS: `${API_URL}/api/decision/analytics`,
  
  // Replay Engine
  REPLAY_SESSIONS: `${API_URL}/api/replay/sessions`,
  REPLAY_COMPLETED: `${API_URL}/api/replay/sessions/completed`,
  REPLAY_START: `${API_URL}/api/replay/start`,
  REPLAY_EVENTS: `${API_URL}/api/replay/events`,
  REPLAY_STATUS: `${API_URL}/api/replay/status`,
  REPLAY_ANALYTICS: `${API_URL}/api/replay/analytics`,
  
  // Multi-Agent Negotiation
  AGENTS_STATUS: `${API_URL}/api/negotiation/agents/status`,
  AGENTS_TASKS: `${API_URL}/api/negotiation/tasks`,
  AGENTS_METRICS: `${API_URL}/api/negotiation/metrics`,
  AGENTS_NEGOTIATION: `${API_URL}/api/negotiation/negotiation-history`,
  
  // API Documentation
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
  UPDATE_INTERVAL: 3000 // 3 seconds for polling fallback
};

// Export default API URL for backward compatibility
export default API_URL;
