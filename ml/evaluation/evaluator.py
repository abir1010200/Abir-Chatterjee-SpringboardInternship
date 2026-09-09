"""
ml/evaluation/evaluator.py
Unified evaluation, visualization, comparison, and MLflow logging
for all smart irrigation models.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, roc_curve,
    mean_absolute_error, mean_squared_error, r2_score
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg

logger = logging.getLogger(__name__)

# Try to import mlflow
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not installed. Local fallback enabled.")


class ModelEvaluator:
    """
    Evaluator that produces standardized performance metrics, publication-quality
    plots, and logs to MLflow when available.
    """

    def __init__(self, artifact_dir: Optional[Path] = None):
        self.artifact_dir = Path(artifact_dir or cfg.ARTIFACT_DIR)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.tracking_uri = cfg.MLFLOW_TRACKING_URI

        if MLFLOW_AVAILABLE:
            tracking_uri = self.tracking_uri
            if tracking_uri.startswith("http"):
                import socket
                from urllib.parse import urlparse
                parsed = urlparse(tracking_uri)
                try:
                    s = socket.create_connection((parsed.hostname or "localhost", parsed.port or 5000), timeout=0.5)
                    s.close()
                    mlflow.set_tracking_uri(tracking_uri)
                    logger.info(f"Connected to remote MLflow server at {tracking_uri}")
                except Exception:
                    import os
                    os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
                    local_runs = (Path(__file__).resolve().parent.parent.parent / "mlruns").resolve()
                    local_runs.mkdir(exist_ok=True)
                    mlflow.set_tracking_uri(local_runs.as_uri())
                    logger.info(f"MLflow server not reachable at {tracking_uri}. Using local tracking store at {local_runs}")
            else:
                mlflow.set_tracking_uri(tracking_uri)

    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, model_name: str) -> Path:
        """Plot and save confusion matrix heatmap."""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["No Irrigation (0)", "Irrigate (1)"],
            yticklabels=["No Irrigation (0)", "Irrigate (1)"],
        )
        plt.title(f"Confusion Matrix — {model_name.replace('_', ' ').title()}")
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()

        out_path = self.artifact_dir / f"confusion_matrix_{model_name}.png"
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def plot_roc_curve(self, y_true: np.ndarray, y_score: np.ndarray, model_name: str) -> Optional[Path]:
        """Plot and save ROC curve."""
        try:
            fpr, tpr, _ = roc_curve(y_true, y_score)
            auc_score = roc_auc_score(y_true, y_score)

            plt.figure(figsize=(6, 5))
            plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC (AUC = {auc_score:.3f})")
            plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.title(f"ROC Curve — {model_name.replace('_', ' ').title()}")
            plt.legend(loc="lower right")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            out_path = self.artifact_dir / f"roc_curve_{model_name}.png"
            plt.savefig(out_path, dpi=200)
            plt.close()
            return out_path
        except Exception as e:
            logger.warning(f"Failed to plot ROC curve for {model_name}: {e}")
            return None

    def plot_feature_importance(self, importances: Dict[str, float], model_name: str, top_n: int = 15) -> Optional[Path]:
        """Plot top-N feature importances bar chart."""
        if not importances:
            return None

        items = list(importances.items())[:top_n]
        features = [k for k, _ in items]
        scores = [v for _, v in items]

        plt.figure(figsize=(10, 6))
        y_pos = np.arange(len(features))
        plt.barh(y_pos, scores, align="center", color="#2b5c8f")
        plt.yticks(y_pos, features)
        plt.gca().invert_yaxis()
        plt.xlabel("Importance Score")
        plt.title(f"Top {top_n} Features — {model_name.replace('_', ' ').title()}")
        plt.grid(True, axis="x", alpha=0.3)
        plt.tight_layout()

        out_path = self.artifact_dir / f"feature_importance_{model_name}.png"
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def plot_volume_residuals(self, y_true: np.ndarray, y_pred: np.ndarray, model_name: str) -> Optional[Path]:
        """Plot scatter of actual vs predicted irrigation volumes."""
        if len(y_true) == 0 or len(y_pred) == 0:
            return None

        plt.figure(figsize=(6, 5))
        plt.scatter(y_true, y_pred, alpha=0.5, color="#1e824c", edgecolors="k", s=30)
        max_val = max(np.max(y_true), np.max(y_pred), 100.0)
        plt.plot([0, max_val], [0, max_val], "r--", label="Ideal Fit (y=x)")
        plt.xlabel("Actual Volume (Liters)")
        plt.ylabel("Predicted Volume (Liters)")
        plt.title(f"Volume Prediction — {model_name.replace('_', ' ').title()}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        out_path = self.artifact_dir / f"volume_residuals_{model_name}.png"
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def log_to_mlflow(
        self,
        experiment_name: str,
        run_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, Any],
        artifacts: List[Path],
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Log parameters, metrics, and artifact paths to MLflow."""
        if not MLFLOW_AVAILABLE:
            logger.info("MLflow not available. Storing metrics locally.")
            return None

        try:
            mlflow.set_experiment(experiment_name)
            with mlflow.start_run(run_name=run_name) as run:
                # Log tags
                if tags:
                    mlflow.set_tags(tags)
                # Log hyperparameters
                for k, v in params.items():
                    if v is not None:
                        mlflow.log_param(k, str(v))
                # Log metrics
                for k, v in metrics.items():
                    if isinstance(v, (int, float)) and not np.isnan(v):
                        mlflow.log_metric(k, float(v))
                # Log image artifacts
                for art in artifacts:
                    if art and art.exists():
                        mlflow.log_artifact(str(art))

                logger.info(f"MLflow run '{run_name}' recorded (ID: {run.info.run_id})")
                return run.info.run_id
        except Exception as e:
            logger.warning(f"MLflow logging encountered warning: {e}. Metrics saved locally.")
            return None

    def compare_models(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Compare models across metrics and pick the best performer.
        Returns sorted DataFrame.
        """
        df = pd.DataFrame(results)
        sort_col = "f1" if "f1" in df.columns else "accuracy"
        df_sorted = df.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

        summary_path = self.artifact_dir / "model_comparison_summary.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)

        csv_path = self.artifact_dir / "model_comparison_summary.csv"
        df_sorted.to_csv(csv_path, index=False)
        logger.info(f"Model comparison table saved to {csv_path}")

        return df_sorted
