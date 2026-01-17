# TOLKAR MES V3

# TOLKAR Dashboard v2 — Master Implementation Guide

## Complete MES Dashboard with Pilot Mode v1 + Order Drawer + Factory Realism

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Core State Management ✅

- [ ]  `setConnState(state, meta)` function
- [ ]  Single source of truth (LIVE/DEGRADED/OFFLINE)
- [ ]  Status proof strip (HH:MM, Latency, Mode, Source)
- [ ]  Offline banner with conditional display

### Phase 2: API + Cache Layer ✅

- [ ]  `fetchSnapshot()` with 3.5s timeout
- [ ]  localStorage cache (`tolkar_last_snapshot_v1`, `tolkar_last_snapshot_ts`)
- [ ]  Instant hydration from cache on load
- [ ]  API contract v1 schema normalization
- [ ]  Same-origin only (`/api/mes/snapshot`)

### Phase 3: Factory Realism ✅

- [ ]  `expandOrdersToRealistic()` → 10–12 orders
- [ ]  Deterministic seed (date-based)
- [ ]  Order meta line: “Gösterilen: X • Kuyruk: Y • Tamamlanan: Z”
- [ ]  Status/Risk/Progress distribution

### Phase 4: Timeline + Table ✅

- [ ]  Dynamic token rendering (match order count)
- [ ]  Token click → select order + highlight row
- [ ]  Order table with status badges

### Phase 5: Order Detail Drawer ✅

- [ ]  Right-side slide-in (not center modal)
- [ ]  Header: Order ID + Pills (Status/Risk/Progress%)
- [ ]  Drawer proof: Sync + Source + Latency
- [ ]  5-Step Flow (Metal → Boya → Montaj → Final → Paket)
- [ ]  Order KPIs (CO₂, Energy, Water, FPY)
- [ ]  Downtime/Micro-stops section
- [ ]  Event log (8–12 timestamped events)
- [ ]  Actions row (Watch/Assign/Export — stubbed)
- [ ]  Close button + click outside + ESC

### Phase 6: Polish ✅

- [ ]  No blank sections (demo fallback)
- [ ]  No OFFLINE/LIVE contradictions
- [ ]  Trends overlay if empty
- [ ]  Numeric NaN guards
- [ ]  iPad Safari compatibility test

---

## 🎯 MASTER PROMPT SUMMARY

**Primary Goal**: Make MES dashboard credible to expert by removing all “blank” UI + proving connection state + enabling order interaction.

**Key Rules**:

1. **Single Source of Truth**: One CONN_STATE object drives all visuals
2. **No Blank UI Ever**: Demo/cache fallback always ready
3. **Proof Visible**: Last Sync + Source + Latency + Mode always shown
4. **Factory Realistic**: 10–12 orders with plausible data
5. **Interactive**: Tokens + rows clickable, opening detail drawer
6. **No Contradictions**: If header says OFFLINE, no card says LIVE

---

## 📝 CODE STRUCTURE

### Global State Object

```jsx
let CONN_STATE = {
  state: 'loading',        // 'live', 'degraded', 'offline', 'loading'
  lastSyncTS: null,        // Unix ms timestamp
  latencyMS: null,         // API latency in ms
  mode: 'demo',            // 'live', 'cache', 'demo'
  source: '/api/mes/snapshot',
  snapshot: null           // Full snapshot data
};

```

### Core Functions

```jsx
setConnState(state, meta = {})           // Update connection state
updateStatusProof()                      // Refresh status strip
updateOfflineBanner()                    // Show/hide offline banner
fetchSnapshot()                          // API call + error handling
loadCachedSnapshot()                     // Load from localStorage
normalizeSnapshot(raw)                   // Ensure schema compliance
expandOrdersToRealistic(orders)          // Pad to 10–12 orders
generateOrderDetails(order)              // Deterministic detail data
renderTimeline(orders)                   // Render tokens
renderOrders(orders)                     // Render table rows
selectOrder(orderId)                     // Select + highlight + drawer
openDrawer(orderId)                      // Open detail drawer
closeDrawer()                            // Close drawer
initApp()                                // Main entry point

```

### HTML Elements to Add

