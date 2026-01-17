"""
TOLKAR Zero@Factory - FastAPI Backend
Production Intelligence Platform for Smartex Machines
Phase 9.5 - Production Ready
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import uuid
import logging
from typing import Optional, List, Dict, Any

# Import our modules
from models import (
    User, Station, ProductionRun, Telemetry, 
    MaintenanceLog, SystemEvent, SessionLocal
)
from auth import AuthService
from database import get_db, init_db, health_check

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TOLKAR Zero@Factory API",
    description="Production Intelligence Platform for Smartex Industrial Washing Machines",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
auth_service = AuthService()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserInfoResponse(BaseModel):
    user_id: str
    username: str
    role: str
    exp: str

class ProductionState(BaseModel):
    stations: List[Dict[str, Any]]
    telemetry: Dict[str, Any]
    timestamp: str

class MaintenanceRequest(BaseModel):
    maintenance_type: str
    description: str
    duration_minutes: int
    parts_replaced: Optional[str] = None
    cost_eur: Optional[float] = None

class ErrorResponse(BaseModel):
    detail: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default users"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check_endpoint():
    """System health check with database status"""
    try:
        db_status = health_check()
        return {
            "status": "healthy",
            "service": "TOLKAR Zero@Factory API v2.0",
            "database": {
                "status": "healthy" if db_status else "unhealthy",
                "database": "connected" if db_status else "disconnected"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

# Config endpoint
@app.get("/api/config", response_model=Dict[str, Any])
async def get_config():
    """Get system configuration"""
    return {
        "app": "TOLKAR Zero@Factory",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "authentication": True,
            "persistent_state": True,
            "audit_logging": True,
            "telemetry": True
        }
    }

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    try:
        user = auth_service.verify_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Role-based access control
def require_role(allowed_roles: List[str]):
    """Dependency to check user role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Login endpoint
