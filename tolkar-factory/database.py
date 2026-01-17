"""
TOLKAR Zero@Factory - Database Configuration
Production Intelligence Platform Database Setup
Phase 9.5 - Production Ready
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import logging
from typing import Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tolkar_factory.db")

# Connection pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create engine with appropriate configuration
def create_database_engine():
    """Create database engine with proper configuration"""
    
    # SQLite specific configuration
    if "sqlite" in DATABASE_URL.lower():
        # SQLite configuration for development
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=False  # Set to True for SQL debugging
        )
        logger.info("✅ SQLite database engine created (development mode)")
    
    # PostgreSQL configuration for production
    elif "postgresql" in DATABASE_URL.lower():
        # PostgreSQL configuration with connection pooling
        engine = create_engine(
            DATABASE_URL,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            pool_pre_ping=True,
            echo=False,  # Set to True for SQL debugging
            # Additional PostgreSQL optimizations
            executemany_mode='batch',
            isolation_level="READ_COMMITTED"
        )
        logger.info("✅ PostgreSQL database engine created (production mode)")
    
    # MySQL configuration (alternative)
    elif "mysql" in DATABASE_URL.lower():
        engine = create_engine(
            DATABASE_URL,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            pool_pre_ping=True,
            echo=False
        )
        logger.info("✅ MySQL database engine created")
    
    else:
        # Default configuration for other databases
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )
        logger.info("✅ Database engine created (default configuration)")
    
    return engine

# Create engine instance
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables"""
    try:
        logger.info("🚀 Initializing TOLKAR Zero@Factory database...")
        
        # Test database connection
        test_connection()
        
        # Import models to register them with SQLAlchemy
        from models import Base, User, Station, ProductionRun, Telemetry, MaintenanceLog, SystemEvent
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Create indexes for better performance
        create_indexes()
        
        # Insert default data
        insert_default_data()
        
        logger.info("✅ Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        with SessionLocal() as db:
            # Simple connection test
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("✅ Database connection test passed")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Import models
        from models import User, Station, ProductionRun, Telemetry, MaintenanceLog, SystemEvent
        
        # Create indexes if they don't exist
        indexes_sql = []
        
        if "sqlite" in DATABASE_URL.lower():
            # SQLite specific indexes
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);",
                "CREATE INDEX IF NOT EXISTS idx_stations_name ON stations (name);",
                "CREATE INDEX IF NOT EXISTS idx_stations_status ON stations (status);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_station_id ON production_runs (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_created_at ON production_runs (created_at);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_status ON production_runs (status);",
                "CREATE INDEX IF NOT EXISTS idx_telemetry_station_id ON telemetry (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_telemetry_recorded_at ON telemetry (recorded_at);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_station_id ON maintenance_logs (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_user_id ON maintenance_logs (user_id);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_maintenance_type ON maintenance_logs (maintenance_type);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_event_type ON system_events (event_type);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events (severity);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_created_at ON system_events (created_at);"
            ]
        
        elif "postgresql" in DATABASE_URL.lower():
            # PostgreSQL specific indexes
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);",
                "CREATE INDEX IF NOT EXISTS idx_stations_name ON stations (name);",
                "CREATE INDEX IF NOT EXISTS idx_stations_status ON stations (status);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_station_id ON production_runs (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_created_at ON production_runs (created_at);",
                "CREATE INDEX IF NOT EXISTS idx_production_runs_status ON production_runs (status);",
                "CREATE INDEX IF NOT EXISTS idx_telemetry_station_id ON telemetry (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_telemetry_recorded_at ON telemetry (recorded_at);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_station_id ON maintenance_logs (station_id);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_user_id ON maintenance_logs (user_id);",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_maintenance_type ON maintenance_logs (maintenance_type);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_event_type ON system_events (event_type);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events (severity);",
                "CREATE INDEX IF NOT EXISTS idx_system_events_created_at ON system_events (created_at);"
            ]
        
        # Execute indexes
        with SessionLocal() as db:
            for sql in indexes_sql:
                try:
                    db.execute(text(sql))
                    db.commit()
                except Exception as e:
                    logger.warning(f"⚠️  Could not create index: {e}")
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Index creation failed: {e}")

