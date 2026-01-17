from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from datetime import datetime
from config import settings
from models import Base, Factory, Station

def init_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'telemetry_history' AND c.relkind = 'r'
          ) THEN
            CREATE TABLE telemetry_history (
              id BIGSERIAL PRIMARY KEY,
              station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
              timestamp TIMESTAMP NOT NULL,
              oee DECIMAL(5,2),
              cycle_time_sec INTEGER,
              fpy DECIMAL(5,2),
              wip INTEGER,
              power_kw DECIMAL(8,2),
              temperature_c DECIMAL(5,2),
              vibration_mm_s DECIMAL(5,2),
              cycle_count INTEGER
            ) PARTITION BY RANGE (timestamp);
          END IF;
        END$$;
        """))
        now = datetime.utcnow()
        part_name = f"telemetry_history_{now.year}_{str(now.month).zfill(2)}"
        start_month = f"{now.year}-{str(now.month).zfill(2)}-01"
        if now.month == 12:
            end_year = now.year + 1
            end_month = 1
        else:
            end_year = now.year
            end_month = now.month + 1
        end_month_str = f"{end_year}-{str(end_month).zfill(2)}-01"
        conn.execute(text(f"""
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = '{part_name}') THEN
            CREATE TABLE {part_name} PARTITION OF telemetry_history
            FOR VALUES FROM ('{start_month}') TO ('{end_month_str}');
          END IF;
        END$$;
        """))
    with Session(engine) as session:
        if not session.query(Factory).first():
            factory = Factory(name="Bursa Plant", location="Bursa, Turkey", timezone="Europe/Istanbul", target_oee=80.0)
            session.add(factory)
            session.flush()
            station_configs = [
                {"num": 1, "name": "Stamping", "type": "stamping", "ct": 120, "pos": 2},
                {"num": 2, "name": "Welding", "type": "welding", "ct": 135, "pos": 5},
                {"num": 3, "name": "Assembly", "type": "assembly", "ct": 150, "pos": 8},
                {"num": 4, "name": "Painting", "type": "painting", "ct": 180, "pos": 11},
                {"num": 5, "name": "Curing", "type": "curing", "ct": 200, "pos": 14},
                {"num": 6, "name": "Inspection", "type": "inspection", "ct": 90, "pos": 17},
                {"num": 7, "name": "Packaging", "type": "packaging", "ct": 110, "pos": 19},
            ]
            for cfg in station_configs:
                session.add(Station(factory_id=factory.id, station_number=cfg["num"], name=f"Station {cfg['num']} - {cfg['name']}", station_type=cfg["type"], target_cycle_time_sec=cfg["ct"], target_fpy=95.0, position_on_track=cfg["pos"]))
            session.commit()

if __name__ == "__main__":
    init_database()