@app.post("/api/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        user = auth_service.authenticate_user(login_request.username, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = auth_service.create_access_token(data={"sub": user.username})
        
        # Log successful login
        with SessionLocal() as db:
            event = SystemEvent(
                id=str(uuid.uuid4()),
                event_type="login",
                label=f"User {user.username} logged in",
                severity="info"
            )
            db.add(event)
            db.commit()
        
        return LoginResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# Get current user info
@app.get("/api/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserInfoResponse(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        exp=(datetime.utcnow() + timedelta(hours=8)).isoformat()
    )

# Production state endpoint
@app.get("/api/state", response_model=ProductionState)
async def get_production_state(current_user: User = Depends(get_current_user)):
    """Get current production state with telemetry"""
    try:
        with SessionLocal() as db:
            # Get all stations
            stations = db.query(Station).all()
            
            # Get latest telemetry data
            latest_telemetry = db.query(Telemetry).order_by(Telemetry.recorded_at.desc()).first()
            
            # Build response
            stations_data = []
            for station in stations:
                # Get latest production run for this station
                latest_run = db.query(ProductionRun).filter(
                    ProductionRun.station_id == station.id
                ).order_by(ProductionRun.created_at.desc()).first()
                
                stations_data.append({
                    "id": station.id,
                    "name": station.name,
                    "wip": latest_run.wip if latest_run else station.wip_baseline,
                    "ct": latest_run.ct if latest_run else station.ct_baseline,
                    "fpy": latest_run.fpy if latest_run else station.fpy_baseline,
                    "oee": latest_run.oee if latest_run else station.oee_baseline,
                    "status": latest_run.status if latest_run else station.status
                })
            
            # Build telemetry data
            telemetry_data = {
                "vibration": latest_telemetry.vibration_mms if latest_telemetry else 2.3,
                "temperature": latest_telemetry.temperature_c if latest_telemetry else 78,
                "pressure": latest_telemetry.pressure_bar if latest_telemetry else 6.2,
                "power": latest_telemetry.power_kw_idx if latest_telemetry else 85,
                "history": {
                    "vibration": [2.0, 2.1, 2.2, 2.3],
                    "temperature": [80, 79, 78, 78],
                    "pressure": [5.9, 6.0, 6.1, 6.2],
                    "power": [81, 82, 84, 85]
                }
            }
            
            return ProductionState(
                stations=stations_data,
                telemetry=telemetry_data,
                timestamp=datetime.utcnow().isoformat()
            )
    except Exception as e:
        logger.error(f"Failed to get production state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve production state"
        )

# Reset all stations to baseline
@app.post("/api/reset", response_model=Dict[str, Any])
async def reset_stations(
    current_user: User = Depends(require_role(["admin", "supervisor"]))
):
    """Reset all production stations to baseline values"""
    try:
        with SessionLocal() as db:
            # Get all stations
            stations = db.query(Station).all()
            
            for station in stations:
                # Create new production run with baseline values
                production_run = ProductionRun(
                    id=str(uuid.uuid4()),
                    station_id=station.id,
                    batch_number=f"RESET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    wip=station.wip_baseline,
                    ct=station.ct_baseline,
                    fpy=station.fpy_baseline,
                    oee=station.oee_baseline,
                    status="ok"
                )
                db.add(production_run)
            
            # Log the reset action
            event = SystemEvent(
                id=str(uuid.uuid4()),
                event_type="reset",
                label=f"All stations reset to baseline by {current_user.username}",
                severity="info"
            )
            db.add(event)
            
            db.commit()
        
        return {
            "status": "success",
            "message": "All stations reset to baseline",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset stations"
        )

# Simulate disruption (shock)
@app.post("/api/shock", response_model=Dict[str, Any])
async def simulate_disruption(current_user: User = Depends(get_current_user)):
    """Simulate production disruption (create bottleneck)"""
    try:
        with SessionLocal() as db:
            # Find finishing station (typically station 4 or 5)
            finishing_station = db.query(Station).filter(
                Station.name.ilike("%finishing%")
            ).first()
            
            if not finishing_station:
                # Fallback to last station
                finishing_station = db.query(Station).order_by(Station.id.desc()).first()
            
            # Create disruption
            production_run = ProductionRun(
                id=str(uuid.uuid4()),
                station_id=finishing_station.id,
                batch_number=f"SHOCK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                wip=8,  # High WIP indicates bottleneck
                ct=finishing_station.ct_baseline + 15,  # Increased cycle time
                fpy=finishing_station.fpy_baseline - 5,  # Reduced FPY
                oee=finishing_station.oee_baseline - 8,  # Reduced OEE
                status="bottleneck",
                disruption_type="simulated_bottleneck"
            )
            db.add(production_run)
            
            # Log the shock event
            event = SystemEvent(
                id=str(uuid.uuid4()),
                event_type="shock",
                station_id=finishing_station.id,
                label=f"Bottleneck detected @ {finishing_station.name}",
                severity="critical"
            )
            db.add(event)
            
            db.commit()
        
        return {
            "status": "success",
            "message": "Disruption simulated",
            "disruption": f"{finishing_station.name} station bottleneck",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Shock simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to simulate disruption"
        )

# Apply improvement (kaizen)
@app.post("/api/kaizen", response_model=Dict[str, Any])
async def apply_kaizen(
    current_user: User = Depends(require_role(["admin", "supervisor"]))
):
    """Apply Kaizen improvement to reduce WIP and improve metrics"""
    try:
        with SessionLocal() as db:
            # Get all stations
            stations = db.query(Station).all()
            
            improvements = {
                "wip_reduced": False,
                "fpy_improved": False,
                "oee_improved": False
            }
            
            for station in stations:
                # Get current state
                latest_run = db.query(ProductionRun).filter(
                    ProductionRun.station_id == station.id
                ).order_by(ProductionRun.created_at.desc()).first()
                
                current_wip = latest_run.wip if latest_run else station.wip_baseline
                current_fpy = latest_run.fpy if latest_run else station.fpy_baseline
                current_oee = latest_run.oee if latest_run else station.oee_baseline
                
                # Apply improvements
                improved_wip = max(1, current_wip - 2)  # Reduce WIP by 2, minimum 1
                improved_fpy = min(99.5, current_fpy + 1.5)  # Improve FPY by 1.5%, max 99.5%
                improved_oee = min(98.0, current_oee + 2.0)  # Improve OEE by 2%, max 98%
                
                # Create improvement run
                production_run = ProductionRun(
                    id=str(uuid.uuid4()),
                    station_id=station.id,
                    batch_number=f"KAIZEN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    wip=improved_wip,
                    ct=station.ct_baseline,  # Back to baseline cycle time
                    fpy=improved_fpy,
                    oee=improved_oee,
                    status="ok",
                    disruption_type=None
                )
                db.add(production_run)
                
                # Track improvements
                if improved_wip < current_wip:
                    improvements["wip_reduced"] = True
                if improved_fpy > current_fpy:
                    improvements["fpy_improved"] = True
                if improved_oee > current_oee:
                    improvements["oee_improved"] = True
            
            # Log the kaizen event
            event = SystemEvent(
                id=str(uuid.uuid4()),
                event_type="kaizen",
                label=f"Kaizen improvement applied by {current_user.username}",
                severity="info"
            )
            db.add(event)
            
            db.commit()
        
        return {
            "status": "success",
            "message": "Kaizen improvement completed",
            "improvements": improvements,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Kaizen failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply Kaizen improvement"
        )

# Get system events
@app.get("/api/events", response_model=List[Dict[str, Any]])
async def get_events(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get system events (audit trail)"""
    try:
        with SessionLocal() as db:
            events = db.query(SystemEvent).order_by(
                SystemEvent.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "station_id": event.station_id,
                    "label": event.label,
                    "severity": event.severity,
                    "created_at": event.created_at.isoformat()
                }
                for event in events
            ]
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events"
        )

# Get maintenance logs for a station
@app.get("/api/maintenance/{station_id}", response_model=List[Dict[str, Any]])
async def get_maintenance_logs(
    station_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get maintenance logs for a specific station"""
    try:
        with SessionLocal() as db:
            logs = db.query(MaintenanceLog).filter(
                MaintenanceLog.station_id == station_id
            ).order_by(MaintenanceLog.created_at.desc()).all()
            
            return [
                {
                    "id": log.id,
                    "station_id": log.station_id,
                    "maintenance_type": log.maintenance_type,
                    "description": log.description,
                    "duration_minutes": log.duration_minutes,
                    "parts_replaced": log.parts_replaced,
                    "cost_eur": log.cost_eur,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
    except Exception as e:
        logger.error(f"Failed to get maintenance logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve maintenance logs"
        )

# Log maintenance work
@app.post("/api/maintenance/{station_id}", response_model=Dict[str, Any])
async def log_maintenance(
    station_id: int,
    maintenance_request: MaintenanceRequest,
    current_user: User = Depends(require_role(["admin", "supervisor"]))
):
    """Log maintenance work for a station"""
    try:
        with SessionLocal() as db:
            # Verify station exists
            station = db.query(Station).filter(Station.id == station_id).first()
            if not station:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Station not found"
                )
            
            # Create maintenance log
            maintenance_log = MaintenanceLog(
                id=str(uuid.uuid4()),
                station_id=station_id,
                maintenance_type=maintenance_request.maintenance_type,
                description=maintenance_request.description,
                duration_minutes=maintenance_request.duration_minutes,
                parts_replaced=maintenance_request.parts_replaced,
                cost_eur=maintenance_request.cost_eur
            )
            db.add(maintenance_log)
            
            # Log the maintenance event
            event = SystemEvent(
                id=str(uuid.uuid4()),
                event_type="maintenance",
                station_id=station_id,
                label=f"Maintenance logged by {current_user.username}: {maintenance_request.maintenance_type}",
                severity="info"
            )
            db.add(event)
            
            db.commit()
            
            return {
                "id": maintenance_log.id,
                "station_id": maintenance_log.station_id,
                "maintenance_type": maintenance_log.maintenance_type,
                "description": maintenance_log.description,
                "duration_minutes": maintenance_log.duration_minutes,
                "parts_replaced": maintenance_log.parts_replaced,
                "cost_eur": maintenance_log.cost_eur,
                "created_at": maintenance_log.created_at.isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Maintenance logging failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log maintenance"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    init_db()
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )