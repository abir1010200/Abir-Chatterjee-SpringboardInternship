"""
ml/notebooks_or_scripts/03_train_baseline.py
Week 4: Baseline Model Training, Evaluation & MLflow Logging.

Performs:
1. Loads test dataset from ml/data/processed/.
2. Evaluates Baseline Rule-Based Model.
3. Logs metrics (Accuracy, Precision, Recall, F1, ROC-AUC, MAE, RMSE) & artifacts to MLflow.
"""
import sys
import logging
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.models.baseline import BaselineIrrigationModel
from ml.evaluation.evaluator import ModelEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.train_baseline")


def run_baseline_training():
    logger.info("=== Running Baseline Model Evaluation & MLflow Logging ===")
    test_path = cfg.ML_ROOT / "data" / "processed" / "test_dataset.parquet"
    if not test_path.exists():
        logger.error(f"Test dataset not found at {test_path}. Run 02_feature_engineering.py first.")
        return

    test_df = pd.read_parquet(test_path)
    baseline = BaselineIrrigationModel()
    metrics = baseline.evaluate(test_df)
    logger.info(f"Baseline Metrics: {metrics}")

    evaluator = ModelEvaluator(cfg.ARTIFACT_DIR)
    pred_df = baseline.predict(test_df)
    y_true = test_df["irrigation_required"].values
    y_pred = pred_df["pred_irrigation_required"].values
    y_conf = pred_df["pred_confidence"].values

    cm_path = evaluator.plot_confusion_matrix(y_true, y_pred, baseline.name)
    roc_path = evaluator.plot_roc_curve(y_true, y_conf, baseline.name)

    artifacts = [p for p in [cm_path, roc_path] if p]

    evaluator.log_to_mlflow(
        experiment_name=cfg.MLFLOW_EXPERIMENT_BASELINE,
        run_name="baseline_rule_based_run",
        params={"model_type": "rule_based", "rain_cutoff": cfg.RAIN_POSTPONE_THRESHOLD},
        metrics=metrics,
        artifacts=artifacts,
        tags={"dataset": "processed_test", "milestone": "milestone_2"}
    )
    logger.info("Baseline evaluation complete & logged to MLflow.")
    return metrics


if __name__ == "__main__":
    run_baseline_training()
