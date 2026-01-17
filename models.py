from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class Factory(Base):
    __tablename__ = "factories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    timezone = Column(String(50), default="UTC")
    target_oee = Column(Numeric(5, 2), default=80.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    stations = relationship("Station", back_populates="factory", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="factory")

class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    station_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    station_type = Column(String(50))
    target_cycle_time_sec = Column(Integer, nullable=False)
    target_fpy = Column(Numeric(5, 2), default=95.00)
    position_on_track = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    factory = relationship("Factory", back_populates="stations")
    current_state = relationship("StationState", uselist=False, back_populates="station")
    telemetry = relationship("TelemetryHistory", back_populates="station")
    events = relationship("Event", back_populates="station")
    __table_args__ = (Index("uq_factory_stationnum", "factory_id", "station_number", unique=True),)

class StationState(Base):
    __tablename__ = "station_state"
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, unique=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), nullable=False)
    oee = Column(Numeric(5, 2))
    cycle_time_sec = Column(Integer)
    wip = Column(Integer, default=0)
    fpy = Column(Numeric(5, 2))
    uptime_hours = Column(Numeric(8, 2))
    bottleneck = Column(Boolean, default=False)
    temperature_c = Column(Numeric(5, 2))
    vibration_mm_s = Column(Numeric(5, 2))
    power_kw = Column(Numeric(8, 2))
    cycle_count = Column(Integer, default=0)
    station = relationship("Station", back_populates="current_state")

class TelemetryHistory(Base):
    __tablename__ = "telemetry_history"
    __table_args__ = (
        Index("idx_station_timestamp", "station_id", "timestamp"),
        {"postgresql_partition_by": "RANGE (timestamp)"},
    )
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    oee = Column(Numeric(5, 2))
    cycle_time_sec = Column(Integer)
    fpy = Column(Numeric(5, 2))
    wip = Column(Integer)
    power_kw = Column(Numeric(8, 2))
    temperature_c = Column(Numeric(5, 2))
    vibration_mm_s = Column(Numeric(5, 2))
    cycle_count = Column(Integer)
    station = relationship("Station", back_populates="telemetry")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id", ondelete="SET NULL"))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    severity = Column(String(20), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    duration_sec = Column(Integer)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    metadata = Column(JSONB)
    factory = relationship("Factory", back_populates="events")
    station = relationship("Station", back_populates="events")
    __table_args__ = (
        Index("idx_factory_timestamp", "factory_id", "timestamp"),
        Index("idx_severity_timestamp", "severity", "timestamp"),
    )

class ProductionLog(Base):
    __tablename__ = "production_logs"
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    units_produced = Column(Integer, nullable=False)
    units_scrapped = Column(Integer, default=0)
    shift = Column(String(20))
    __table_args__ = (Index("idx_prod_station_timestamp", "station_id", "timestamp"),)

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50))
    description = Column(Text)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    duration_minutes = Column(Integer)
    cost = Column(Numeric(10, 2))
    __table_args__ = (Index("idx_sched_completed", "scheduled_at", "completed"),)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(50), default="operator")
    factory_id = Column(Integer, ForeignKey("factories.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
