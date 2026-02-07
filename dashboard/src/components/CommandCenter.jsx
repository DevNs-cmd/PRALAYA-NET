import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const CommandCenter = () => {
  const [systemData, setSystemData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [systemMode, setSystemMode] = useState('autonomous');
  const [demoActive, setDemoActive] = useState(false);

  // Fetch system data
  const fetchSystemData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/autonomous/command-center/data');
      const data = await response.json();
      setSystemData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching system data:', error);
      setLoading(false);
    }
  };

  // Start autonomous demo
  const startAutonomousDemo = async () => {
    try {
      setDemoActive(true);
      const response = await fetch('http://127.0.0.1:8000/api/autonomous/start-autonomous-demo', {
        method: 'POST'
      });
      const result = await response.json();
      console.log('Demo started:', result);
    } catch (error) {
      console.error('Error starting demo:', error);
      setDemoActive(false);
    }
  };

  // Simulate disaster cascade
  const simulateDisaster = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/autonomous/simulate-disaster', {
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

  useEffect(() => {
    fetchSystemData();
    const interval = setInterval(fetchSystemData, 3000); // Update every 3 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-xl">Loading Command Center...</div>
      </div>
    );
  }

  const getStabilityColor = (index) => {
    if (index < 0.4) return 'text-red-500';
    if (index < 0.7) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getStabilityBgColor = (index) => {
    if (index < 0.4) return 'bg-red-500';
    if (index < 0.7) return 'bg-yellow-500';
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
    <div className="min-h-screen bg-gray-900 text-white p-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold mb-2">🚀 PRALAYA-NET Command Center</h1>
        <p className="text-gray-400">Autonomous Self-Healing National Infrastructure Network</p>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
              className={`px-4 py-2 rounded ${demoActive ? 'bg-gray-600' : 'bg-green-600 hover:bg-green-700'}`}
            >
              {demoActive ? 'Demo Running...' : 'Start Full Demo'}
            </button>
            <button
              onClick={simulateDisaster}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
            >
              Simulate Disaster
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">System Status</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${systemData?.national_stability_index?.status === 'healthy' ? 'bg-green-500' : systemData?.national_stability_index?.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'} animate-pulse`}></div>
            <span className="capitalize">{systemData?.national_stability_index?.status || 'Unknown'}</span>
          </div>
        </div>
      </div>

      {/* National Stability Index */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">National Stability Index</h2>
        <div className="flex items-center justify-center">
          <div className="relative">
            <div className="w-48 h-48 rounded-full border-8 border-gray-700 flex items-center justify-center">
              <div className={`text-center ${getStabilityColor(systemData?.national_stability_index?.value || 0)}`}>
                <div className="text-5xl font-bold">
                  {Math.round((systemData?.national_stability_index?.value || 0) * 100)}%
                </div>
                <div className="text-sm">Stability</div>
              </div>
            </div>
            {/* Animated ring */}
            <div className={`absolute inset-0 rounded-full border-8 ${getStabilityBgColor(systemData?.national_stability_index?.value || 0)} animate-pulse`}></div>
          </div>
        </div>
        <div className="text-center mt-4 text-gray-400">
          Real-time infrastructure stability indicator
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Live India Map */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Live India Map</h2>
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

        {/* Autonomous Actions Panel */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Autonomous Actions</h2>
          <div className="space-y-4">
            <div className="bg-gray-700 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">Active Intents</span>
                <span className="text-green-400">{systemData?.autonomous_actions?.total_active || 0}</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (systemData?.autonomous_actions?.total_active || 0) * 20)}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-gray-700 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">Executing</span>
                <span className="text-yellow-400">{systemData?.autonomous_actions?.executing || 0}</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (systemData?.autonomous_actions?.executing || 0) * 30)}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-gray-700 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold">Completed Today</span>
                <span className="text-blue-400">{systemData?.autonomous_actions?.completed_today || 0}</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (systemData?.autonomous_actions?.completed_today || 0) * 5)}%` }}
                ></div>
              </div>
            </div>

            {/* Active Intents List */}
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Active Intents</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {systemData?.autonomous_actions?.active_intents?.slice(0, 5).map((intent, index) => (
                  <div key={index} className="bg-gray-700 rounded p-2 text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium">{intent.target_infrastructure_node}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        intent.status === 'executing' ? 'bg-yellow-600' : 
                        intent.status === 'completed' ? 'bg-green-600' : 'bg-gray-600'
                      }`}>
                        {intent.status}
                      </span>
                    </div>
                    <div className="text-gray-400 text-xs mt-1">
                      Risk: {(intent.risk_level * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Crisis Timeline Feed */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h2 className="text-xl font-bold mb-4">Crisis Timeline Feed</h2>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          <div className="flex items-start space-x-3 bg-gray-700 rounded p-3">
            <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <div className="font-semibold">Disaster Detected</div>
              <div className="text-gray-400 text-sm">High risk detected in Mumbai power grid</div>
              <div className="text-gray-500 text-xs">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
          
          <div className="flex items-start space-x-3 bg-gray-700 rounded p-3">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <div className="font-semibold">Intent Generated</div>
              <div className="text-gray-400 text-sm">Autonomous stabilization intent created</div>
              <div className="text-gray-500 text-xs">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
          
          <div className="flex items-start space-x-3 bg-gray-700 rounded p-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <div className="font-semibold">Agents Negotiating</div>
              <div className="text-gray-400 text-sm">Multi-agent negotiation in progress</div>
              <div className="text-gray-500 text-xs">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
          
          <div className="flex items-start space-x-3 bg-gray-700 rounded p-3">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <div className="font-semibold">Infrastructure Stabilized</div>
              <div className="text-gray-400 text-sm">Risk reduced by 45%, stability improved</div>
              <div className="text-gray-500 text-xs">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Coordination & Execution Proof */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Coordination */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Agent Coordination</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-green-400">
                {systemData?.agent_coordination?.available || 0}
              </div>
              <div className="text-gray-400 text-sm">Available Agents</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-2xl font-bold text-yellow-400">
                {systemData?.agent_coordination?.total_agents || 0}
              </div>
              <div className="text-gray-400 text-sm">Total Agents</div>
            </div>
          </div>
          
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Agent Status</h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {systemData?.agent_coordination?.agents?.slice(0, 4).map((agent, index) => (
                <div key={index} className="bg-gray-700 rounded p-2 text-sm">
                  <div className="flex justify-between">
                    <span>{agent.agent_id}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      agent.status === 'idle' ? 'bg-green-600' : 
                      agent.status === 'executing' ? 'bg-yellow-600' : 'bg-gray-600'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                  <div className="text-gray-400 text-xs">
                    {agent.agent_type} • Performance: {(agent.performance_score * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Execution Proof */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Execution Proof</h2>
          <div className="bg-gray-700 rounded p-3">
            <div className="text-2xl font-bold text-blue-400">
              {systemData?.execution_proof?.total_executions || 0}
            </div>
            <div className="text-gray-400 text-sm">Executions Today</div>
          </div>
          
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Recent Ledger Entries</h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {systemData?.execution_proof?.recent_ledger?.slice(0, 3).map((entry, index) => (
                <div key={index} className="bg-gray-700 rounded p-2 text-sm">
                  <div className="font-medium">{entry.intent_id}</div>
                  <div className="text-gray-400 text-xs">
                    {entry.action_executed} • {entry.validation_result ? 'Success' : 'Failed'}
                  </div>
                  <div className="text-gray-500 text-xs">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;
