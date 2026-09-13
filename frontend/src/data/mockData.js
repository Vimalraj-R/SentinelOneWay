// Mock data for SentinelOneWay SOC Dashboard

export const kpiData = {
  riskScore: {
    value: 67,
    trend: '+5',
    status: 'warning', // success, warning, danger
    label: 'Network Risk Score'
  },
  activeAlerts: {
    value: 23,
    trend: '+8',
    status: 'warning',
    label: 'Active Alerts'
  },
  criticalThreats: {
    value: 4,
    trend: '+2',
    status: 'danger',
    label: 'Critical Threats'
  },
  flowRate: {
    value: '2.4k',
    trend: '+12%',
    status: 'success',
    label: 'Current Flow Rate',
    unit: 'flows/sec'
  }
};

export const trafficData = [
  { time: '00:00', flows: 1200, threats: 2 },
  { time: '04:00', flows: 980, threats: 1 },
  { time: '08:00', flows: 2100, threats: 5 },
  { time: '12:00', flows: 2800, threats: 8 },
  { time: '16:00', flows: 3200, threats: 12 },
  { time: '20:00', flows: 2400, threats: 6 },
  { time: '23:59', flows: 1800, threats: 3 }
];

export const threatDistribution = [
  { name: 'DDoS/Flood', value: 35, color: '#ef4444' },
  { name: 'Port Scan', value: 28, color: '#f97316' },
  { name: 'C2 Beacon', value: 18, color: '#eab308' },
  { name: 'DNS Tunnel', value: 12, color: '#3b82f6' },
  { name: 'Data Exfil', value: 7, color: '#8b5cf6' }
];

export const severityDistribution = [
  { severity: 'Critical', count: 4, color: '#dc2626' },
  { severity: 'High', count: 11, color: '#ea580c' },
  { severity: 'Medium', count: 8, color: '#ca8a04' },
  { severity: 'Low', count: 15, color: '#16a34a' }
];

export const recentAlerts = [
  {
    id: 1,
    time: '23:47:12',
    threat: 'SYN Flood',
    source: '203.0.113.45',
    destination: '10.0.1.15:443',
    severity: 'Critical',
    confidence: 0.94,
    status: 'Active'
  },
  {
    id: 2,
    time: '23:45:33',
    threat: 'Port Scan',
    source: '198.51.100.88',
    destination: '10.0.2.0/24',
    severity: 'High',
    confidence: 0.89,
    status: 'Active'
  },
  {
    id: 3,
    time: '23:42:18',
    threat: 'C2 Beacon',
    source: '10.0.3.142',
    destination: '185.220.101.5:8080',
    severity: 'Critical',
    confidence: 0.97,
    status: 'Investigating'
  },
  {
    id: 4,
    time: '23:38:05',
    threat: 'DNS Tunnel',
    source: '10.0.4.88',
    destination: 'malicious-domain.xyz',
    severity: 'High',
    confidence: 0.82,
    status: 'Active'
  },
  {
    id: 5,
    time: '23:35:44',
    threat: 'Data Exfiltration',
    source: '10.0.5.201',
    destination: '198.51.100.200:443',
    severity: 'Critical',
    confidence: 0.91,
    status: 'Blocked'
  },
  {
    id: 6,
    time: '23:28:22',
    threat: 'Port Scan',
    source: '203.0.113.120',
    destination: '10.0.1.0/24',
    severity: 'Medium',
    confidence: 0.76,
    status: 'Resolved'
  }
];

export const topAssets = [
  { ip: '10.0.1.15', hostname: 'web-server-01', alerts: 8, risk: 'High' },
  { ip: '10.0.2.50', hostname: 'db-primary', alerts: 5, risk: 'Critical' },
  { ip: '10.0.3.142', hostname: 'workstation-42', alerts: 4, risk: 'High' },
  { ip: '10.0.4.88', hostname: 'dns-resolver', alerts: 3, risk: 'Medium' },
  { ip: '10.0.5.201', hostname: 'file-server', alerts: 3, risk: 'High' }
];

export const aiInsights = [
  {
    id: 1,
    type: 'anomaly',
    title: 'Unusual Traffic Pattern Detected',
    description: 'Traffic from 10.0.3.0/24 increased 12x above baseline during off-hours.',
    severity: 'warning',
    confidence: 0.88,
    timestamp: '23:45:00'
  },
  {
    id: 2,
    type: 'correlation',
    title: 'Possible Multi-Stage Attack',
    description: 'Port scan from 198.51.100.88 followed by connection attempts to scanned ports.',
    severity: 'critical',
    confidence: 0.92,
    timestamp: '23:42:00'
  },
  {
    id: 3,
    type: 'prediction',
    title: 'DGA Domain Activity',
    description: 'Host 10.0.4.88 queried 47 algorithmically-generated domains in 10 minutes.',
    severity: 'high',
    confidence: 0.85,
    timestamp: '23:38:00'
  }
];

export const monitoringStatus = {
  mode: 'Passive',
  status: 'Active',
  uptime: '99.97%',
  lastUpdate: new Date().toISOString(),
  sensors: {
    total: 8,
    active: 8,
    inactive: 0
  },
  networkInterfaces: [
    { name: 'eth0', status: 'active', packets: '2.4M/s', drops: 0 },
    { name: 'eth1', status: 'active', packets: '1.8M/s', drops: 0 }
  ]
};
