import os
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent
ARTIFACT_DIR = ML_ROOT / "artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True)

RANDOM_SEED: int = int(os.getenv("ML_SEED", "42"))
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_irrigation.db")
MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_BASELINE: str = "baseline_rule_based"
MLFLOW_EXPERIMENT_RF: str = "random_forest_irrigation"
MLFLOW_EXPERIMENT_GBM: str = "gradient_boosting_irrigation"
MLFLOW_EXPERIMENT_LSTM: str = "lstm_irrigation"

SYNTHETIC_DAYS: int = 180
SYNTHETIC_INTERVAL_HOURS: int = 1
SYNTHETIC_MIN_ROWS: int = 100

TRAIN_RATIO: float = 0.70
VAL_RATIO: float = 0.15
TEST_RATIO: float = 0.15

FIELD_CAPACITY: dict = {
    "clay": 45.0, "clay loam": 40.0, "loam": 35.0,
    "sandy loam": 28.0, "sandy": 20.0, "silt loam": 38.0,
    "silty clay": 42.0, "default": 35.0,
}

IRRIGATION_TRIGGER_FRACTION: float = float(os.getenv("IRRIGATION_TRIGGER_FRACTION", "0.65"))
RAIN_POSTPONE_THRESHOLD: float = float(os.getenv("RAIN_POSTPONE_THRESHOLD", "40.0"))
MIN_IRRIGATION_GAP_HOURS: int = int(os.getenv("MIN_IRRIGATION_GAP_HOURS", "12"))
PREFERRED_IRRIGATION_HOUR_MORNING: int = 6
PREFERRED_IRRIGATION_HOUR_EVENING: int = 18
HIGH_TEMP_EVENING_THRESHOLD: float = 35.0

STAGE_WATER_REQUIREMENT: dict = {
    "initial": 0.6, "vegetative": 1.0, "flowering": 1.2,
    "mid season": 1.2, "grain filling": 1.1,
    "late season": 0.8, "ripening": 0.6, "default": 1.0,
}

MAX_LITERS_PER_HECTARE: float = 5000.0
MIN_IRRIGATION_VOLUME_LITERS: float = 50.0
ROLLING_WINDOWS_HOURS: list = [3, 6, 12]
FEATURE_LAG_STEPS: int = 1

RF_N_ESTIMATORS: int = 200
RF_MAX_DEPTH: int = 15
RF_MIN_SAMPLES_SPLIT: int = 5
RF_MIN_SAMPLES_LEAF: int = 2
RF_CLASS_WEIGHT: str = "balanced"

GBM_N_ESTIMATORS: int = 200
GBM_MAX_DEPTH: int = 5
GBM_LEARNING_RATE: float = 0.05
GBM_SUBSAMPLE: float = 0.8
GBM_MIN_SAMPLES_SPLIT: int = 5

LSTM_SEQUENCE_LENGTH: int = int(os.getenv("ML_SEQUENCE_LENGTH", "12"))
LSTM_HIDDEN_SIZE: int = 64
LSTM_NUM_LAYERS: int = 2
LSTM_DROPOUT: float = 0.2
LSTM_LEARNING_RATE: float = 1e-3
LSTM_BATCH_SIZE: int = 32
LSTM_MAX_EPOCHS: int = 100
LSTM_EARLY_STOP_PATIENCE: int = 10
LSTM_FEATURE_COLS: list = [
    "soil_moisture", "temperature", "humidity",
    "rainfall_1h", "rain_probability", "kc_factor", "hour_of_day",
]

CONFIDENCE_HIGH: float = 0.75
CONFIDENCE_MEDIUM: float = 0.50
