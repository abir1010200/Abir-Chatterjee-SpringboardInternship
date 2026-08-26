import json
import logging
import threading
import time
import re
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.schemas.sensor_reading import SensorReadingCreate
from backend.app.services.ingestion import ingest_sensor_reading

logger = logging.getLogger(__name__)

# Topic pattern: farm/{farm_id}/field/{field_id}/sensor/{sensor_id}/reading
TOPIC_REGEX = re.compile(r"^farm/([^/]+)/field/(\d+)/sensor/([^/]+)/reading$")

class MQTTSubscriberService:
    def __init__(self):
        self.host = settings.MQTT_BROKER_HOST
        self.port = settings.MQTT_BROKER_PORT
        self.client_id = f"{settings.MQTT_CLIENT_ID}_{int(time.time())}"
        self.topic = settings.MQTT_TOPIC_PREFIX
        self.client: mqtt.Client = None
        self._is_running = False
        self._thread: threading.Thread = None

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"Connected to MQTT Broker at {self.host}:{self.port} with Client ID: {self.client_id}")
            client.subscribe(self.topic, qos=1)
            logger.info(f"Subscribed to topic pattern: {self.topic}")
        else:
            logger.error(f"Failed to connect to MQTT Broker with return code: {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            logger.warning(f"Unexpected MQTT Broker disconnection (code={rc}). Auto-reconnection enabled.")
        else:
            logger.info("MQTT Broker disconnected cleanly.")

    def _on_message(self, client, userdata, msg):
        """Processes incoming MQTT telemetry messages."""
        try:
            topic = msg.topic
            payload_raw = msg.payload.decode("utf-8")
            logger.debug(f"Received MQTT message on {topic}: {payload_raw}")

            data = json.loads(payload_raw)

            # Extract metadata from topic if available
            match = TOPIC_REGEX.match(topic)
            if match:
                _, field_id_str, sensor_id_from_topic = match.groups()
                if "field_id" not in data:
                    data["field_id"] = int(field_id_str)
                if "sensor_id" not in data:
                    data["sensor_id"] = sensor_id_from_topic

            # Ensure timestamp
            if "timestamp" not in data:
                data["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Validate with Pydantic
            validated_payload = SensorReadingCreate(**data)

            # Store in DB via shared ingestion engine
            db = SessionLocal()
            try:
                reading, is_dup = ingest_sensor_reading(db=db, payload=validated_payload, source="mqtt")
                logger.info(
                    f"MQTT Telemetry Ingested: sensor={reading.sensor_id} "
                    f"moisture={reading.soil_moisture}% dup={is_dup}"
                )
            finally:
                db.close()

        except json.JSONDecodeError as jde:
            logger.warning(f"Invalid JSON payload received on topic {msg.topic}: {jde}")
        except ValueError as ve:
            logger.warning(f"Validation failure for MQTT payload on topic {msg.topic}: {ve}")
        except Exception as e:
            logger.error(f"Unexpected error handling MQTT telemetry on {msg.topic}: {e}")

    def start(self):
        """Start the MQTT client subscriber in a dedicated daemon thread."""
        if self._is_running:
            return

        def _run():
            try:
                # Use MQTT protocol v3.1.1/v5 compatible
                try:
                    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)
                except AttributeError:
                    self.client = mqtt.Client(client_id=self.client_id)

                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message

                logger.info(f"Connecting to MQTT Broker at {self.host}:{self.port}...")
                self.client.connect_async(self.host, self.port, keepalive=60)
                self.client.loop_start()
                self._is_running = True
            except Exception as e:
                logger.warning(f"MQTT Broker connection failed ({e}). MQTT subscription inactive until broker is available.")

        self._thread = threading.Thread(target=_run, daemon=True, name="MQTT-Subscriber")
        self._thread.start()

    def stop(self):
        """Stop the MQTT subscriber client loop."""
        if self.client and self._is_running:
            self._is_running = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT Subscriber service stopped.")

mqtt_service = MQTTSubscriberService()
