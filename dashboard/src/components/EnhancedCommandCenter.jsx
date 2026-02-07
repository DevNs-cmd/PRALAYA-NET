import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { API_ENDPOINTS, WS_ENDPOINTS, CONFIG } from '../config/api';

// Fix leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const EnhancedCommandCenter = () => {
  const [systemData, setSystemData] = useState(null);
  const [stabilityData, setStabilityData] = useState(null);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [activeActions, setActiveActions] = useState([]);
  const [decisionExplanation, setDecisionExplanation] = useState(null);
  const [replayMode, setReplayMode] = useState(false);
  const [replayStatus, setReplayStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [systemMode, setSystemMode] = useState('autonomous');
  const [demoActive, setDemoActive] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // connected, disconnected, error
  const [backendStatus, setBackendStatus] = useState('checking'); // checking, online, offline
  
  // WebSocket connections
  const stabilityWs = useRef(null);
  const actionsWs = useRef(null);
  const timelineWs = useRef(null);
  const riskWs = useRef(null);

  // Initialize WebSocket connections
  useEffect(() => {
    // Connect to WebSocket streams
    connectWebSockets();
    
    // Fetch initial data
    fetchInitialData();
    
    return () => {
      // Cleanup WebSocket connections
      if (stabilityWs.current) stabilityWs.current.close();
      if (actionsWs.current) actionsWs.current.close();
      if (timelineWs.current) timelineWs.current.close();
      if (riskWs.current) riskWs.current.close();
    };
  }, []);

  const connectWebSockets = () => {
    console.log('🔄 Connecting to WebSocket streams...');
    
    // Stability stream
    stabilityWs.current = new WebSocket(WS_ENDPOINTS.STABILITY_STREAM);
    stabilityWs.current.onopen = () => {
      console.log('✅ Connected to stability stream');
      setConnectionStatus('connected');
    };
    stabilityWs.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'stability_update') {
        setStabilityData(data.stability_index);
      }
    };
    stabilityWs.current.onerror = (error) => {
      console.error('❌ Stability stream error:', error);
      setConnectionStatus('error');
    };
    stabilityWs.current.onclose = () => {
      console.log('🔌 Stability stream closed');
      setConnectionStatus('disconnected');
    };

    // Actions stream
    actionsWs.current = new WebSocket(WS_ENDPOINTS.ACTIONS_STREAM);
    actionsWs.current.onopen = () => {
      console.log('✅ Connected to actions stream');
    };
    actionsWs.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'action_update') {
        setActiveActions(prev => [...prev.slice(-9), data.action]);
      }
    };
    actionsWs.current.onerror = (error) => {
      console.error('❌ Actions stream error:', error);
    };

    // Timeline stream
    timelineWs.current = new WebSocket(WS_ENDPOINTS.TIMELINE_STREAM);
    timelineWs.current.onopen = () => {
      console.log('✅ Connected to timeline stream');
    };
    timelineWs.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'event') {
        setTimelineEvents(prev => [...prev.slice(-19), data.event]);
      }
    };
    timelineWs.current.onerror = (error) => {
      console.error('❌ Timeline stream error:', error);
    };

    // Risk stream
    riskWs.current = new WebSocket(WS_ENDPOINTS.RISK_STREAM);
    riskWs.current.onopen = () => {
      console.log('✅ Connected to risk stream');
    };
    riskWs.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'risk_update') {
        setSystemData(prev => prev ? {
          ...prev,
          infrastructure: {
            ...prev.infrastructure,
            nodes: data.infrastructure_nodes || prev.infrastructure.nodes
          }
        } : null);
      }
    };
    riskWs.current.onerror = (error) => {
      console.error('❌ Risk stream error:', error);
    };
  };

  const fetchInitialData = async () => {
    try {
      setBackendStatus('checking');
      console.log('🔄 Connecting to PRALAYA-NET backend...');
      
      // Fetch system data
      const systemResponse = await fetch(API_ENDPOINTS.COMMAND_CENTER_DATA);
      const systemData = await systemResponse.json();
      setSystemData(systemData);

      // Fetch stability data
      const stabilityResponse = await fetch(API_ENDPOINTS.STABILITY_CURRENT);
      const stabilityData = await stabilityResponse.json();
      setStabilityData(stabilityData.stability_index);

      // Fetch recent events
      const eventsResponse = await fetch(API_ENDPOINTS.REPLAY_EVENTS + '?limit=20');
      const eventsData = await eventsResponse.json();
      setTimelineEvents(eventsData.events);

      setBackendStatus('online');
      console.log('✅ Connected to PRALAYA-NET backend');
      setLoading(false);
    } catch (error) {
      console.error('❌ Error connecting to backend:', error);
      setBackendStatus('offline');
      setLoading(false);
    }
  };

  const startAutonomousDemo = async () => {
    try {
      setDemoActive(true);
      const response = await fetch(API_ENDPOINTS.AUTONOMOUS_DEMO, {
        method: 'POST'
      });
      const result = await response.json();
      console.log('Demo started:', result);
    } catch (error) {
      console.error('Error starting demo:', error);
      setDemoActive(false);
    }
  };

  const simulateDisaster = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.AUTONOMOUS_SIMULATE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          disaster_type: 'earthquake',
          affected_nodes: ['power_grid_mumbai', 'telecom_mumbai', 'transport_mumbai'],
          severity: 0.8
        })
      });
      const result = await response.json();
      console.log('Disaster simulated:', result);
    } catch (error) {
      console.error('Error simulating disaster:', error);
    }
  };

  const getDecisionExplanation = async (intentId) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.DECISION_EXPLAIN}/${intentId}`);
      const data = await response.json();
      setDecisionExplanation(data.explanation);
    } catch (error) {
      console.error('Error getting decision explanation:', error);
    }
  };

  const startReplay = async () => {
    try {
      // Get completed sessions
      const sessionsResponse = await fetch(API_ENDPOINTS.REPLAY_COMPLETED + '?limit=1');
      const sessionsData = await sessionsResponse.json();
      
      if (sessionsData.completed_sessions.length > 0) {
        const sessionId = sessionsData.completed_sessions[0].session_id;
        
        const response = await fetch(API_ENDPOINTS.REPLAY_START, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            playback_speed: 2.0
          })
        });
        
        if (response.ok) {
          setReplayMode(true);
          setReplayStatus('replaying');
        }
      }
    } catch (error) {
      console.error('Error starting replay:', error);
    }
  };

  const stopReplay = async () => {
    try {
      // Get active sessions
      const sessionsResponse = await fetch(API_ENDPOINTS.REPLAY_SESSIONS);
      const sessionsData = await sessionsResponse.json();
      
      if (sessionsData.active_sessions.length > 0) {
        const sessionId = sessionsData.active_sessions[0].session_id;
        
        await fetch(`${API_ENDPOINTS.REPLAY_STATUS}/${sessionId}`, {
          method: 'POST'
        });
      }
      
      setReplayMode(false);
      setReplayStatus(null);
    } catch (error) {
      console.error('Error stopping replay:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl mb-4">Loading Enhanced Command Center...</div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">
              {backendStatus === 'checking' ? 'Checking backend connection...' : 
               backendStatus === 'online' ? 'Backend connected' : 
               'Backend offline - check if backend is running'}
              </span>
          </div>
        </div>
      </div>
    );
  }

  const getStabilityColor = (index) => {
    if (!index) return 'text-gray-500';
    if (index.overall_score < 0.4) return 'text-red-500';
    if (index.overall_score < 0.7) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getStabilityBgColor = (index) => {
    if (!index) return 'bg-gray-500';
    if (index.overall_score < 0.4) return 'bg-red-500';
    if (index.overall_score < 0.7) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  // Infrastructure node locations
  const infrastructureLocations = {
    power_grid_mumbai: [19.0760, 72.8777],
    power_grid_delhi: [28.7041, 77.1025],
    telecom_mumbai: [19.0760, 72.8777],
    telecom_delhi: [28.7041, 77.1025],
    transport_mumbai: [19.0760, 72.8777],
    transport_delhi: [28.7041, 77.1025],
    water_mumbai: [19.0760, 72.8777],
    water_delhi: [28.7041, 77.1025],
    hospital_mumbai: [19.0760, 72.8777],
    hospital_delhi: [28.7041, 77.1025],
    bridge_sealink: [19.0760, 72.8777],
    bridge_bandra: [19.0760, 72.8777]
  };
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center">
        <div className="text-xl mb-4">Loading Enhanced Command Center...</div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">
            {backendStatus === 'checking' ? 'Checking backend connection...' : 
             backendStatus === 'online' ? 'Backend connected' : 
             'Backend offline - check if backend is running'}
            </span>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">System Mode</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setSystemMode('manual')}
              className={`px-3 py-1 rounded ${systemMode === 'manual' ? 'bg-blue-600' : 'bg-gray-700'}`}
            >
              Manual
            </button>
            <button
              onClick={() => setSystemMode('assisted')}
              className={`px-3 py-1 rounded ${systemMode === 'assisted' ? 'bg-blue-600' : 'bg-gray-700'}`}
            >
              Assisted
            </button>
            <button
              onClick={() => setSystemMode('autonomous')}
              className={`px-3 py-1 rounded ${systemMode === 'autonomous' ? 'bg-green-600' : 'bg-gray-700'}`}
            >
              Autonomous
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Demo Controls</h3>
          <div className="flex space-x-2">
            <button
              onClick={startAutonomousDemo}
              disabled={demoActive}
              className={`px-3 py-1 rounded ${demoActive ? 'bg-gray-600' : 'bg-green-600 hover:bg-green-700'}`}
            >
              {demoActive ? 'Demo Running' : 'Start Demo'}
            </button>
            <button
              onClick={simulateDisaster}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded"
            >
              Simulate
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Replay Mode</h3>
          <div className="flex space-x-2">
            {!replayMode ? (
              <button
                onClick={startReplay}
                className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded"
              >
                Start Replay
              </button>
            ) : (
              <button
                onClick={stopReplay}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded"
              >
                Stop Replay
              </button>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">System Status</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${stabilityData?.level === 'healthy' || stabilityData?.level === 'excellent' ? 'bg-green-500' : stabilityData?.level === 'warning' ? 'bg-yellow-500' : 'bg-red-500'} animate-pulse`}></div>
            <span className="capitalize">{stabilityData?.level || 'Unknown'}</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* National Stability Index */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">National Stability Index</h2>
          <div className="flex items-center justify-center">
            <div className="relative">
              <div className="w-48 h-48 rounded-full border-8 border-gray-700 flex items-center justify-center">
                <div className={`text-center ${getStabilityColor(stabilityData)}`}>
                  <div className="text-5xl font-bold">
                    {stabilityData ? Math.round(stabilityData.overall_score * 100) : 0}%
                  </div>
                  <div className="text-sm">Stability</div>
                  <div className="text-xs mt-1 capitalize">{stabilityData?.trend || 'stable'}</div>
                </div>
              </div>
              {/* Animated ring */}
              <div className={`absolute inset-0 rounded-full border-8 ${getStabilityBgColor(stabilityData)} animate-pulse`}></div>
            </div>
          </div>
          <div className="text-center mt-4 text-gray-400">
            Real-time infrastructure stability indicator
          </div>
        </div>

        {/* Live India Map */}
        <div className="bg-gray-800 rounded-lg p-4 lg:col-span-2">
          <h2 className="text-xl font-bold mb-4">Live India Risk Map</h2>
          <div className="h-96 rounded-lg overflow-hidden">
            <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: '100%', width: '100%' }}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              
              {/* Infrastructure nodes */}
              {systemData?.infrastructure?.nodes && Object.entries(systemData.infrastructure.nodes).map(([nodeId, nodeData]) => {
                const location = infrastructureLocations[nodeId];
                if (!location) return null;
                
                const risk = nodeData.risk;
                const color = risk > 0.6 ? 'red' : risk > 0.3 ? 'yellow' : 'green';
                
                return (
                  <CircleMarker
                    key={nodeId}
                    center={location}
                    radius={10}
                    fillColor={color}
                    color="#fff"
                    weight={2}
                    opacity={1}
                    fillOpacity={0.8}
                  >
                    <Popup>
                      <div className="text-black">
                        <strong>{nodeId}</strong><br/>
                        Type: {nodeData.type}<br/>
                        Risk: {(risk * 100).toFixed(1)}%<br/>
                        Load: {nodeData.load}/{nodeData.capacity}
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>
        </div>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Autonomous Actions Panel */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Autonomous Actions</h2>
          <div className="space-y-3">
            {activeActions.slice(0, 5).map((action, index) => (
              <div key={index} className="bg-gray-700 rounded p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold">{action.target_infrastructure_node || 'Unknown Node'}</div>
                    <div className="text-sm text-gray-400">{action.action || 'Unknown Action'}</div>
                  </div>
                  <button
                    onClick={() => getDecisionExplanation(action.intent_id)}
                    className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                  >
                    Explain
                  </button>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${(action.progress || 0) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Status: {action.status || 'Unknown'} • Risk: {action.risk_level ? (action.risk_level * 100).toFixed(1) : 'N/A'}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Decision Explanation Panel */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Decision Explanation</h2>
          {decisionExplanation ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-blue-400">Chosen Action</h3>
                <p className="text-gray-300">{decisionExplanation.chosen_action}</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-green-400">Reasoning</h3>
                <p className="text-gray-300 text-sm whitespace-pre-line">{decisionExplanation.reasoning}</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-yellow-400">Signals Used</h3>
                <div className="space-y-1">
                  {decisionExplanation.signals_used?.slice(0, 3).map((signal, index) => (
                    <div key={index} className="text-sm text-gray-300">
                      • {signal.signal_type}: {(signal.value * 100).toFixed(1)}% confidence
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-purple-400">Predicted Impact</h3>
                <div className="text-sm text-gray-300">
                  Risk Reduction: {decisionExplanation.predicted_impact?.risk_reduction ? (decisionExplanation.predicted_impact.risk_reduction * 100).toFixed(1) : 'N/A'}%
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-red-400">Confidence</h3>
                <div className="text-sm text-gray-300">
                  {(decisionExplanation.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-400 text-center py-8">
              Click "Explain" on any action to see detailed reasoning
            </div>
          )}
        </div>
      </div>

      {/* Crisis Timeline */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h2 className="text-xl font-bold mb-4">Crisis Timeline Feed</h2>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {timelineEvents.slice(-10).reverse().map((event, index) => (
            <div key={index} className="flex items-start space-x-3 bg-gray-700 rounded p-3">
              <div className={`w-2 h-2 rounded-full mt-2 ${
                event.severity === 'critical' ? 'bg-red-500' :
                event.severity === 'warning' ? 'bg-yellow-500' :
                event.event_type === 'disaster_detected' ? 'bg-red-500' :
                event.event_type === 'intent_generated' ? 'bg-yellow-500' :
                event.event_type === 'stabilization_executed' ? 'bg-green-500' :
                'bg-blue-500'
              }`}></div>
              <div className="flex-1">
                <div className="font-semibold capitalize">
                  {event.event_type?.replace('_', ' ') || 'Unknown Event'}
                </div>
                <div className="text-gray-400 text-sm">
                  {event.data?.message || 'System event occurred'}
                </div>
                <div className="text-gray-500 text-xs">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-2">Infrastructure Health</h3>
          <div className="text-2xl font-bold text-blue-400">
            {systemData?.infrastructure?.total_nodes || 0}
          </div>
          <div className="text-gray-400 text-sm">Total Nodes</div>
          <div className="text-sm text-red-400 mt-1">
            {systemData?.infrastructure?.high_risk_nodes || 0} High Risk
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-2">Agent Coordination</h3>
          <div className="text-2xl font-bold text-green-400">
            {systemData?.agent_coordination?.available || 0}
          </div>
          <div className="text-gray-400 text-sm">Available Agents</div>
          <div className="text-sm text-yellow-400 mt-1">
            {systemData?.agent_coordination?.total_agents || 0} Total
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-2">Execution Proof</h3>
          <div className="text-2xl font-bold text-purple-400">
            {systemData?.execution_proof?.total_executions || 0}
          </div>
          <div className="text-gray-400 text-sm">Executions Today</div>
          <div className="text-sm text-green-400 mt-1">
            {systemData?.autonomous_actions?.completed_today || 0} Completed
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedCommandCenter;
