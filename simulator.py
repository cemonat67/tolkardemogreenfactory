import time
import random
from datetime import datetime, timedelta

class Simulator:
    def __init__(self):
        self.stations = [
            {"id": 1, "name": "Washing", "wip": 3, "ct": 45, "fpy": 98.0, "oee": 94.0, "status": "ok"},
            {"id": 2, "name": "Pre-treatment", "wip": 3, "ct": 45, "fpy": 98.0, "oee": 94.0, "status": "ok"},
            {"id": 3, "name": "Finishing", "wip": 4, "ct": 50, "fpy": 96.0, "oee": 90.0, "status": "ok"},
            {"id": 4, "name": "Inspection", "wip": 2, "ct": 25, "fpy": 97.0, "oee": 92.0, "status": "ok"},
            {"id": 5, "name": "Packaging", "wip": 2, "ct": 20, "fpy": 99.0, "oee": 95.0, "status": "ok"},
        ]
        self.events = []
        self.telemetry = []
        self._seed()

    def _seed(self):
        now = datetime.utcnow()
        for s in self.stations:
            for i in range(24):
                t = now - timedelta(minutes=5*i)
                self.telemetry.append({
                    "id": f"t-{s['id']}-{i}", "station_id": s["id"],
                    "vibration_mms": round(2.0 + random.random()*0.6, 2),
                    "temperature_c": round(76 + random.random()*6, 1),
                    "pressure_bar": round(5.8 + random.random()*0.6, 2),
                    "power_kw_idx": round(80 + random.random()*8, 1),
                    "recorded_at": t
                })
        self.events.append({"id": "e-1", "event_type": "shock", "station_id": 3, "label": "Bottleneck detected @ Finishing", "severity": "critical", "created_at": now - timedelta(hours=1)})

    def get_state(self):
        ts = datetime.utcnow()
        return {
            "stations": self.stations,
            "telemetry": {
                "vibration": 2.3,
                "temperature": 78,
                "pressure": 6.2,
                "power": 85,
                "history": {
                    "vibration": [2.0, 2.1, 2.2, 2.3],
                    "temperature": [80, 79, 78, 78],
                    "pressure": [5.9, 6.0, 6.1, 6.2],
                    "power": [81, 82, 84, 85]
                }
            },
            "timestamp": ts
        }

    def reset(self):
        for s in self.stations:
            s["status"] = "ok"
        self.events.append({"id": f"e-{int(time.time())}", "event_type": "reset", "station_id": None, "label": "Stations reset to baseline", "severity": "info", "created_at": datetime.utcnow()})
        return {"status": "success", "message": "All stations reset to baseline"}

    def shock(self):
        fin = next((x for x in self.stations if x["name"] == "Finishing"), None)
        if fin:
            fin["status"] = "bottleneck"
            fin["wip"] = 8
            fin["fpy"] = max(90.0, fin["fpy"] - 4.0)
            self.events.append({"id": f"e-{int(time.time())}", "event_type": "shock", "station_id": fin["id"], "label": "Bottleneck detected @ Finishing", "severity": "critical", "created_at": datetime.utcnow()})
        return {"status": "success", "message": "Disruption simulated", "disruption": "Finishing station bottleneck"}

    def kaizen(self):
        for s in self.stations:
            s["status"] = "ok"
            s["wip"] = max(1, s["wip"] - 1)
            s["oee"] = min(96.0, s["oee"] + 1.0)
            s["fpy"] = min(99.0, s["fpy"] + 1.0)
            self.events.append({"id": f"e-{int(time.time())}", "event_type": "kaizen", "station_id": s["id"], "label": "Kaizen applied", "severity": "info", "created_at": datetime.utcnow()})
        return {"status": "success", "message": "Kaizen improvement completed"}

    def get_events(self, limit=20, start=None, end=None):
        rows = list(self.events)
        rows.sort(key=lambda r: (r["created_at"] or datetime.utcnow()), reverse=True)
        if start:
            rows = [r for r in rows if r["created_at"] and r["created_at"] >= start]
        if end:
            rows = [r for r in rows if r["created_at"] and r["created_at"] <= end]
        return rows[:limit]

    def get_telemetry(self, start=None, end=None, station_id=None, limit=100):
        rows = list(self.telemetry)
        if station_id:
            rows = [r for r in rows if r["station_id"] == station_id]
        if start:
            rows = [r for r in rows if r["recorded_at"] and r["recorded_at"] >= start]
        if end:
            rows = [r for r in rows if r["recorded_at"] and r["recorded_at"] <= end]
        rows.sort(key=lambda r: r["recorded_at"], reverse=True)
        return rows[:limit]

sim = Simulator()
