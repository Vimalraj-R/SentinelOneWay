# Alert Investigation Page - Complete

## 🎯 Overview

A comprehensive threat alert investigation interface has been implemented for SentinelOneWay, designed to provide SOC analysts with detailed, human-readable explanations of why threats were detected and what evidence supports those detections.

---

## ✨ Key Features

### 🔍 **Human-Readable Detection Reasoning**
The most important feature - explains WHY the alert was triggered in plain language:
- "SYN traffic increased 14.6x above the learned baseline"
- "23,421 unique source addresses contacted the target"
- NOT technical jargon like "feature_14 = 3.921"

### 🛡️ **Read-Only Operations**
Following SentinelOneWay's passive monitoring principle:
- ✅ Mark Investigating
- ✅ Acknowledge
- ✅ Resolve
- ✅ Add Notes
- ✅ Export Report
- ❌ NO block/kill/quarantine actions

### 📊 **Comprehensive Analysis**
- Network flow information with visual source→destination
- Risk assessment with circular gauge
- Technical evidence metrics
- Event timeline
- Related alerts
- Affected asset details
- AI/ML model explanation
- Analyst collaboration notes

---

## 🎨 Components Created (11 Total)

### Alert Components (`src/components/alert/`)

1. **AlertHeader.jsx**
   - Threat name, severity, confidence, status badges
   - Detection timestamp
   - Back navigation button
   - Alert/Flow ID

2. **NetworkInfo.jsx**
   - Visual source → destination display
   - IP addresses and ports
   - Protocol, duration, packet/byte counts
   - Flow ID

3. **RiskPanel.jsx**
   - Animated circular risk score gauge (0-100)
   - Risk level classification
   - Attack category and vector
   - Asset criticality
   - Model confidence

4. **DetectionReasoning.jsx** ⭐ **Most Important**
   - Human-readable summary
   - Bullet-pointed evidence list with checkmarks
   - Clear explanation of detection logic

5. **TechnicalEvidence.jsx**
   - Grid layout of technical metrics
   - Baseline comparisons
   - Statistical anomalies
   - Network measurements

6. **EventTimeline.jsx**
   - Chronological event progression
   - Color-coded severity markers
   - Visual timeline with connecting lines
   - Time-stamped events

7. **RelatedAlerts.jsx**
   - Linked related alerts (clickable)
   - Severity indicators
   - Target information
   - Quick navigation

8. **AffectedAsset.jsx**
   - Hostname and IP address
   - Asset role and criticality
   - Location and ownership
   - Running services
   - Last user and login time

9. **AIExplanation.jsx**
   - ML model name and confidence
   - Detailed AI analysis in natural language
   - Recommendations section
   - Purple/blue gradient styling for AI context

10. **AnalystActions.jsx**
    - Status change buttons (passive actions only)
    - Export alert report
    - Passive monitoring mode notice
    - NO active mitigation options

11. **AnalystNotes.jsx**
    - Add new notes interface
    - View existing notes with author/timestamp
    - Collaboration space for SOC team

---

## 📄 Pages Created

### **AlertDetail.jsx**
Main investigation page that orchestrates all components:
- Route: `/alert/:id`
- Responsive grid layout
- Retrieves alert data by ID
- Handles missing alert gracefully

---

## 📊 Mock Data Structure

### **mockAlertDetails.js**
Contains detailed data for 3 sample alerts:

#### **Alert #1: SYN Flood**
- **Severity**: Critical
- **Confidence**: 94%
- **Detection**: 14.6x traffic spike, 23,421 unique sources
- **Technical Evidence**: 182,400 SYN/sec vs 12,500 baseline
- **Full investigation timeline and AI analysis**

#### **Alert #2: Port Scan**
- **Severity**: High
- **Confidence**: 89%
- **Detection**: Sequential port scanning across 42 hosts
- **Technical Evidence**: 65,535 ports probed, 289 ports/sec scan rate
- **Reconnaissance activity classification**

#### **Alert #3: C2 Beacon** ⭐ **Most Sophisticated**
- **Severity**: Critical
- **Confidence**: 97%
- **Detection**: 120-second regular beaconing pattern
- **Technical Evidence**: 98.7% interval consistency, malicious IP match
- **Includes compromise indicators and IR recommendations**

---

## 🚀 How to Use

### Accessing Alert Details

**From Overview Dashboard:**
1. Click any row in the "Recent Threat Alerts" table
2. Automatically navigates to `/alert/{id}`

**Direct URL:**
```
http://localhost:5173/alert/1  (SYN Flood)
http://localhost:5173/alert/2  (Port Scan)
http://localhost:5173/alert/3  (C2 Beacon)
```

### Navigation
- **Back to Overview**: Click "← Back to Overview" button
- **Related Alerts**: Click any related alert card
- **Add Notes**: Click "Add Note" button

---

## 🎨 Design Decisions

### **1. Human-First Communication**
- Avoids ML jargon and raw feature scores
- Uses comparative language ("14.6x above baseline")
- Explains impact ("incomplete handshakes", "highly distributed")

### **2. Visual Hierarchy**
- Alert header at top (most important context)
- "Why Detected?" section prominent and early
- Technical evidence follows reasoning
- Supporting details (timeline, related alerts) below

### **3. Progressive Disclosure**
- Summary first, then detailed evidence
- Technical metrics after human explanation
- Related context grouped logically

