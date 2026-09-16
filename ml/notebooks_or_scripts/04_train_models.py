"""
ml/notebooks_or_scripts/04_train_models.py
Week 4: Model Training, Hyperparameter Tuning (XGBoost/GBM & Random Forest), LSTM Time-Series Training & MLflow Tracking.

Performs:
1. Loads train, val, and test datasets from ml/data/processed/.
2. Applies Scikit-Learn preprocessing ColumnTransformer.
3. Performs Hyperparameter Tuning on Random Forest and Gradient Boosting models.
4. Trains Random Forest, Gradient Boosting, and PyTorch LSTM models.
5. Evaluates classification & regression metrics (Accuracy, Precision, Recall, F1, ROC-AUC, MAE, RMSE, R²).
6. Logs parameters, tuned hyperparams, visual plots, and artifacts to MLflow.
"""
import sys
import json
import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.preprocessing.pipeline import (
    build_preprocessing_pipeline, ALL_FEATURES,
    TARGET_CLASSIFICATION, TARGET_REGRESSION_VOL
)
from ml.models.random_forest import RandomForestIrrigationModel
from ml.models.gradient_boosting import GradientBoostingIrrigationModel
from ml.models.lstm import LSTMIrrigationModel
from ml.evaluation.evaluator import ModelEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.train_models")


def tune_random_forest(X_train, y_cls_train, X_val, y_cls_val):
    """Hyperparameter tuning for Random Forest Classifier using Randomized Search concept."""
    logger.info("Executing Hyperparameter Tuning for Random Forest...")
    from sklearn.ensemble import RandomForestClassifier
    best_score = -1.0
    best_params = {
        "n_estimators": cfg.RF_N_ESTIMATORS,
        "max_depth": cfg.RF_MAX_DEPTH,
        "min_samples_split": cfg.RF_MIN_SAMPLES_SPLIT
    }
    
    param_grid = [
        {"n_estimators": 100, "max_depth": 10, "min_samples_split": 5},
        {"n_estimators": 200, "max_depth": 15, "min_samples_split": 5},
        {"n_estimators": 250, "max_depth": 20, "min_samples_split": 2},
    ]

    for params in param_grid:
        clf = RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            min_samples_split=params["min_samples_split"],
            random_state=cfg.RANDOM_SEED,
            class_weight=cfg.RF_CLASS_WEIGHT
        )
        clf.fit(X_train, y_cls_train)
        score = clf.score(X_val, y_cls_val)
        if score > best_score:
            best_score = score
            best_params = params

    logger.info(f"Random Forest Best Tuned Params: {best_params} (Val Accuracy: {best_score:.4f})")
    return best_params


def tune_gradient_boosting(X_train, y_cls_train, X_val, y_cls_val):
    """Hyperparameter tuning for Gradient Boosting Classifier."""
    logger.info("Executing Hyperparameter Tuning for Gradient Boosting...")
    from sklearn.ensemble import GradientBoostingClassifier
    best_score = -1.0
    best_params = {
        "n_estimators": cfg.GBM_N_ESTIMATORS,
        "max_depth": cfg.GBM_MAX_DEPTH,
        "learning_rate": cfg.GBM_LEARNING_RATE
    }

    param_grid = [
        {"n_estimators": 100, "max_depth": 3, "learning_rate": 0.1},
        {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05},
        {"n_estimators": 250, "max_depth": 6, "learning_rate": 0.03},
    ]

    for params in param_grid:
        gbm = GradientBoostingClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            learning_rate=params["learning_rate"],
            random_state=cfg.RANDOM_SEED
        )
        gbm.fit(X_train, y_cls_train)
        score = gbm.score(X_val, y_cls_val)
        if score > best_score:
            best_score = score
            best_params = params

    logger.info(f"Gradient Boosting Best Tuned Params: {best_params} (Val Accuracy: {best_score:.4f})")
    return best_params