def insert_default_data():
    """Insert default data into database"""
    try:
        logger.info("📊 Inserting default data...")
        
        # Import required modules
        from models import User, Station, ProductionRun, Telemetry, MaintenanceLog, SystemEvent
        from auth import AuthService
        import uuid
        from datetime import datetime
        
        auth_service = AuthService()
        
        with SessionLocal() as db:
            # Check if users exist
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("👥 Creating default users...")
                
                # Admin user
                admin_user = User(
                    id=str(uuid.uuid4()),
                    username="admin",
                    email="admin@tolkar.local",
                    password_hash=auth_service.hash_password("admin123"),
                    role="admin",
                    is_active=True
                )
                db.add(admin_user)
                
                # Supervisor user
                supervisor_user = User(
                    id=str(uuid.uuid4()),
                    username="supervisor",
                    email="supervisor@tolkar.local",
                    password_hash=auth_service.hash_password("supervisor123"),
                    role="supervisor",
                    is_active=True
                )
                db.add(supervisor_user)
                
                # Operator user
                operator_user = User(
                    id=str(uuid.uuid4()),
                    username="operator1",
                    email="operator1@tolkar.local",
                    password_hash=auth_service.hash_password("operator123"),
                    role="operator",
                    is_active=True
                )
                db.add(operator_user)
                
                db.commit()
                logger.info("✅ Default users created successfully")
            
            # Check if stations exist
            station_count = db.query(Station).count()
            if station_count == 0:
                logger.info("🏭 Creating default production stations...")
                
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
                logger.info("✅ Default stations created successfully")
            
            # Create initial telemetry data
            telemetry_count = db.query(Telemetry).count()
            if telemetry_count == 0:
                logger.info("📡 Creating initial telemetry data...")
                
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
                logger.info("✅ Initial telemetry data created successfully")
            
            # Create initial production runs
            production_run_count = db.query(ProductionRun).count()
            if production_run_count == 0:
                logger.info("📈 Creating initial production runs...")
                
                # Get all stations
                stations = db.query(Station).all()
                
                for station in stations:
                    # Create initial production run with baseline values
                    production_run = ProductionRun(
                        id=str(uuid.uuid4()),
                        station_id=station.id,
                        batch_number=f"INIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{station.id}",
                        wip=station.wip_baseline,
                        ct=station.ct_baseline,
                        fpy=station.fpy_baseline,
                        oee=station.oee_baseline,
                        status="ok"
                    )
                    db.add(production_run)
                
                db.commit()
                logger.info("✅ Initial production runs created successfully")
            
            logger.info("✅ Default data insertion completed successfully")
            
    except Exception as e:
        logger.error(f"❌ Default data insertion failed: {e}")
        raise

def health_check() -> bool:
    """Comprehensive database health check"""
    try:
        with SessionLocal() as db:
            # Test basic connection
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test table existence
            from models import User, Station
            user_count = db.query(User).count()
            station_count = db.query(Station).count()
            
            if user_count == 0:
                logger.warning("⚠️  No users found in database")
            
            if station_count == 0:
                logger.warning("⚠️  No stations found in database")
            
            logger.info(f"✅ Database health check passed (users: {user_count}, stations: {station_count})")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False

def reset_database():
    """Reset database (drop all tables and recreate)"""
    try:
        logger.warning("🔄 Resetting database...")
        
        # Import models
        from models import Base
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables recreated")
        
        # Insert default data
        insert_default_data()
        
        logger.info("✅ Database reset completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise

def backup_database(backup_path: str = None):
    """Backup database"""
    try:
        if "sqlite" in DATABASE_URL.lower():
            # SQLite backup
            import shutil
            import datetime
            
            if backup_path is None:
                backup_path = f"tolkar_factory_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Get database file path from URL
            db_path = DATABASE_URL.replace("sqlite:///", "")
            
            shutil.copy2(db_path, backup_path)
            logger.info(f"✅ SQLite database backed up to: {backup_path}")
            return backup_path
            
        else:
            logger.warning("⚠️  Database backup not implemented for this database type")
            return None
            
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        return None

if __name__ == "__main__":
    # Command line interface
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_db()
        elif command == "health":
            if health_check():
                print("✅ Database is healthy")
                sys.exit(0)
            else:
                print("❌ Database is unhealthy")
                sys.exit(1)
        elif command == "reset":
            reset_database()
        elif command == "backup":
            backup_path = backup_database()
            if backup_path:
                print(f"✅ Database backed up to: {backup_path}")
            else:
                print("❌ Database backup failed")
        else:
            print("Available commands: init, health, reset, backup")
    else:
        # Default: initialize database
        init_db()