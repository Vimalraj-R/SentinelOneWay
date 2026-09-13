# SentinelOneWay Frontend - SOC Dashboard

## 🎯 Phase 2 Complete

Professional cybersecurity SOC dashboard built with React, Tailwind CSS, and Recharts.

---

## 🚀 Quick Start

```bash
# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Access at: **http://localhost:5174** (or port shown in terminal)

---

## 📁 File Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Sidebar.jsx              # Navigation sidebar
│   │   ├── TopBar.jsx               # Top status bar
│   │   └── Layout.jsx               # Master layout wrapper
│   │
│   └── dashboard/
│       ├── KPICard.jsx              # Reusable metric cards
│       ├── RiskGauge.jsx            # Circular risk score gauge
│       ├── TrafficChart.jsx         # Traffic line chart
│       ├── ThreatDistribution.jsx   # Threat donut chart
│       ├── SeverityDistribution.jsx # Severity bar chart
│       ├── AlertsTable.jsx          # Alerts data table
│       ├── TopAssets.jsx            # Most targeted assets
│       ├── AIInsightPanel.jsx       # ML insights
│       └── MonitoringStatus.jsx     # System status
│
├── pages/
│   ├── Overview.jsx                 # Main dashboard (✅ Complete)
│   └── PlaceholderPage.jsx          # Coming soon template
│
├── data/
│   └── mockData.js                  # All mock data
│
├── App.jsx                          # Routing configuration
├── main.jsx                         # React entry point
└── index.css                        # Global styles
```

---

## 🎨 Components Created: 12 Total

### Layout (3 components)
- Sidebar, TopBar, Layout

### Dashboard (9 components)
- KPICard, RiskGauge, TrafficChart
- ThreatDistribution, SeverityDistribution
- AlertsTable, TopAssets
- AIInsightPanel, MonitoringStatus

---

## 📊 Mock Data

All realistic, human-readable cybersecurity data:
- KPIs with trends
- 24h traffic timeline
- 5 threat types
- 6 recent alerts
- 5 top assets
- 3 AI insights
- System monitoring status

---

## 🧭 Navigation

1. Overview ✅ - Main dashboard (complete)
2. Live Traffic - Coming in Phase 3
3. Threat Alerts - Coming in Phase 3
4. Attack Timeline - Coming in Phase 3
5. Assets - Coming in Phase 3
6. AI Insights - Coming in Phase 3
7. Simulation Lab - Coming in Phase 3
8. System Health - Coming in Phase 3

---

Built for SOC analysts and critical infrastructure protection 🛡️