def run_model_training():
    logger.info("=== Running Week 4 Model Training, Tuning & MLflow Logging ===")
    
    # 1. Load Processed Datasets
    data_dir = cfg.ML_ROOT / "data" / "processed"
    train_df = pd.read_parquet(data_dir / "train_dataset.parquet")
    val_df = pd.read_parquet(data_dir / "val_dataset.parquet")
    test_df = pd.read_parquet(data_dir / "test_dataset.parquet")

    logger.info(f"Loaded datasets - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # 2. Fit Preprocessor
    preprocessor = build_preprocessing_pipeline()
    preprocessor.fit(train_df)
    preprocessor_path = cfg.ARTIFACT_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    logger.info(f"Saved fitted preprocessor to {preprocessor_path}")

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
    results = []

    # ──────────────────────────────────────────────────────────────────────────
    # Model 1: Random Forest
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training & Tuning Random Forest ---")
    rf_best_params = tune_random_forest(X_train, y_cls_train, X_val, y_cls_val)
    rf_model = RandomForestIrrigationModel(
        n_estimators=rf_best_params["n_estimators"],
        max_depth=rf_best_params["max_depth"]
    )
    rf_model.fit(X_train, y_cls_train, y_vol=y_vol_train, feature_names=ALL_FEATURES)
    rf_metrics = rf_model.evaluate(X_test, y_cls_test, y_vol_test)
    
    # Calculate R2 for regression
    pred_cls_rf, pred_vol_rf, _ = rf_model.predict(X_test)
    mask = y_cls_test == 1
    if mask.sum() > 0:
        rf_metrics["volume_r2"] = round(r2_score(y_vol_test[mask], pred_vol_rf[mask]), 4)
    results.append(rf_metrics)

    rf_path = rf_model.save(cfg.ARTIFACT_DIR)
    probs_rf = rf_model.predict_proba(X_test)
    cm_rf = evaluator.plot_confusion_matrix(y_cls_test, pred_cls_rf, rf_model.name)
    roc_rf = evaluator.plot_roc_curve(y_cls_test, probs_rf, rf_model.name)
    feat_imp_rf = rf_model.get_feature_importances()
    fi_rf = evaluator.plot_feature_importance(feat_imp_rf, rf_model.name)
    res_rf = evaluator.plot_volume_residuals(y_vol_test[mask], pred_vol_rf[mask], rf_model.name)

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_RF,
        run_name="rf_tuned_run",
        params=rf_best_params,
        metrics=rf_metrics,
        artifacts=[p for p in [rf_path, cm_rf, roc_rf, fi_rf, res_rf] if p],
        tags={"model_type": "random_forest", "tuned": "true"}
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model 2: Gradient Boosting
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training & Tuning Gradient Boosting ---")
    gbm_best_params = tune_gradient_boosting(X_train, y_cls_train, X_val, y_cls_val)
    gbm_model = GradientBoostingIrrigationModel(
        n_estimators=int(gbm_best_params["n_estimators"]),
        max_depth=int(gbm_best_params["max_depth"]),
        learning_rate=float(gbm_best_params["learning_rate"])
    )
    gbm_model.fit(X_train, y_cls_train, y_vol=y_vol_train, feature_names=ALL_FEATURES)
    gbm_metrics = gbm_model.evaluate(X_test, y_cls_test, y_vol_test)
    
    pred_cls_gbm, pred_vol_gbm, _ = gbm_model.predict(X_test)
    if mask.sum() > 0:
        gbm_metrics["volume_r2"] = round(r2_score(y_vol_test[mask], pred_vol_gbm[mask]), 4)
    results.append(gbm_metrics)

    gbm_path = gbm_model.save(cfg.ARTIFACT_DIR)
    probs_gbm = gbm_model.predict_proba(X_test)
    cm_gbm = evaluator.plot_confusion_matrix(y_cls_test, pred_cls_gbm, gbm_model.name)
    roc_gbm = evaluator.plot_roc_curve(y_cls_test, probs_gbm, gbm_model.name)
    feat_imp_gbm = gbm_model.get_feature_importances()
    fi_gbm = evaluator.plot_feature_importance(feat_imp_gbm, gbm_model.name)
    res_gbm = evaluator.plot_volume_residuals(y_vol_test[mask], pred_vol_gbm[mask], gbm_model.name)

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_GBM,
        run_name="gbm_tuned_run",
        params=gbm_best_params,
        metrics=gbm_metrics,
        artifacts=[p for p in [gbm_path, cm_gbm, roc_gbm, fi_gbm, res_gbm] if p],
        tags={"model_type": "gradient_boosting", "tuned": "true"}
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Model 3: PyTorch LSTM Time-Series Sequence Model
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("--- Training PyTorch LSTM Sequence Model ---")
    lstm_model = LSTMIrrigationModel(max_epochs=20)
    lstm_model.fit(train_df, val_df)
    lstm_metrics = lstm_model.evaluate(test_df)
    results.append(lstm_metrics)

    lstm_path = lstm_model.save(cfg.ARTIFACT_DIR)
    X_seq_test, y_seq_cls, y_seq_vol = lstm_model.create_sequences(test_df, is_training=False)
    if y_seq_cls is not None and len(X_seq_test) > 0:
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
        run_name="lstm_sequence_run",
        params={"seq_len": cfg.LSTM_SEQUENCE_LENGTH, "hidden_dim": cfg.LSTM_HIDDEN_SIZE},
        metrics=lstm_metrics,
        artifacts=[p for p in [lstm_path, cm_lstm, roc_lstm, res_lstm] if p],
        tags={"model_type": "lstm"}
    )

    logger.info("All model training, hyperparameter tuning & MLflow logging completed.")
    return results


if __name__ == "__main__":
    run_model_training()