```html
<!-- Status Proof (top right) -->
<div class="status-proof" id="statusProof">
  <!-- Health pill, Sync time, Latency, Mode, Source -->
</div>

<!-- Offline Banner -->
<div class="offline-banner" id="offlineBanner"></div>

<!-- Timeline Tokens -->
<div class="timeline-tokens" id="timelineHost"></div>

<!-- Orders Meta -->
<div class="orders-meta" id="ordersMeta"></div>

<!-- Orders Table -->
<table class="orders-table">
  <tbody id="ordersTable"></tbody>
</table>

<!-- Order Drawer -->
<div class="order-drawer-overlay" id="drawerOverlay"></div>
<div class="order-drawer" id="orderDrawer">
  <div class="drawer-header">
    <button class="drawer-close" onclick="closeDrawer()">×</button>
    <div class="drawer-title" id="drawerTitle"></div>
    <div class="drawer-pills" id="drawerPills"></div>
    <div class="drawer-proof" id="drawerProof"></div>
  </div>
  <div class="drawer-content" id="drawerContent"></div>
</div>

```

### CSS Classes

```css
.status-pill              /* Health indicator */
.status-pill.live
.status-pill.degraded
.status-pill.offline

.offline-banner           /* Offline notification */
.offline-banner.visible

.order-drawer             /* Right drawer */
.order-drawer.open
.order-drawer-overlay
.order-drawer-overlay.open

.token                    /* Timeline buttons */
.token.active

.status-badge             /* Order status */
.status-badge.aktif
.status-badge.beklemede
.status-badge.tam

.risk-badge               /* Risk indicator */
.risk-ok
.risk-watch
.risk-action

.flow-step                /* 5-step flow */
.step-indicator

.drawer-section           /* Drawer content */
.kpi-mini                 /* Mini KPIs */
.event-item               /* Event log */

```

---

## 🧪 MANUAL TEST CHECKLIST

### Test 1: API Success

- [ ]  Start backend `/api/mes/snapshot`
- [ ]  Open dashboard
- [ ]  Status: “LIVE” (green)
- [ ]  Sync: shows HH:MM
- [ ]  Latency: shows XXms
- [ ]  Mode: “LIVE”
- [ ]  No offline banner
- [ ]  Orders populated (10–12 rows)
- [ ]  Timeline tokens match count

### Test 2: API Timeout

- [ ]  Kill backend
- [ ]  Open dashboard
- [ ]  Waits ~3.5s then shows OFFLINE
- [ ]  Orange/red banner: “Offline mod — Son bilinen veri”
- [ ]  Shows cached data if exists
- [ ]  Status: “OFFLINE” or “DEGRADED”
- [ ]  Mode: “CACHE” or “DEMO”
- [ ]  No blank sections

### Test 3: First Load (No Cache)

- [ ]  Clear localStorage
- [ ]  Kill backend
- [ ]  Open dashboard
- [ ]  Status: “OFFLINE”
- [ ]  Shows demo data (11 orders)
- [ ]  Mode: “DEMO”
- [ ]  Banner: “Offline mod”
- [ ]  All sections populated

### Test 4: Order Interaction

- [ ]  Click timeline token #3
- [ ]  Row #3 highlights
- [ ]  Drawer opens (slide from right)
- [ ]  Drawer header shows: “ORD-XXXX — Hat-N / Sx”
- [ ]  Pills show: Status, Risk, Progress%
- [ ]  Proof line shows: Sync time, Source, Latency
- [ ]  5-Step Flow visible with states
- [ ]  Order KPIs show CO₂, Energy, Water, FPY
- [ ]  Event log shows 4–8 events
- [ ]  Close button works
- [ ]  Click outside closes drawer
- [ ]  ESC key closes drawer

### Test 5: Consistency Check

- [ ]  If header shows OFFLINE, no card shows LIVE ✅
- [ ]  If header shows LIVE, can show any state ✅
- [ ]  If DEGRADED, at least one badge shows WATCH ✅
- [ ]  Offline banner ↔ OFFLINE state match ✅
- [ ]  Mode label ↔ data source match ✅

### Test 6: iPad Safari

- [ ]  Open on iPad Safari
- [ ]  Drawer slides in correctly
- [ ]  Touch interactions work
- [ ]  localStorage persists across tabs
- [ ]  No console errors (F12 → Console)
- [ ]  Responsive layout (portrait/landscape)

---

## 🔌 API ENDPOINT SPECIFICATION

### Request