### **4. Read-Only Philosophy**
- Prominently displays "Passive Monitoring Mode" notice
- No destructive or active mitigation actions
- Focus on investigation, documentation, and coordination

### **5. Color Coding**
- **Critical**: Red (immediate attention)
- **High**: Orange (elevated concern)
- **Medium**: Yellow (monitor)
- **Low**: Green (informational)
- **AI Sections**: Purple/blue gradient

### **6. Professional SOC Aesthetics**
- Dark theme for 24/7 operations
- Monospace fonts for IPs, timestamps, technical data
- Clear section headers with icons
- Ample white space, not cluttered

---

## 🔍 Key Sections Explained

### **"Why Was This Detected?" Section**
The centerpiece of the investigation page. Each alert includes:

**Summary**: One-sentence description
**Evidence List**: 4-6 bullet points explaining:
- What anomaly was observed
- How it deviates from normal
- Why it's significant
- Supporting context

**Example (SYN Flood):**
```
✓ SYN traffic increased 14.6x above the learned baseline
✓ 23,421 unique source addresses contacted the target
✓ SYN/ACK ratio is significantly abnormal (18.4:1 vs normal 1.2:1)
✓ Source IP entropy indicates highly distributed attack
✓ No corresponding ACK packets - incomplete handshakes
```

### **Technical Evidence Panel**
Provides quantitative backup for detection reasoning:
- Current values vs baselines
- Deviation percentages
- Statistical measurements
- Network metrics

### **AI Explanation**
- Model name (Random Forest, Isolation Forest, etc.)
- Confidence score
- 2-3 paragraph analysis in conversational language
- Specific recommendations for next steps

---

## 🧪 Testing the Feature

### Test Alert #1 (SYN Flood)
```bash
# Navigate to Overview
http://localhost:5173/

# Click first alert in table (SYN Flood)
# Should show:
# - Risk score: 92/100
# - 6-item timeline
# - 2 related alerts
# - DDoS attack explanation
```

### Test Alert #3 (C2 Beacon)
```bash
# Direct access
http://localhost:5173/alert/3

# Should show:
# - 120-second beacon interval
# - Compromised workstation details
# - User context (jdoe logged off)
# - Analyst note from "analyst-mike"
# - IR recommendations
```

### Test Interactive Features
1. **Add Note**: Click "Add Note" → Enter text → Save
2. **Change Status**: Click "Mark Investigating" button
3. **Export**: Click "Export Alert Report" (console log)
4. **Related Alerts**: Click related alert card → Navigate to that alert
5. **Back Navigation**: Click "← Back to Overview"

---

## 📂 File Structure

```
src/
├── components/
│   └── alert/
│       ├── AlertHeader.jsx           # Header with badges
│       ├── NetworkInfo.jsx           # Source→Dest display
│       ├── RiskPanel.jsx             # Risk gauge
│       ├── DetectionReasoning.jsx    # ⭐ Why detected
│       ├── TechnicalEvidence.jsx     # Metrics grid
│       ├── EventTimeline.jsx         # Chronological events
│       ├── RelatedAlerts.jsx         # Linked alerts
│       ├── AffectedAsset.jsx         # Host details
│       ├── AIExplanation.jsx         # ML analysis
│       ├── AnalystActions.jsx        # Status/Export
│       └── AnalystNotes.jsx          # Collaboration
│
├── pages/
│   └── AlertDetail.jsx               # Main page
│
├── data/
│   └── mockAlertDetails.js           # 3 detailed alerts
│
└── App.jsx                            # Updated with /alert/:id route
```

---

## 🎯 Design Principles Applied

### **1. Clarity Over Complexity**
- Simple, focused layouts
- One concept per section
- Clear section headers

### **2. Context First**
- Alert header provides immediate context
- Summary before details
- Related information grouped

### **3. Evidence-Based**
- Every detection reason backed by evidence
- Technical metrics support claims
- Timeline shows progression

### **4. Analyst-Friendly**
- Conversational language
- Actionable recommendations
- Collaboration tools (notes)

### **5. Passive Posture**
- No active mitigation
- Focus on understanding
- Document and coordinate

---

## ✅ Success Criteria Met

✅ **Human-readable explanations** - No raw ML features  
✅ **Comprehensive investigation** - All critical sections present  
✅ **Passive actions only** - No block/kill/quarantine  
✅ **Professional design** - Clean, SOC-appropriate  
✅ **Detailed evidence** - Technical and contextual  
✅ **AI transparency** - Model confidence and reasoning  
✅ **Collaboration tools** - Notes and status tracking  
✅ **Related context** - Timeline, assets, related alerts  

---

## 🔮 Next Steps (Phase 4)

1. **Backend Integration**
   - Connect to real alert API
   - Live data instead of mock
   - Real-time updates via WebSocket

2. **Enhanced Features**
   - Alert filtering and search
   - PCAP download links
   - Threat intelligence enrichment
   - Export to SIEM/ticketing systems

3. **Advanced Analysis**
   - MITRE ATT&CK mapping
   - Attack chain visualization
   - Comparative analysis (similar alerts)

---

## 📝 Summary

**Created**: 11 reusable alert components + 1 main page  
**Routing**: Integrated with React Router  
**Data**: 3 detailed mock alerts with rich context  
**Philosophy**: Human-readable, passive, evidence-based  
**Status**: ✅ Complete and functional  

**Test it now:** Click any alert in the Overview dashboard! 🚀
