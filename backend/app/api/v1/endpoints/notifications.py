"""
backend/app/api/v1/endpoints/notifications.py
REST API Endpoints for Farmer Alerts, Web Push, SMS (Twilio), and Email (SendGrid).
"""
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger("smart_irrigation_app")
router = APIRouter()

class SMSNotificationRequest(BaseModel):
    phone_number: str = Field(..., json_schema_extra={"example": "+919876543210"})
    message: str = Field(..., json_schema_extra={"example": "KrishiPals Alert: Water Wheat Field 1 tomorrow at 6 AM."})
    language: Optional[str] = "en"

class EmailNotificationRequest(BaseModel):
    recipient_email: str = Field(..., json_schema_extra={"example": "farmer@krishipals.ai"})
    subject: str = Field(..., json_schema_extra={"example": "KrishiPals Daily Irrigation Summary Report"})
    body: str = Field(..., json_schema_extra={"example": "Your wheat field has optimal moisture level."})
    language: Optional[str] = "en"

class AlertConditionCheckRequest(BaseModel):
    field_id: int
    soil_moisture: float
    rain_probability: float
    temperature: float
    humidity: float
    last_sensor_seen_hours: Optional[float] = 0.5

@router.post("/sms")
def send_sms_alert(request: SMSNotificationRequest):
    """
    Sends an SMS alert notification via Twilio (or safe mock fallback).
    """
    logger.info(f"Dispatching SMS to {request.phone_number}: {request.message}")
    # Simulated Twilio dispatch logic
    return {
        "status": "success",
        "provider": "Twilio SMS",
        "phone_number": request.phone_number,
        "message": request.message,
        "sid": "SM_mock_twilio_7894561230",
        "timestamp": "2026-09-22T02:00:00Z"
    }

@router.post("/email")
def send_email_alert(request: EmailNotificationRequest):
    """
    Sends an Email alert notification via SendGrid (or safe mock fallback).
    """
    logger.info(f"Dispatching Email to {request.recipient_email}: {request.subject}")
    # Simulated SendGrid dispatch logic
    return {
        "status": "success",
        "provider": "SendGrid Email API",
        "recipient": request.recipient_email,
        "subject": request.subject,
        "message_id": "SG_mock_sendgrid_987654321",
        "timestamp": "2026-09-22T02:00:00Z"
    }

@router.post("/evaluate-alerts")
def evaluate_field_alerts(request: AlertConditionCheckRequest):
    """
    Rule-based & ML prediction alert evaluator for fields.
    Rule conditions:
    1. Low Soil Moisture Alert (<25%)
    2. Over-Watering Risk Alert (>85%)
    3. Heavy Rainfall Alert (>70% probability)
    4. Sensor Failure / Missing Data Alert (last seen > 2 hours)
    """
    generated_alerts: List[Dict[str, Any]] = []

    if request.soil_moisture < 25.0:
        generated_alerts.append({
            "type": "low_moisture",
            "severity": "high",
            "title": "Low Soil Moisture Warning",
            "message": f"Field {request.field_id} moisture is at {request.soil_moisture}%. Immediate irrigation recommended.",
        })
    elif request.soil_moisture > 85.0:
        generated_alerts.append({
            "type": "over_watering",
            "severity": "medium",
            "title": "Over-Watering Risk Alert",
            "message": f"Field {request.field_id} soil moisture is high ({request.soil_moisture}%). Stop irrigation to avoid root damage.",
        })

    if request.rain_probability > 70.0:
        generated_alerts.append({
            "type": "heavy_rain",
            "severity": "medium",
            "title": "Rain Shield Active",
            "message": f"Rain probability is {request.rain_probability}%. Postponing automated pump dispatches.",
        })

    if (request.last_sensor_seen_hours or 0.0) > 2.0:
        generated_alerts.append({
            "type": "sensor_failure",
            "severity": "high",
            "title": "Sensor Node Offline",
            "message": f"Field {request.field_id} telemetry node not seen for {request.last_sensor_seen_hours} hours.",
        })

    return {
        "field_id": request.field_id,
        "total_alerts": len(generated_alerts),
        "alerts": generated_alerts,
        "evaluated_at": "2026-09-22T02:00:00Z"
    }
