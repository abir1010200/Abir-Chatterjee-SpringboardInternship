"""
ml/serving/model_loader.py
Model registry lookup and artifact loader.
Hot-loads the active champion model with fallback to domain baseline.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.models.baseline import BaselineIrrigationModel
from ml.models.random_forest import RandomForestIrrigationModel
from ml.models.gradient_boosting import GradientBoostingIrrigationModel
from ml.models.lstm import LSTMIrrigationModel
from ml.features.engineering import engineer_features
from ml.db.models import MLModelRegistry
from backend.app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class ServedModelWrapper:
    """Wrapper encapsulating model inference, feature preprocessing, and metadata."""

    def __init__(
        self,
        model_name: str,
        version: str,
        model_instance: Any,
        preprocessor: Optional[Any] = None,
        metrics: Optional[Dict[str, Any]] = None,
        artifact_path: Optional[str] = None,
        trained_at: Optional[str] = None,
    ):
        self.model_name = model_name
        self.version = version
        self.model = model_instance
        self.preprocessor = preprocessor
        self.metrics = metrics or {}
        self.artifact_path = artifact_path
        self.trained_at = trained_at

    def predict_features(self, feat_dict: Dict[str, Any]) -> Tuple[bool, float, float, Optional[int]]:
        """
        Take dictionary of raw/semi-raw features, run feature engineering,
        preprocess, and predict.
        Returns: (irrigation_required, volume_liters, confidence_score, recommended_hour)
        """
        # Baseline fallback
        if self.model_name == "baseline_rule_based" or self.preprocessor is None:
            if hasattr(self.model, "predict_row"):
                row = pd.Series(feat_dict)
                req, vol, conf, rec_hour = self.model.predict_row(row)
                return bool(req), float(vol), float(conf), int(rec_hour)
            else:
                baseline = BaselineIrrigationModel()
                req, vol, conf, rec_hour = baseline.predict_row(pd.Series(feat_dict))
                return bool(req), float(vol), float(conf), int(rec_hour)

        # Tabular model pipeline
        df_input = pd.DataFrame([feat_dict])
        df_eng = engineer_features(df_input)

        if self.model_name == "lstm":
            # For single-point serving, pad with recent state or replicate
            padded = pd.concat([df_eng] * cfg.LSTM_SEQUENCE_LENGTH, ignore_index=True)
            pred_cls, pred_vol, conf = self.model.predict(padded)
            req = bool(pred_cls[-1]) if len(pred_cls) > 0 else False
            vol = float(pred_vol[-1]) if len(pred_vol) > 0 else 0.0
            confidence = float(conf[-1]) if len(conf) > 0 else 0.8
            rec_hour = cfg.PREFERRED_IRRIGATION_HOUR_MORNING
            return req, vol, confidence, rec_hour

        # Sklearn tabular models (RF, GBM)
        try:
            X_trans = self.preprocessor.transform(df_eng)
            pred_cls, pred_vol, conf = self.model.predict(X_trans)
            req = bool(pred_cls[0])
            vol = float(pred_vol[0])
            confidence = float(conf[0])
            rec_hour = (
                cfg.PREFERRED_IRRIGATION_HOUR_EVENING
                if float(feat_dict.get("temperature", 25.0)) > cfg.HIGH_TEMP_EVENING_THRESHOLD
                else cfg.PREFERRED_IRRIGATION_HOUR_MORNING
            )
            return req, vol, confidence, rec_hour
        except Exception as e:
            logger.warning(f"Inference error in {self.model_name}: {e}. Falling back to baseline.")
            baseline = BaselineIrrigationModel()
            req, vol, conf, rec_hour = baseline.predict_row(pd.Series(feat_dict))
            return bool(req), float(vol), float(conf), int(rec_hour)


def load_active_model() -> ServedModelWrapper:
    """
    Load the champion model.
    1. Check `best_model_metadata.json`
    2. Check DB `ml_model_registry`
    3. Fall back to Baseline
    """
    meta_file = cfg.ARTIFACT_DIR / "best_model_metadata.json"
    preprocessor_file = cfg.ARTIFACT_DIR / "preprocessor.joblib"
    preprocessor = None

    if preprocessor_file.exists():
        try:
            preprocessor = joblib.load(preprocessor_file)
        except Exception as e:
            logger.warning(f"Could not load preprocessor: {e}")

    # Check local metadata JSON first
    if meta_file.exists():
        try:
            with open(meta_file, "r") as f:
                meta = json.load(f)
            model_name = meta.get("best_model_name", "baseline_rule_based")
            version = meta.get("version", "1.0.0")
            art_path = meta.get("artifact_path")
            metrics = meta.get("metrics", {})
            trained_at = meta.get("trained_at")

            if art_path and Path(art_path).exists():
                art_p = Path(art_path)
                if model_name == "random_forest":
                    loaded = RandomForestIrrigationModel.load(art_p)
                elif model_name == "gradient_boosting":
                    loaded = GradientBoostingIrrigationModel.load(art_p)
                elif model_name == "lstm":
                    loaded = LSTMIrrigationModel.load(art_p)
                else:
                    loaded = BaselineIrrigationModel()

                logger.info(f"Loaded champion model '{model_name}' (v{version}) from {art_path}")
                return ServedModelWrapper(
                    model_name=model_name,
                    version=version,
                    model_instance=loaded,
                    preprocessor=preprocessor,
                    metrics=metrics,
                    artifact_path=art_path,
                    trained_at=trained_at,
                )
        except Exception as e:
            logger.warning(f"Error loading from best_model_metadata.json: {e}")

    # Check DB registry
    try:
        db = SessionLocal()
        record = db.query(MLModelRegistry).filter(MLModelRegistry.is_active == True).order_by(MLModelRegistry.id.desc()).first()
        if record and record.artifact_path and Path(record.artifact_path).exists():
            art_p = Path(record.artifact_path)
            model_name = record.model_name
            if model_name == "random_forest":
                loaded = RandomForestIrrigationModel.load(art_p)
            elif model_name == "gradient_boosting":
                loaded = GradientBoostingIrrigationModel.load(art_p)
            elif model_name == "lstm":
                loaded = LSTMIrrigationModel.load(art_p)
            else:
                loaded = BaselineIrrigationModel()

            metrics = json.loads(record.metrics_json) if record.metrics_json else {}
            db.close()
            return ServedModelWrapper(
                model_name=model_name,
                version=record.model_version,
                model_instance=loaded,
                preprocessor=preprocessor,
                metrics=metrics,
                artifact_path=record.artifact_path,
                trained_at=str(record.trained_at),
            )
        db.close()
    except Exception as e:
        logger.warning(f"DB model lookup failed: {e}")

    # Fallback to Baseline
    logger.info("Defaulting to BaselineIrrigationModel (rule-based fallback)")
    return ServedModelWrapper(
        model_name="baseline_rule_based",
        version="1.0.0",
        model_instance=BaselineIrrigationModel(),
        preprocessor=None,
        metrics={"f1": 0.85, "model": "baseline_rule_based"},
        artifact_path=None,
        trained_at=None,
    )
