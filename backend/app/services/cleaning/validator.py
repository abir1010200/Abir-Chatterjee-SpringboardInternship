import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class TelemetryValidationReport:
    def __init__(self):
        self.total_readings: int = 0
        self.valid_readings: int = 0
        self.outliers_detected: int = 0
        self.duplicates_found: int = 0
        self.gaps_detected: List[Dict[str, Any]] = []
        self.status: str = "clean"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "total_readings": self.total_readings,
            "valid_readings": self.valid_readings,
            "outliers_detected": self.outliers_detected,
            "duplicates_found": self.duplicates_found,
            "gaps_count": len(self.gaps_detected),
            "gaps": self.gaps_detected
        }

class TelemetryValidator:
    """
    Validation engine evaluating sensor telemetry streams for:
    - Gap intervals beyond expected cadence (e.g. > 30 mins)
    - Physical boundary violations
    - Sudden statistical outliers (Z-score & Delta Rate of Change)
    """
    @staticmethod
    def detect_telemetry_gaps(
        timestamps: List[datetime],
        expected_interval_minutes: float = 15.0,
        gap_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Identify intervals where sensor transmissions dropped beyond threshold."""
        if len(timestamps) < 2:
            return []

        sorted_ts = sorted(timestamps)
        max_allowed_delta = timedelta(minutes=expected_interval_minutes * gap_multiplier)
        gaps = []

        for i in range(1, len(sorted_ts)):
            delta = sorted_ts[i] - sorted_ts[i-1]
            if delta > max_allowed_delta:
                missing_minutes = delta.total_seconds() / 60.0
                gaps.append({
                    "start_time": sorted_ts[i-1].isoformat(),
                    "end_time": sorted_ts[i].isoformat(),
                    "gap_duration_minutes": round(missing_minutes, 1),
                    "estimated_missing_samples": int(missing_minutes // expected_interval_minutes)
                })

        return gaps

    @staticmethod
    def detect_outliers_zscore(
        values: List[float],
        threshold: float = 3.0
    ) -> List[bool]:
        """Flags statistical outliers using rolling or global Z-score."""
        if len(values) < 4:
            return [False] * len(values)

        arr = np.array(values, dtype=float)
        mean = np.mean(arr)
        std = np.std(arr)

        if std < 1e-6:
            return [False] * len(values)

        z_scores = np.abs((arr - mean) / std)
        return [bool(x) for x in (z_scores > threshold)]

    @staticmethod
    def detect_rate_of_change_anomalies(
        values: List[float],
        timestamps: List[datetime],
        max_rate_per_minute: float = 2.5  # Max 2.5% moisture change per minute without rain/irrigation
    ) -> List[bool]:
        """Detects physically impossible sudden sensor spikes."""
        if len(values) < 2:
            return [False] * len(values)

        anomalies = [False] * len(values)
        for i in range(1, len(values)):
            dt_min = max(0.1, (timestamps[i] - timestamps[i-1]).total_seconds() / 60.0)
            rate = abs(values[i] - values[i-1]) / dt_min
            if rate > max_rate_per_minute:
                anomalies[i] = True

        return [bool(x) for x in anomalies]
