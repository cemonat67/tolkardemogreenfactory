"""
TOLKAR Zero@Factory - SQLAlchemy Models
Production Intelligence Platform Database Models
Phase 9.5 - Production Ready
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tolkar_factory.db")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

class User(Base):
    """User model for authentication and role management"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="operator", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    maintenance_logs = relationship("MaintenanceLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Station(Base):
    """Production station configuration"""
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    station_type = Column(String(50), nullable=True)
    
    # Baseline performance metrics
    wip_baseline = Column(Integer, default=3, nullable=False)  # Work in Progress
    ct_baseline = Column(Integer, default=45, nullable=False)  # Cycle Time (minutes)
    fpy_baseline = Column(Float, default=98.0, nullable=False)  # First Pass Yield (%)
    oee_baseline = Column(Float, default=94.0, nullable=False)  # Overall Equipment Effectiveness (%)
    
    # Current status
    status = Column(String(20), default="ok", nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    production_runs = relationship("ProductionRun", back_populates="station")
    telemetry_data = relationship("Telemetry", back_populates="station")
    maintenance_logs = relationship("MaintenanceLog", back_populates="station")
    
    def __repr__(self):
        return f"<Station(name='{self.name}', status='{self.status}')>"

class ProductionRun(Base):
    """Production run data with KPIs"""
    __tablename__ = "production_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    batch_number = Column(String(50), nullable=False, index=True)
    
    # Key Performance Indicators
    wip = Column(Integer, nullable=True)  # Work in Progress
    ct = Column(Integer, nullable=True)  # Cycle Time (minutes)
    fpy = Column(Float, nullable=True)  # First Pass Yield (%)
    oee = Column(Float, nullable=True)  # Overall Equipment Effectiveness (%)
    
    # Status and disruption tracking
    status = Column(String(20), nullable=True, index=True)
    disruption_type = Column(String(50), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    station = relationship("Station", back_populates="production_runs")
    
    def __repr__(self):
        return f"<ProductionRun(batch='{self.batch_number}', station_id={self.station_id})>"

class Telemetry(Base):
    """Real-time sensor telemetry data"""
    __tablename__ = "telemetry"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    
    # Sensor readings
    vibration_mms = Column(Float, nullable=True)  # Vibration (mm/s)
    temperature_c = Column(Float, nullable=True)  # Temperature (°C)
    pressure_bar = Column(Float, nullable=True)  # Pressure (bar)
    power_kw_idx = Column(Float, nullable=True)  # Power consumption index (kW)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    station = relationship("Station", back_populates="telemetry_data")
    
    def __repr__(self):
        return f"<Telemetry(station_id={self.station_id}, recorded_at='{self.recorded_at}')>"

class MaintenanceLog(Base):
    """Maintenance activity logs"""
    __tablename__ = "maintenance_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # Maintenance details
    maintenance_type = Column(String(50), nullable=False, index=True)  # preventive, corrective, emergency
    description = Column(Text, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    parts_replaced = Column(String(255), nullable=True)
    cost_eur = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    station = relationship("Station", back_populates="maintenance_logs")
    user = relationship("User", back_populates="maintenance_logs")
    
    def __repr__(self):
        return f"<MaintenanceLog(station_id={self.station_id}, type='{self.maintenance_type}')>"

class SystemEvent(Base):
    """System events and audit trail"""
    __tablename__ = "system_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False, index=True)  # login, logout, reset, shock, kaizen, maintenance
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True, index=True)
    
    # Event details
    label = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # info, warning, critical
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    station = relationship("Station")
    
    def __repr__(self):
        return f"<SystemEvent(type='{self.event_type}', severity='{self.severity}', label='{self.label}')>"

# Database initialization function
def init_db():
    """Initialize database and create default data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create default data
        with SessionLocal() as db:
            # Check if users exist
            user_count = db.query(User).count()
            if user_count == 0:
                # Create default users
                from auth import AuthService
                auth_service = AuthService()
                
                # Admin user
                admin_user = User(
                    id=str(uuid.uuid4()),
                    username="admin",
                    email="admin@tolkar.local",
                    password_hash=auth_service.hash_password("admin123"),
                    role="admin"
                )
                db.add(admin_user)
                
                # Supervisor user
                supervisor_user = User(
                    id=str(uuid.uuid4()),
                    username="supervisor",
                    email="supervisor@tolkar.local",
                    password_hash=auth_service.hash_password("supervisor123"),
                    role="supervisor"
                )
                db.add(supervisor_user)
                
                # Operator user
                operator_user = User(
                    id=str(uuid.uuid4()),
                    username="operator1",
                    email="operator1@tolkar.local",
                    password_hash=auth_service.hash_password("operator123"),
                    role="operator"
                )
                db.add(operator_user)
                
                db.commit()
                print("✅ Default users created successfully")
            
            # Check if stations exist
            station_count = db.query(Station).count()
            if station_count == 0:
                # Create default production stations
                stations = [
                    Station(
                        id=1,
                        name="Washing",
                        station_type="washing",
                        wip_baseline=3,
                        ct_baseline=45,
                        fpy_baseline=98.0,
                        oee_baseline=94.0,
                        status="ok"
                    ),
                    Station(
                        id=2,
                        name="Dyeing",
                        station_type="dyeing",
                        wip_baseline=3,
                        ct_baseline=45,
                        fpy_baseline=98.0,
                        oee_baseline=94.0,
                        status="ok"
                    ),
                    Station(
                        id=3,
                        name="Finishing",
                        station_type="finishing",
                        wip_baseline=3,
                        ct_baseline=45,
                        fpy_baseline=98.0,
                        oee_baseline=94.0,
                        status="ok"
                    ),
                    Station(
                        id=4,
                        name="Inspection",
                        station_type="inspection",
                        wip_baseline=3,
                        ct_baseline=45,
                        fpy_baseline=98.0,
                        oee_baseline=94.0,
                        status="ok"
                    ),
                    Station(
                        id=5,
                        name="Packing",
                        station_type="packing",
                        wip_baseline=3,
                        ct_baseline=45,
                        fpy_baseline=98.0,
                        oee_baseline=94.0,
                        status="ok"
                    )
                ]
                
                for station in stations:
                    db.add(station)
                
                db.commit()
                print("✅ Default stations created successfully")
            
            # Create initial telemetry data
            telemetry_count = db.query(Telemetry).count()
            if telemetry_count == 0:
                # Add initial telemetry readings
                telemetry_data = [
                    Telemetry(
                        id=str(uuid.uuid4()),
                        station_id=1,
                        vibration_mms=2.3,
                        temperature_c=78,
                        pressure_bar=6.2,
                        power_kw_idx=85
                    ),
                    Telemetry(
                        id=str(uuid.uuid4()),
                        station_id=2,
                        vibration_mms=2.1,
                        temperature_c=82,
                        pressure_bar=5.8,
                        power_kw_idx=88
                    ),
                    Telemetry(
                        id=str(uuid.uuid4()),
                        station_id=3,
                        vibration_mms=2.5,
                        temperature_c=75,
                        pressure_bar=6.5,
                        power_kw_idx=92
                    ),
                    Telemetry(
                        id=str(uuid.uuid4()),
                        station_id=4,
                        vibration_mms=1.9,
                        temperature_c=79,
                        pressure_bar=5.5,
                        power_kw_idx=78
                    ),
                    Telemetry(
                        id=str(uuid.uuid4()),
                        station_id=5,
                        vibration_mms=2.0,
                        temperature_c=76,
                        pressure_bar=6.0,
                        power_kw_idx=81
                    )
                ]
                
                for telemetry in telemetry_data:
                    db.add(telemetry)
                
                db.commit()
                print("✅ Initial telemetry data created successfully")
            
            print("✅ Database initialization completed successfully")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def health_check() -> bool:
    """Check database connectivity"""
    try:
        with SessionLocal() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

# Create indexes for better performance
from sqlalchemy import Index

# Create indexes
Index('idx_users_username', User.username)
Index('idx_users_email', User.email)
Index('idx_users_role', User.role)
Index('idx_stations_name', Station.name)
Index('idx_stations_status', Station.status)
Index('idx_production_runs_station_id', ProductionRun.station_id)
Index('idx_production_runs_created_at', ProductionRun.created_at)
Index('idx_production_runs_status', ProductionRun.status)
Index('idx_telemetry_station_id', Telemetry.station_id)
Index('idx_telemetry_recorded_at', Telemetry.recorded_at)
Index('idx_maintenance_logs_station_id', MaintenanceLog.station_id)
Index('idx_maintenance_logs_user_id', MaintenanceLog.user_id)
Index('idx_maintenance_logs_maintenance_type', MaintenanceLog.maintenance_type)
Index('idx_system_events_event_type', SystemEvent.event_type)
Index('idx_system_events_severity', SystemEvent.severity)
Index('idx_system_events_created_at', SystemEvent.created_at)