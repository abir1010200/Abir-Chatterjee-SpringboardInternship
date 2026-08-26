import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.sensor import Sensor

logger = logging.getLogger(__name__)

class SensorMonitorService:
    """
    Monitors IoT hardware health, detects sensor disconnections,
    and updates operational statuses (active -> stale -> offline).
    """
    def __init__(self):
        self.stale_threshold = timedelta(minutes=settings.SENSOR_STALE_THRESHOLD_MINUTES)
        self.offline_threshold = timedelta(minutes=settings.SENSOR_OFFLINE_THRESHOLD_MINUTES)

    def evaluate_fleet_status(self, db: Session) -> Dict[str, Any]:
        """
        Scans all registered sensors, updates their status based on heartbeat latency,
        and generates a hardware reliability summary.
        """
        now = datetime.now(timezone.utc)
        sensors: List[Sensor] = db.query(Sensor).all()

        active_count = 0
        stale_count = 0
        offline_count = 0
        low_battery_sensors = []
        sensor_statuses = []

        for s in sensors:
            last_seen = getattr(s, "last_seen")
            battery = getattr(s, "battery_level")

            # Check heartbeat recency
            if last_seen is None:
                new_status = "offline"
            else:
                if last_seen.tzinfo is None:
                    last_seen = last_seen.replace(tzinfo=timezone.utc)
                
                dt = now - last_seen
                if dt <= self.stale_threshold:
                    new_status = "active"
                elif dt <= self.offline_threshold:
                    new_status = "stale"
                else:
                    new_status = "offline"

            setattr(s, "status", new_status)

            if new_status == "active":
                active_count += 1
            elif new_status == "stale":
                stale_count += 1
            else:
                offline_count += 1

            if battery is not None and float(battery) < 20.0:
                low_battery_sensors.append({
                    "sensor_id": s.id,
                    "field_id": s.field_id,
                    "battery_level": float(battery)
                })

            sensor_statuses.append({
                "sensor_id": s.id,
                "field_id": s.field_id,
                "status": new_status,
                "battery_level": float(battery) if battery is not None else None,
                "last_seen": last_seen.isoformat() if last_seen else None,
            })

        db.commit()

        return {
            "total_sensors": len(sensors),
            "active_count": active_count,
            "stale_count": stale_count,
            "offline_count": offline_count,
            "low_battery_alerts": low_battery_sensors,
            "sensors": sensor_statuses,
            "evaluated_at": now.isoformat()
        }

sensor_monitor = SensorMonitorService()
