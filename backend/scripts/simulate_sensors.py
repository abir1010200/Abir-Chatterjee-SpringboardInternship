#!/usr/bin/env python3
"""
AI-Powered Smart Irrigation System - Realistic Sensor Data Simulator
====================================================================
Generates physics-informed soil moisture & soil temperature time series:
- Diurnal evapotranspiration decay (faster drying during solar peak)
- Sharp infiltration spikes on simulated rain/irrigation events
- Realistic sensor noise and battery discharge
- Supports REST API publishing, MQTT broker publishing, and Direct DB backfilling.
"""

import sys
import os
import time
import math
import random
import argparse
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import httpx

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Simulator) %(message)s"
)
logger = logging.getLogger("sensor_simulator")

class SoilPhysicsModel:
    """
    Simulates realistic soil moisture dynamics based on soil type,
    ambient solar cycle, evapotranspiration decay, and irrigation events.
    """
    def __init__(self, sensor_id: str, field_id: int, initial_moisture: float = 38.0):
        self.sensor_id = sensor_id
        self.field_id = field_id
        self.moisture = initial_moisture
        self.battery = random.uniform(92.0, 99.5)
        self.irrigation_cooldown = 0
        self.field_capacity = 42.0
        self.wilting_point = 14.0

    def step(self, current_time: datetime, dt_minutes: float = 15.0) -> Dict[str, Any]:
        hour = current_time.hour + (current_time.minute / 60.0)
        
        # 1. Soil Temperature: Diurnal cycle peaking at ~15:00 UTC, trough at ~05:00 UTC
        # Base: 24°C, Amplitude: 8°C
        temp_rad = (hour - 9) * (2 * math.pi / 24.0)
        soil_temp = 24.0 + 7.5 * math.sin(temp_rad) + random.gauss(0, 0.3)

        # 2. Evapotranspiration rate (ET): Stronger during daytime (10:00 to 17:00)
        daylight_factor = max(0.0, math.sin((hour - 6) * math.pi / 12.0)) if 6 <= hour <= 18 else 0.05
        decay_rate = (0.015 + 0.045 * daylight_factor) * (dt_minutes / 15.0)
        
        self.moisture -= decay_rate

        # 3. Simulated Irrigation Event: Trigger if soil moisture drops below threshold
        if self.moisture < (self.wilting_point + 6.0) and self.irrigation_cooldown <= 0:
            logger.info(f"💦 Triggering simulated irrigation spike for Field {self.field_id} ({self.sensor_id})")
            # Infiltration spike (+20% to +26%)
            self.moisture += random.uniform(20.0, 26.0)
            self.irrigation_cooldown = 48  # Cooldown steps (~12 hours)
        elif self.irrigation_cooldown > 0:
            self.irrigation_cooldown -= 1

        # Cap physical bounds with slight sensor measurement noise
        noise = random.gauss(0, 0.2)
        reported_moisture = max(self.wilting_point, min(self.field_capacity + 8.0, self.moisture + noise))
        self.moisture = max(self.wilting_point, min(self.field_capacity + 8.0, self.moisture))

        # 4. Battery drain (~0.001% per step)
        self.battery = max(5.0, self.battery - random.uniform(0.0005, 0.002))

        return {
            "sensor_id": self.sensor_id,
            "field_id": self.field_id,
            "soil_moisture": round(reported_moisture, 2),
            "temperature_soil": round(soil_temp, 2),
            "battery_level": round(self.battery, 1),
            "timestamp": current_time.isoformat()
        }

def run_rest_simulation(
    sensors: List[SoilPhysicsModel],
    api_url: str,
    interval_sec: float,
    duration_sec: int
):
    logger.info(f"Starting REST Telemetry Stream to {api_url}/api/sensors/readings (Interval: {interval_sec}s, Duration: {duration_sec}s)")
    start_time = time.time()
    steps = 0
    client = httpx.Client(timeout=10.0)

    try:
        while True:
            now_utc = datetime.now(timezone.utc)
            for sensor in sensors:
                payload = sensor.step(now_utc, dt_minutes=15.0)
                try:
                    res = client.post(f"{api_url}/api/sensors/readings", json=payload)
                    if res.status_code in [200, 201]:
                        data = res.json()
                        logger.info(
                            f"[REST Sent] Sensor={payload['sensor_id']} Field={payload['field_id']} "
                            f"Moisture={payload['soil_moisture']}% SoilTemp={payload['temperature_soil']}°C "
                            f"Battery={payload['battery_level']}% -> Status: {data.get('status')}"
                        )
                    else:
                        logger.warning(f"REST API Error {res.status_code}: {res.text}")
                except Exception as e:
                    logger.error(f"Failed to send telemetry via REST: {e}")

            steps += 1
            if duration_sec > 0 and (time.time() - start_time) >= duration_sec:
                logger.info(f"Simulation duration ({duration_sec}s) reached. Total steps: {steps}")
                break

            time.sleep(interval_sec)
    except KeyboardInterrupt:
        logger.info("Simulation halted by user.")
    finally:
        client.close()

