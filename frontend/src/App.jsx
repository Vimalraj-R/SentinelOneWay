import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Overview from './pages/Overview';
import AlertDetail from './pages/AlertDetail';
import LiveTraffic from './pages/LiveTraffic';
import ThreatAlerts from './pages/ThreatAlerts';
import AttackTimeline from './pages/AttackTimeline';
import Assets from './pages/Assets';
import SimulationLab from './pages/SimulationLab';
import SystemHealth from './pages/SystemHealth';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="alert/:id" element={<AlertDetail />} />
          <Route path="live-traffic" element={<LiveTraffic />} />
          <Route path="threat-alerts" element={<ThreatAlerts />} />
          <Route path="attack-timeline" element={<AttackTimeline />} />
          <Route path="assets" element={<Assets />} />
          <Route path="simulation-lab" element={<SimulationLab />} />
          <Route path="system-health" element={<SystemHealth />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
