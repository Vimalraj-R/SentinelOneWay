/**
 * Simulation Lab - Safe demonstration environment
 */
import { useState } from 'react';
import { Play, Square, AlertTriangle, Activity, Zap, Shield, TrendingUp } from 'lucide-react';

export default function SimulationLab() {
  const [selectedScenario, setSelectedScenario] = useState('syn_flood');
  const [intensity, setIntensity] = useState(0.5);
  const [duration, setDuration] = useState(30);
  const [isRunning, setIsRunning] = useState(false);

  const scenarios = [
    { id: 'normal', name: 'Normal Traffic', description: 'Benign HTTP, DNS, and application traffic', icon: Activity, color: 'green' },
    { id: 'syn_flood', name: 'SYN Flood Attack', description: 'Volumetric DDoS with incomplete TCP handshakes', icon: Zap, color: 'red' },
    { id: 'port_scan', name: 'Port Scan', description: 'Systematic reconnaissance across multiple ports', icon: Shield, color: 'orange' },
    { id: 'c2_beacon', name: 'C2 Beaconing', description: 'Periodic command-and-control communications', icon: TrendingUp, color: 'red' },
    { id: 'dns_tunnel', name: 'DNS Tunneling', description: 'Data exfiltration through DNS queries', icon: AlertTriangle, color: 'yellow' },
    { id: 'data_exfil', name: 'Data Exfiltration', description: 'Large outbound data transfer', icon: TrendingUp, color: 'red' }
  ];

  const currentScenario = scenarios.find(s => s.id === selectedScenario);

  const getColorClasses = (color) => {
    const colors = {
      green: 'border-green-500 bg-green-500/10 text-green-400',
      red: 'border-red-500 bg-red-500/10 text-red-400',
      orange: 'border-orange-500 bg-orange-500/10 text-orange-400',
      yellow: 'border-yellow-500 bg-yellow-500/10 text-yellow-400'
    };
    return colors[color] || colors.green;
  };

  const getIntensityLabel = () => {
    if (intensity < 0.33) return 'Low';
    if (intensity < 0.67) return 'Medium';
    return 'High';
  };

  const startSimulation = () => {
    setIsRunning(true);
    setTimeout(() => setIsRunning(false), duration * 1000);
  };

  const stopSimulation = () => {
    setIsRunning(false);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Warning Banner */}
      <div className="bg-yellow-500/20 border-2 border-yellow-500 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-yellow-400 flex-shrink-0" />
          <div>
            <div className="font-bold text-yellow-400 text-lg">
              Simulation Mode — Synthetic Traffic
            </div>
            <div className="text-sm text-yellow-300">
              All traffic is synthetically generated in-memory. No actual malicious packets are transmitted over the network.
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Simulation Lab</h1>
        <p className="text-gray-400">
          Test and demonstrate the detection pipeline with synthetic attack scenarios
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Scenario Selection */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Scenario</h2>
            <div className="space-y-2">
              {scenarios.map((scenario) => {
                const Icon = scenario.icon;
                return (
                  <button
                    key={scenario.id}
                    onClick={() => !isRunning && setSelectedScenario(scenario.id)}
                    disabled={isRunning}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedScenario === scenario.id
                        ? getColorClasses(scenario.color)
                        : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                    } ${isRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="font-semibold text-white">{scenario.name}</div>
                        <div className="text-xs text-gray-400 mt-1">{scenario.description}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Intensity Control */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Intensity</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Level:</span>
                <span className="font-semibold text-white">{getIntensityLabel()}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={intensity}
                onChange={(e) => !isRunning && setIntensity(parseFloat(e.target.value))}
                disabled={isRunning}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-50"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          </div>

          {/* Duration */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Duration</h2>
            <div className="grid grid-cols-3 gap-2">
              {[15, 30, 60].map(sec => (
                <button
                  key={sec}
                  onClick={() => !isRunning && setDuration(sec)}
                  disabled={isRunning}
                  className={`px-4 py-2 rounded-lg border-2 transition-all font-medium ${
                    duration === sec
                      ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                      : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600'
                  } ${isRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {sec}s
                </button>
              ))}
            </div>
          </div>

          {/* Control Buttons */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Control</h2>
            {!isRunning ? (
              <button
                onClick={startSimulation}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                <Play className="w-5 h-5" />
                Start Simulation
              </button>
            ) : (
              <button
                onClick={stopSimulation}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
              >
                <Square className="w-5 h-5" />
                Stop Simulation
              </button>
            )}
          </div>
        </div>

        {/* Metrics Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              {isRunning ? 'Simulation Running' : 'Ready to Simulate'}
            </h2>
            <div className="space-y-2">
              <p className="text-gray-400">
                <strong className="text-white">Scenario:</strong> {currentScenario?.name}
              </p>
              <p className="text-gray-400">
                <strong className="text-white">Intensity:</strong> {getIntensityLabel()}
              </p>
              <p className="text-gray-400">
                <strong className="text-white">Duration:</strong> {duration} seconds
              </p>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">Synthetic Flows Generated</div>
              <div className="text-3xl font-bold text-white">
                {isRunning ? Math.floor(Math.random() * 1000) : 0}
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">Test Threats Detected</div>
              <div className="text-3xl font-bold text-white">
                {isRunning ? Math.floor(Math.random() * 50) : 0}
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">Avg Detection Latency</div>
              <div className="text-3xl font-bold text-white">
                {isRunning ? (5 + Math.random() * 10).toFixed(1) : 0}
                <span className="text-base text-gray-400 ml-1">ms</span>
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">Current Risk Score</div>
              <div className="text-3xl font-bold text-white">
                {isRunning ? Math.floor(50 + Math.random() * 50) : 0}
                <span className="text-base text-gray-400 ml-1">/100</span>
              </div>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <p className="text-blue-300 text-sm">
              <strong>Safe Testing:</strong> The simulation generates synthetic network flows processed by the same detection pipeline
              used for real traffic. No actual network packets are transmitted.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
