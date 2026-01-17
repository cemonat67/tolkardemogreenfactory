import time
from datetime import datetime
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.requests import Request
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from config import settings
from services.simulator import initialize_demo_factory, get_demo_state, reset_demo_factory, apply_demo_shock, apply_demo_kaizen

async def health(request: Request):
    return JSONResponse({"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "demo_mode": settings.DEMO_MODE})

async def root(request: Request):
    return JSONResponse({"message": "TOLKAR ZERO@FACTORY API (starlette)", "version": "1.0.0"})

async def state(request: Request):
    return JSONResponse(get_demo_state())

async def events(request: Request):
    data = get_demo_state()
    return JSONResponse(data.get("events", []))

async def telemetry(request: Request):
    # Stub telemetry; in demo, return empty series
    return JSONResponse([])

async def reset(request: Request):
    return JSONResponse({"success": True, "message": "Factory reset to initial state", "new_state": reset_demo_factory()})

async def shock(request: Request):
    body = await request.json()
    res = apply_demo_shock(station_id=body.get("station_id"), shock_type=body.get("shock_type", "quality_issue"), severity=body.get("severity", "medium"))
    return JSONResponse(res)

async def kaizen(request: Request):
    body = await request.json()
    res = apply_demo_kaizen(station_id=body.get("station_id", 3), improvement_type=body.get("improvement_type", "cycle_time_reduction"), improvement_pct=float(body.get("improvement_pct", 10)))
    return JSONResponse(res)

routes = [
    Route("/", root),
    Route("/health", health),
    Route("/api/state", state),
    Route("/api/events", events),
    Route("/api/telemetry", telemetry),
    Route("/api/reset", reset, methods=["POST"]),
    Route("/api/shock", shock, methods=["POST"]),
    Route("/api/kaizen", kaizen, methods=["POST"]),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
]

app = Starlette(debug=settings.DEBUG_MODE, routes=routes, middleware=middleware)

@app.middleware("http")
async def process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

if settings.DEMO_MODE:
    initialize_demo_factory()

# Serve UI and assets from same origin to avoid mixed content
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/ui", StaticFiles(directory=".", html=True), name="ui")

# API v1 contract
def reason_label(code: str) -> str:
    m = {
        "RC10": "Malzeme bekliyor",
        "RC11": "Makine arızası",
        "RC12": "Operatör bekliyor",
        "RC13": "Kalite red bekliyor",
        "RC14": "Bakım planlı duruş",
    }
    return m.get(code or "", "Bilinmiyor")

def build_lines_v1():
    d = get_demo_state()
    stations = d.get("stations", [])
    ts = d.get("timestamp")
    site_id = "tolkar_aosb"
    lines_def = [
        {"line_id": 1, "line_name": "Metal & Şase"},
        {"line_id": 2, "line_name": "Boya Hattı"},
        {"line_id": 3, "line_name": "Montaj"},
        {"line_id": 4, "line_name": "Final Test"},
        {"line_id": 5, "line_name": "Paketleme & Sevkiyat"},
    ]
    def map_line(name: str) -> int:
        n=(name or "").lower()
        if "metal" in n or "şa" in n: return 1
        if "boya" in n or "paint" in n: return 2
        if "montaj" in n or "assembly" in n: return 3
        if "test" in n: return 4
        if "paket" in n or "sevkiyat" in n: return 5
        return 3
    groups = {ld["line_id"]: {"line_id": ld["line_id"], "line_name": ld["line_name"], "status": "Idle", "wip": 0, "throughput_ph": 0, "ct_min": 0, "oee": 0, "fpy": 0, "bottleneck_station": None, "last_event": None, "_count": 0} for ld in lines_def}
    for s in stations:
        lid = map_line(s.get("name"))
        g = groups.get(lid)
        if not g: continue
        g["wip"] += int(s.get("wip") or 0)
        g["ct_min"] += int(round(((s.get("cycle_time_sec") or 0)/60)))
        g["oee"] += float(s.get("oee") or 0)
        g["fpy"] += float(s.get("fpy") or 0)
        if str(s.get("status")).lower() == "critical" or s.get("bottleneck"):
            g["bottleneck_station"] = s.get("name")
        g["_count"] += 1
    ev = (d.get("events") or [])
    last_ev = ev[0] if ev else None
    for lid, g in groups.items():
        c = g.pop("_count")
        if c > 0:
            g["ct_min"] = int(round(g["ct_min"]/c))
            g["oee"] = int(round(g["oee"]/c))
            g["fpy"] = int(round(g["fpy"]/c))
            g["throughput_ph"] = int(round(60/max(g["ct_min"],1)))
            g["status"] = "Running" if g["oee"] >= 70 and g["wip"] > 0 else ("Idle" if g["wip"]==0 else "Down")
            if g.get("bottleneck_station"): g["status"] = "Blocked"
        else:
            g.update({"ct_min":0,"oee":0,"fpy":0,"throughput_ph":0,"status":"Idle"})
        if last_ev:
            rc = "RC12"
            g["last_event"] = {"ts": last_ev.get("timestamp"), "type": last_ev.get("event_type"), "reason_code": rc, "since_ts": last_ev.get("timestamp")}
        else:
            g["last_event"] = {"ts": ts, "type": "info", "reason_code": "RC10", "since_ts": ts}
    return {"ts": ts, "site_id": site_id, "last_sync": ts, "lines": list(groups.values())}

def build_stations_v1():
    d = get_demo_state()
    stations = d.get("stations", [])
    res=[]
    for idx, s in enumerate(stations, start=1):
        res.append({
            "station_id": idx,
            "station_name": s.get("name"),
            "line_id": 3,
            "status": "bottleneck" if s.get("bottleneck") else (str(s.get("status") or "ok")),
            "wip": int(s.get("wip") or 0),
            "ct_sec": int(s.get("cycle_time_sec") or 0),
            "downtime_sec": 0,
            "reason_code": "RC12" if s.get("bottleneck") else "",
            "updated_ts": d.get("timestamp")
        })
    return {"ts": d.get("timestamp"), "site_id": "tolkar_aosb", "last_sync": d.get("timestamp"), "stations": res}

def build_events_v1():
    d = get_demo_state()
    ev = []
    for e in d.get("events", []):
        ev.append({
            "ts": e.get("timestamp"),
            "type": e.get("event_type"),
            "site_id": "tolkar_aosb",
            "line_id": 3,
            "station_id": e.get("station_id"),
            "status": e.get("severity"),
            "reason_code": "RC12",
            "payload": {"message": e.get("message")}
        })
    return {"ts": d.get("timestamp"), "site_id": "tolkar_aosb", "last_sync": d.get("timestamp"), "events": ev}

async def status_v1(request: Request):
    # Use the exact same sources as /api/v1/lines and /api/v1/events
    def get_lines_data():
        return _use_seed_lines() or build_lines_v1()
    def get_events_data():
        return _use_seed_events() or build_events_v1()
    LD = get_lines_data()
    ED = get_events_data()
    lines = LD.get("lines", [])
    events = ED.get("events", [])
    # last_sync: prefer seed's last_sync, else demo timestamp
    last_sync = SEED.get("last_sync") or LD.get("last_sync")
    health = "ok"
    reason = ""
    if not lines:
        health = "degraded"; reason = "lines_empty"
    elif not events:
        health = "degraded"; reason = "events_empty"
    else:
        # optional stale check (pilot): seed older than 2 hours
        try:
            from datetime import datetime, timezone
            if SEED.get("last_sync"):
                t = datetime.fromisoformat(SEED["last_sync"].replace("Z","+00:00"))
                age = (datetime.now(timezone.utc) - t).total_seconds()
                if age > 2*60*60:
                    health = "degraded"; reason = "stale_seed"
        except Exception:
            pass
    return JSONResponse({"ts": last_sync, "site_id": "tolkar_aosb", "last_sync": last_sync, "health": health, "reason": reason})

async def lines_v1(request: Request):
    return JSONResponse(_use_seed_lines() or build_lines_v1())

async def stations_v1(request: Request):
    return JSONResponse(_use_seed_stations() or build_stations_v1())

async def events_v1(request: Request):
    return JSONResponse(_use_seed_events() or build_events_v1())

app.add_route("/api/v1/status", status_v1)
app.add_route("/api/v1/lines", lines_v1)
app.add_route("/api/v1/stations", stations_v1)
app.add_route("/api/v1/events", events_v1)

# Seed storage
SEED = {"lines": None, "stations": None, "events": None, "orders": None, "last_sync": None}

async def seed_status(request: Request):
    return JSONResponse({"has_seed": bool(SEED["lines"] or SEED["stations"] or SEED["events"]), "last_sync": SEED["last_sync"]})

async def seed_upload(request: Request):
    payload = await request.json()
    SEED["lines"] = payload.get("lines")
    SEED["stations"] = payload.get("stations")
    SEED["events"] = payload.get("events")
    SEED["orders"] = payload.get("orders")
    from datetime import datetime
    SEED["last_sync"] = datetime.utcnow().isoformat()
    return JSONResponse({"success": True, "last_sync": SEED["last_sync"]})

app.add_route("/api/v1/seed/status", seed_status)
app.add_route("/api/v1/seed/upload", seed_upload, methods=["POST"])

# Override builders if seed exists
def _use_seed_lines():
    return bool(SEED["lines"]) and {"ts": SEED.get("last_sync"), "site_id": "tolkar_aosb", "last_sync": SEED.get("last_sync"), "lines": SEED["lines"]}

def _use_seed_stations():
    return bool(SEED["stations"]) and {"ts": SEED.get("last_sync"), "site_id": "tolkar_aosb", "last_sync": SEED.get("last_sync"), "stations": SEED["stations"]}

def _use_seed_events():
    return bool(SEED["events"]) and {"ts": SEED.get("last_sync"), "site_id": "tolkar_aosb", "last_sync": SEED.get("last_sync"), "events": SEED["events"]}

def _use_seed_orders():
    return bool(SEED["orders"]) and {"ts": SEED.get("last_sync"), "site_id": "tolkar_aosb", "last_sync": SEED.get("last_sync"), "orders": SEED["orders"]}

def build_orders_v1():
    d = get_demo_state()
    ts = d.get("timestamp")
    lines = build_lines_v1().get("lines", [])
    out = []
    def mk(order_id, lid, sid, state, energy, co2, risk, rc, note):
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat()
        return {
            "order_id": order_id,
            "line_id": lid,
            "station_id": sid,
            "state": state,
            "start_ts": ts,
            "updated_ts": now,
            "elapsed_min": 30.0,
            "energy_kwh": energy,
            "co2e_kg": co2,
            "scrap_units": 0,
            "rework_units": 0,
            "eta_ts": now,
            "risk": risk,
            "reason_code": rc,
            "payload": {"note": note}
        }
    blocked_boya = any((l for l in lines if l.get("line_name")=="Boya Hattı" and l.get("status")=="Down"))
    out.append(mk("ORD-2026-0001", 3, 3, "moving", 4.0, 1.8, "ok", "", "Montaj akışta"))
    out.append(mk("ORD-2026-0002", 3, 3, "processing", 4.5, 2.0, "ok", "", "Montaj istasyonda"))
    out.append(mk("ORD-2026-0003", 5, 1, "waiting", 2.2, 1.0, "at_risk", "RC10", "Paketleme bekliyor"))
    out.append(mk("ORD-2026-0004", 1, 1, "moving", 3.1, 1.4, "ok", "", "Metal & Şase akışta"))
    if blocked_boya:
        out.append(mk("ORD-2026-0005", 2, 2, "down", 2.9, 1.2, "late", "RC11", "Boya hattı arıza"))
        out.append(mk("ORD-2026-0006", 2, 2, "blocked", 2.0, 0.9, "at_risk", "RC11", "Boya bekliyor"))
    else:
        out.append(mk("ORD-2026-0005", 2, 2, "moving", 2.3, 1.0, "ok", "", "Boya akışta"))
    return {"ts": ts, "site_id": "tolkar_aosb", "last_sync": ts, "orders": out[:8]}

async def orders_v1(request: Request):
    return JSONResponse(_use_seed_orders() or build_orders_v1())

app.add_route("/api/v1/orders", orders_v1)

# Demo auth endpoints
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "supervisor": {"password": "supervisor123", "role": "supervisor"},
    "operator1": {"password": "operator123", "role": "operator"},
}
TOKENS = {}

async def login(request: Request):
    payload = await request.json()
    u = (payload.get("username") or "").strip()
    p = payload.get("password") or ""
    rec = USERS.get(u)
    if not rec or rec["password"] != p:
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)
    import secrets
    token = secrets.token_hex(16)
    TOKENS[token] = {"username": u, "role": rec["role"]}
    return JSONResponse({"access_token": token, "user": {"username": u, "role": rec["role"]}})

async def me(request: Request):
    auth = request.headers.get("Authorization") or ""
    parts = auth.split()
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else None
    user = token and TOKENS.get(token)
    if not user:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return JSONResponse({"user": user})

app.add_route("/api/login", login, methods=["POST"])
app.add_route("/api/me", me)