def run_mqtt_simulation(
    sensors: List[SoilPhysicsModel],
    mqtt_host: str,
    mqtt_port: int,
    interval_sec: float,
    duration_sec: int
):
    import paho.mqtt.client as mqtt
    import json

    logger.info(f"Starting MQTT Telemetry Stream to {mqtt_host}:{mqtt_port} (Interval: {interval_sec}s, Duration: {duration_sec}s)")
    
    try:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sim_publisher_{int(time.time())}")
        except AttributeError:
            client = mqtt.Client(client_id=f"sim_publisher_{int(time.time())}")

        client.connect(mqtt_host, mqtt_port, keepalive=60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Could not connect to MQTT Broker {mqtt_host}:{mqtt_port} ({e}). Ensure Mosquitto is running.")
        return

    start_time = time.time()
    steps = 0
    try:
        while True:
            now_utc = datetime.now(timezone.utc)
            for sensor in sensors:
                payload = sensor.step(now_utc, dt_minutes=15.0)
                topic = f"farm/farm01/field/{sensor.field_id}/sensor/{sensor.sensor_id}/reading"
                payload_json = json.dumps(payload)
                client.publish(topic, payload_json, qos=1)
                logger.info(
                    f"[MQTT Published] Topic={topic} Moisture={payload['soil_moisture']}% "
                    f"Temp={payload['temperature_soil']}°C"
                )

            steps += 1
            if duration_sec > 0 and (time.time() - start_time) >= duration_sec:
                logger.info(f"Simulation duration ({duration_sec}s) reached.")
                break

            time.sleep(interval_sec)
    except KeyboardInterrupt:
        logger.info("MQTT Simulation halted by user.")
    finally:
        client.loop_stop()
        client.disconnect()

def backfill_historical_data(sensors: List[SoilPhysicsModel], days: int = 14):
    """Generates continuous historical 15-minute telemetry for ML model training."""
    from backend.app.db.session import SessionLocal
    from backend.app.schemas.sensor_reading import SensorReadingCreate
    from backend.app.services.ingestion import ingest_sensor_reading

    logger.info(f"Backfilling {days} days of historical 15-minute sensor readings into database...")
    db = SessionLocal()
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    end_date = datetime.now(timezone.utc)
    current = start_date
    total_records = 0

    try:
        while current <= end_date:
            for sensor in sensors:
                data = sensor.step(current, dt_minutes=15.0)
                payload = SensorReadingCreate(**data)
                ingest_sensor_reading(db=db, payload=payload, source="historical_backfill")
                total_records += 1
            current += timedelta(minutes=15)
        logger.info(f"Historical backfill complete! Ingested {total_records} readings across {len(sensors)} sensors.")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="AI Smart Irrigation - Realistic Sensor Data Simulator")
    parser.add_argument("--fields", type=int, default=2, help="Number of fields to simulate (default: 2)")
    parser.add_argument("--sensors-per-field", type=int, default=2, help="Sensors per field (default: 2)")
    parser.add_argument("--interval", type=float, default=2.0, help="Publish interval in seconds (default: 2.0)")
    parser.add_argument("--duration", type=int, default=10, help="Simulation duration in seconds (0 for infinite, default: 10)")
    parser.add_argument("--protocol", choices=["rest", "mqtt", "backfill"], default="rest", help="Ingestion transport protocol")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="Backend API base URL")
    parser.add_argument("--mqtt-host", type=str, default="localhost", help="MQTT Broker hostname")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT Broker port")
    parser.add_argument("--historical-days", type=int, default=14, help="Days to backfill when protocol=backfill")

    args = parser.parse_args()

    # Initialize sensor models
    sensor_models: List[SoilPhysicsModel] = []
    for f in range(1, args.fields + 1):
        for s in range(1, args.sensors_per_field + 1):
            sensor_id = f"SEN-FIELD0{f}-0{s}"
            initial_moisture = random.uniform(32.0, 42.0)
            sensor_models.append(SoilPhysicsModel(sensor_id=sensor_id, field_id=f, initial_moisture=initial_moisture))

    logger.info(f"Initialized {len(sensor_models)} sensors across {args.fields} fields.")

    if args.protocol == "rest":
        run_rest_simulation(sensor_models, api_url=args.api_url, interval_sec=args.interval, duration_sec=args.duration)
    elif args.protocol == "mqtt":
        run_mqtt_simulation(sensor_models, mqtt_host=args.mqtt_host, mqtt_port=args.mqtt_port, interval_sec=args.interval, duration_sec=args.duration)
    elif args.protocol == "backfill":
        backfill_historical_data(sensor_models, days=args.historical_days)

if __name__ == "__main__":
    main()