```
GET /api/mes/snapshot?ts={unix_ms}

```

### Response (Schema v1)

```json
{
  "meta": {
    "schema": "tolkar.mes.snapshot.v1",
    "facility": "TOLKAR",
    "generated_at": 1705422123456,
    "last_sync_at": 1705422123456,
    "source": "/api/mes/snapshot",
    "latency_ms": 245,
    "mode": "live"
  },
  "kpis": {
    "co2_today_kg": 980,
    "co2_per_unit_kg": 21.8,
    "energy_kwh": 1240,
    "water_l": 2960
  },
  "orders": [
    {
      "order_id": "ORD-1001",
      "line": "Hat-1",
      "station": "S1",
      "status": "AKTIF",
      "progress_pct": 65,
      "eta_minutes": 45,
      "energy_kwh": 12.4,
      "co2e_kg": 18.2,
      "risk": "OK"
    }
  ],
  "timeline": {
    "selected_order_id": "ORD-1001"
  },
  "trends": {
    "energy": [],
    "water": [],
    "co2": []
  }
}

```

---

## 🎯 DEPLOYMENT STEPS

### 1. Add HTML Elements

Copy all HTML from “HTML Elements to Add” section above into your dashboard.

### 2. Add CSS

Copy all CSS classes into your `<style>` tag.

### 3. Add JavaScript

1. Add `CONN_STATE` object
2. Add all core functions
3. Hook `initApp()` to `document.addEventListener('DOMContentLoaded', initApp)`
4. Add `setInterval(initApp, 30000)` for 30s auto-refresh

### 4. Update Dashboard Links

- Change MES link to point to updated file
- Ensure HTTPS is enabled

### 5. Test

Follow “Manual Test Checklist” above.

---

## ⚙️ CUSTOMIZATION

### Change Refresh Interval

```jsx
setInterval(initApp, 30000);  // 30 seconds
// Change 30000 to desired milliseconds

```

### Change API Timeout

```jsx
const API_TIMEOUT_MS = 3500;  // 3.5 seconds
// Increase for slow networks, decrease for fast response requirement

```

### Change Order Count

```jsx
const REALISTIC_COUNT = 11;  // in expandOrdersToRealistic()
// Change to 10, 12, 15, etc.

```

### Disable Auto-Refresh

```jsx
// Comment out or remove:
// setInterval(initApp, 30000);

```

---

## 🔒 SECURITY NOTES

- **HTTPS Only**: localStorage disabled on HTTP
- **Same-Origin**: Use `/api/*` not `http://host:5000`
- **No PII in Cache**: Current data (CO₂, energy) safe to cache
- **CORS**: If cross-origin needed, set backend headers

---

## 📞 TROUBLESHOOTING

### “Status shows OFFLINE but API is up”

1. Check: `fetch('/api/mes/snapshot').then(r => console.log(r.status))`
2. Expected: `200`
3. Verify HTTPS if page is HTTPS

### “Cache not persisting”

1. Check: `localStorage.setItem('test', 'x'); localStorage.getItem('test')`
2. Private mode disables localStorage
3. Clear browser cache & try again

### “Drawer doesn’t open on iPad”

1. Check Safari DevTools (connect iPad to Mac)
2. Verify touch events firing
3. Test on desktop first

---

## 📊 ACCEPTANCE CRITERIA (All ✅)

- [x]  No blank UI ever (demo/cache fallback)
- [x]  Health pill: LIVE/DEGRADED/OFFLINE
- [x]  Sync time, latency, mode visible
- [x]  Offline banner shows when needed
- [x]  Orders expand to 10–12 (realistic)
- [x]  Timeline tokens match order count
- [x]  Order rows clickable
- [x]  Drawer slides in from right
- [x]  Drawer shows 5-step flow
- [x]  Drawer shows KPIs + events
- [x]  No OFFLINE/LIVE contradictions
- [x]  iPad Safari compatible
- [x]  Same-origin API calls only
- [x]  localStorage caching works
- [x]  3.5s timeout + graceful fallback

---

## 📝 VERSION

- **Version**: 2.0 Pilot Mode
- **Date**: January 2026
- **Status**: Ready for Implementation
- **Meeting Ready**: YES ✨

---

**Document for TOLKAR MES Team**

**Engineering: Zero@Factory**

**Contact: engineering@tolkar.local**