# ✅ Verify All Pages Working

## Test Each Page (Copy URLs to Browser)

### 1. Overview Dashboard
**URL:** http://localhost:5173/
**Should show:**
- ✅ Active threats count
- ✅ Network risk score
- ✅ Recent alerts table
- ✅ Traffic chart

### 2. Live Traffic
**URL:** http://localhost:5173/live-traffic
**Should show:**
- ✅ Flows/sec, Inbound, Outbound metrics
- ✅ Protocol distribution (TCP/UDP/Other)
- ✅ Live flow table with 10 recent flows
- ✅ Auto-refresh toggle (Live/Paused)

### 3. Threat Alerts
**URL:** http://localhost:5173/threat-alerts
**Should show:**
- ✅ Stats: Total 15, Critical 5, High 7, Medium 3
- ✅ Search bar
- ✅ Filter by severity dropdown
- ✅ Sort by dropdown
- ✅ 15 alert cards listed

### 4. Attack Timeline
**URL:** http://localhost:5173/attack-timeline
**Should show:**
- ✅ 3 incidents in left panel
- ✅ Timeline visualization
- ✅ Attack stages with times
- ✅ Affected assets

### 5. Assets
**URL:** http://localhost:5173/assets
**Should show:**
- ✅ Stats cards (Total: 8, Critical Risk, High Risk, Active Monitoring)
- ✅ Search bar
- ✅ 8 asset cards in grid layout
- ✅ Each card shows: hostname, IP, type, risk level, alerts

### 6. Simulation Lab
**URL:** http://localhost:5173/simulation-lab
**Should show:**
- ✅ Yellow warning banner "SIMULATION MODE"
- ✅ 6 scenario cards (Normal, SYN Flood, Port Scan, C2, DNS Tunnel, Exfil)
- ✅ Intensity slider (Low/Medium/High)
- ✅ Duration buttons (15/30/60 sec)
- ✅ Start/Stop button
- ✅ 4 metrics cards (Flows, Threats, Latency, Risk)

### 7. System Health
**URL:** http://localhost:5173/system-health
**Should show:**
- ✅ Green "System Operational" banner
- ✅ 4 component cards (Backend API, Database, ML Models, WebSocket)
- ✅ Performance metrics section
- ✅ System resources (CPU, Memory, Disk) with progress bars

## If Pages Don't Load:

### Check Browser Console
1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Look for red error messages
4. Share any errors you see

### Clear Browser Cache
1. Press **Ctrl+Shift+Delete** (or Cmd+Shift+Delete on Mac)
2. Check "Cached images and files"
3. Click "Clear data"
4. Refresh with **Ctrl+F5**

### Restart Frontend
```bash
# Stop current frontend (Ctrl+C in terminal)
cd C:\Users\Vimalraj\SentinelOneWay\frontend
npm run dev
```

## Quick Test Commands

```bash
# Test if all routes exist
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/ && echo "Overview"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/live-traffic && echo "Live Traffic"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/threat-alerts && echo "Threat Alerts"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/attack-timeline && echo "Attack Timeline"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/assets && echo "Assets"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/simulation-lab && echo "Simulation Lab"
curl -s -o /dev/null -w "%{http_code} " http://localhost:5173/system-health && echo "System Health"
```

All should return **200**.

## Common Issues

### Issue 1: "Showing 0 of X alerts"
**Fix:** Refresh page (F5), check backend is running

### Issue 2: Pages load but show "Loading..."
**Fix:** Check backend is running at port 8000

### Issue 3: Clicking sidebar does nothing
**Fix:** 
1. Check browser console for errors
2. Hard refresh: Ctrl+Shift+R
3. Clear cache and reload

### Issue 4: Assets page shows "No Assets Found"
**This is normal!** Assets page generates 8 mock assets automatically.
Just refresh the page.

### Issue 5: Simulation Lab doesn't start
**Fix:** Check backend is running, click Start button again

## ✅ Confirmation Checklist

Go through each page and check:
- [ ] Overview - Shows dashboard
- [ ] Live Traffic - Shows flows table
- [ ] Threat Alerts - Shows 15 alerts
- [ ] Attack Timeline - Shows 3 incidents
- [ ] Assets - Shows 8 asset cards
- [ ] Simulation Lab - Shows 6 scenarios
- [ ] System Health - Shows green status

## Still Not Working?

Share:
1. **Screenshot** of what you see
2. **Browser console errors** (F12 → Console tab)
3. **Which page** is not working
4. **What happens** when you click the sidebar link
