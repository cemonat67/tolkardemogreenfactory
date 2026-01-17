import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging, time
from config import settings
from api import state as state_router
from api import control as control_router
from api import telemetry as telemetry_router
from api import events as events_router
from api import auth as auth_router

logging.basicConfig(level=logging.INFO if settings.DEBUG_MODE else logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEMO_MODE:
        from services.simulator import initialize_demo_factory
        initialize_demo_factory()
    yield

app = FastAPI(title="TOLKAR ZERO@FACTORY API", description="Real-time production monitoring & digital twin platform", version="1.0.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response

app.include_router(state_router.router, prefix="/api", tags=["Factory State"])
app.include_router(control_router.router, prefix="/api", tags=["Control Actions"])
app.include_router(telemetry_router.router, prefix="/api", tags=["Telemetry"])
app.include_router(events_router.router, prefix="/api", tags=["Events"])
app.include_router(auth_router.router, prefix="/api", tags=["Auth"])
app.include_router(auth_router.router_public, prefix="/api", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "TOLKAR ZERO@FACTORY API", "version": "1.0.0", "status": "operational", "demo_mode": settings.DEMO_MODE, "endpoints": {"docs": "/docs", "state": "/api/state", "telemetry": "/api/telemetry", "events": "/api/events", "control": "/api/reset, /api/shock, /api/kaizen"}}

@app.get("/health")
def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "demo_mode": settings.DEMO_MODE}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(exc) if settings.DEBUG_MODE else "An error occurred", "path": str(request.url)})
