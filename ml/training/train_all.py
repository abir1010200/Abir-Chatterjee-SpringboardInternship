"""
ml/training/train_all.py
End-to-end multi-model training and evaluation orchestrator.
Trains Baseline, Random Forest, Gradient Boosting, and LSTM.
Generates evaluation metrics, comparison plots, and registers the winning model.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.app.db.session import SessionLocal, engine, Base
from ml import config as cfg
from ml.data.loader import load_all_fields_dataset
from ml.data.splitter import chronological_split, get_split_summary
from ml.features.engineering import engineer_features
from ml.preprocessing.pipeline import (
    build_preprocessing_pipeline, ALL_FEATURES,
    TARGET_CLASSIFICATION, TARGET_REGRESSION_VOL
)
from ml.models.baseline import BaselineIrrigationModel
from ml.models.random_forest import RandomForestIrrigationModel
from ml.models.gradient_boosting import GradientBoostingIrrigationModel
from ml.models.lstm import LSTMIrrigationModel
from ml.evaluation.evaluator import ModelEvaluator
from ml.db.models import MLModelRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ml.training.train_all")


def run_training_pipeline() -> Dict[str, Any]:
    """Execute end-to-end training and model selection pipeline."""
    logger.info("=== Starting Smart Irrigation ML Training Pipeline ===")
    cfg.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ensure database schema includes ML tables
    logger.info("Ensuring ML tables exist in database...")
    Base.metadata.create_all(bind=engine)

    # 2. Data Ingestion & Fallback
    logger.info("Loading agricultural telemetry dataset...")
    df_raw = load_all_fields_dataset(min_rows=cfg.SYNTHETIC_MIN_ROWS)
    logger.info(f"Loaded {len(df_raw)} records (source: {df_raw.get('data_source', pd.Series(['unknown'])).iloc[0]})")

    # 3. Feature Engineering
    logger.info("Running feature engineering pipeline...")
    df_feat = engineer_features(df_raw)
    logger.info(f"Engineered feature set: {len(df_feat)} rows, {len(df_feat.columns)} columns")

    # 4. Chronological Train/Val/Test Split
    logger.info("Splitting dataset chronologically (70/15/15)...")
    train_df, val_df, test_df = chronological_split(df_feat)
    split_info = get_split_summary(train_df, val_df, test_df)
    logger.info(f"Dataset split: {split_info}")

    # 5. Preprocessing Pipeline
    logger.info("Fitting Scikit-Learn preprocessing ColumnTransformer...")
    preprocessor = build_preprocessing_pipeline()
    preprocessor.fit(train_df)
    preprocessor_path = cfg.ARTIFACT_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    logger.info(f"Preprocessor saved to {preprocessor_path}")

    # Transform tabular features
    X_train = preprocessor.transform(train_df)
    X_val = preprocessor.transform(val_df)
    X_test = preprocessor.transform(test_df)

    y_cls_train = train_df[TARGET_CLASSIFICATION].values.astype(int)
    y_cls_val = val_df[TARGET_CLASSIFICATION].values.astype(int)
    y_cls_test = test_df[TARGET_CLASSIFICATION].values.astype(int)

    y_vol_train = train_df[TARGET_REGRESSION_VOL].values.astype(float)
    y_vol_val = val_df[TARGET_REGRESSION_VOL].values.astype(float)
    y_vol_test = test_df[TARGET_REGRESSION_VOL].values.astype(float)

    evaluator = ModelEvaluator(cfg.ARTIFACT_DIR)
    results: List[Dict[str, Any]] = []

    # ──────────────────────────────────────────────────────────────────────────
    # Model 1: Baseline Rule-Based Model
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Evaluating Baseline Rule-Based Model ---")
    baseline = BaselineIrrigationModel()
    baseline_metrics = baseline.evaluate(test_df)
    results.append(baseline_metrics)

    pred_baseline_df = baseline.predict(test_df)
    y_pred_base = pred_baseline_df["pred_irrigation_required"].values
    cm_base = evaluator.plot_confusion_matrix(y_cls_test, y_pred_base, baseline.name)
    roc_base = evaluator.plot_roc_curve(y_cls_test, pred_baseline_df["pred_confidence"].values, baseline.name)
    res_base = evaluator.plot_volume_residuals(
        y_vol_test[y_cls_test == 1], pred_baseline_df["pred_volume_liters"].values[y_cls_test == 1], baseline.name
    )

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_BASELINE,
        run_name="baseline_evaluation",
        params={"type": "rule_based"},
        metrics=baseline_metrics,
        artifacts=[p for p in [cm_base, roc_base, res_base] if p],
        tags={"dataset_rows": str(len(df_feat)), "model_type": "baseline"},
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model 2: Random Forest
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training Random Forest Model ---")
    rf_model = RandomForestIrrigationModel()
    rf_model.fit(X_train, y_cls_train, y_vol=y_vol_train, feature_names=ALL_FEATURES)
    rf_metrics = rf_model.evaluate(X_test, y_cls_test, y_vol_test)
    results.append(rf_metrics)

    rf_path = rf_model.save(cfg.ARTIFACT_DIR)
    pred_cls_rf, pred_vol_rf, _ = rf_model.predict(X_test)
    probs_rf = rf_model.predict_proba(X_test)

    cm_rf = evaluator.plot_confusion_matrix(y_cls_test, pred_cls_rf, rf_model.name)
    roc_rf = evaluator.plot_roc_curve(y_cls_test, probs_rf, rf_model.name)
    feat_imp_rf = rf_model.get_feature_importances()
    fi_plot_rf = evaluator.plot_feature_importance(feat_imp_rf, rf_model.name)
    res_rf = evaluator.plot_volume_residuals(y_vol_test[y_cls_test == 1], pred_vol_rf[y_cls_test == 1], rf_model.name)

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_RF,
        run_name="rf_training_run",
        params={"n_estimators": cfg.RF_N_ESTIMATORS, "max_depth": cfg.RF_MAX_DEPTH},
        metrics=rf_metrics,
        artifacts=[p for p in [rf_path, cm_rf, roc_rf, fi_plot_rf, res_rf] if p],
        tags={"dataset_rows": str(len(df_feat)), "model_type": "random_forest"},
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model 3: Gradient Boosting
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training Gradient Boosting Model ---")
    gbm_model = GradientBoostingIrrigationModel()
    gbm_model.fit(X_train, y_cls_train, y_vol=y_vol_train, feature_names=ALL_FEATURES)
    gbm_metrics = gbm_model.evaluate(X_test, y_cls_test, y_vol_test)
    results.append(gbm_metrics)

    gbm_path = gbm_model.save(cfg.ARTIFACT_DIR)
    pred_cls_gbm, pred_vol_gbm, _ = gbm_model.predict(X_test)
    probs_gbm = gbm_model.predict_proba(X_test)

    cm_gbm = evaluator.plot_confusion_matrix(y_cls_test, pred_cls_gbm, gbm_model.name)
    roc_gbm = evaluator.plot_roc_curve(y_cls_test, probs_gbm, gbm_model.name)
    feat_imp_gbm = gbm_model.get_feature_importances()
    fi_plot_gbm = evaluator.plot_feature_importance(feat_imp_gbm, gbm_model.name)
    res_gbm = evaluator.plot_volume_residuals(y_vol_test[y_cls_test == 1], pred_vol_gbm[y_cls_test == 1], gbm_model.name)

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_GBM,
        run_name="gbm_training_run",
        params={"n_estimators": cfg.GBM_N_ESTIMATORS, "learning_rate": cfg.GBM_LEARNING_RATE},
        metrics=gbm_metrics,
        artifacts=[p for p in [gbm_path, cm_gbm, roc_gbm, fi_plot_gbm, res_gbm] if p],
        tags={"dataset_rows": str(len(df_feat)), "model_type": "gradient_boosting"},
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model 4: PyTorch LSTM
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training PyTorch LSTM Model ---")
    lstm_model = LSTMIrrigationModel(max_epochs=20)  # fast convergence on CPU
    lstm_model.fit(train_df, val_df)
    lstm_metrics = lstm_model.evaluate(test_df)
    results.append(lstm_metrics)

    lstm_path = lstm_model.save(cfg.ARTIFACT_DIR)
    X_seq_test, y_seq_cls, y_seq_vol = lstm_model.create_sequences(test_df, is_training=False)
    if len(X_seq_test) > 0:
        pred_cls_lstm, pred_vol_lstm, conf_lstm = lstm_model.predict(test_df)
        cm_lstm = evaluator.plot_confusion_matrix(y_seq_cls, pred_cls_lstm, lstm_model.name)
        roc_lstm = evaluator.plot_roc_curve(y_seq_cls, conf_lstm, lstm_model.name)
        res_lstm = evaluator.plot_volume_residuals(
            y_seq_vol[y_seq_cls == 1] if y_seq_vol is not None else np.array([]),
            pred_vol_lstm[y_seq_cls == 1],
            lstm_model.name
        )
    else:
        cm_lstm, roc_lstm, res_lstm = None, None, None

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_LSTM,
        run_name="lstm_training_run",
        params={"seq_len": cfg.LSTM_SEQUENCE_LENGTH, "hidden_dim": cfg.LSTM_HIDDEN_SIZE},
        metrics=lstm_metrics,
        artifacts=[p for p in [lstm_path, cm_lstm, roc_lstm, res_lstm] if p],
        tags={"dataset_rows": str(len(df_feat)), "model_type": "lstm"},
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model Comparison & Winner Selection
    # ──────────────────────────────────────────────────────────────────────────
    comparison_df = evaluator.compare_models(results)
    logger.info(f"\nModel Comparison Leaderboard:\n{comparison_df.to_string()}")

    best_record = comparison_df.iloc[0].to_dict()
    best_model_name = best_record["model"]
    logger.info(f"Champion Model Selected: {best_model_name} (F1: {best_record.get('f1')})")

    # Determine winning artifact path
    artifact_map = {
        "random_forest": rf_path,
        "gradient_boosting": gbm_path,
        "lstm": lstm_path,
        "baseline_rule_based": None,
    }
    best_artifact = artifact_map.get(best_model_name)

    # Save metadata for Serving API
    best_metadata = {
        "best_model_name": best_model_name,
        "version": "1.0.0",
        "metrics": best_record,
        "artifact_path": str(best_artifact) if best_artifact else None,
        "preprocessor_path": str(preprocessor_path),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path = cfg.ARTIFACT_DIR / "best_model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(best_metadata, f, indent=2)

    # Register in DB
    db = SessionLocal()
    try:
        # Mark previous active models as inactive
        db.query(MLModelRegistry).filter(MLModelRegistry.is_active == True).update({"is_active": False})

        registry_entry = MLModelRegistry(
            model_name=best_model_name,
            model_version="1.0.0",
            task_type="classification_and_regression",
            metrics_json=json.dumps(best_record),
            artifact_path=str(best_artifact) if best_artifact else None,
            is_active=True,
            trained_at=datetime.now(timezone.utc),
        )
        db.add(registry_entry)
        db.commit()
        logger.info(f"Registered {best_model_name} into ml_model_registry (ID: {registry_entry.id})")
    except Exception as e:
        logger.error(f"Failed to record in model registry: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info("=== Smart Irrigation Training Pipeline Complete ===")
    return best_metadata


if __name__ == "__main__":
    run_training_pipeline()
