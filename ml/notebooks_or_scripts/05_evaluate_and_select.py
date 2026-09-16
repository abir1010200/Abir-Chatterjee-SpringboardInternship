"""
ml/notebooks_or_scripts/05_evaluate_and_select.py
Week 4: Model Evaluation Leaderboard, Champion Model Selection & DB Registry Entry.

Performs:
1. Aggregates evaluation results across Baseline, RF, GBM, and LSTM.
2. Generates summary comparison table and leaderboard chart.
3. Persists champion model metadata to ml/artifacts/best_model_metadata.json.
4. Registers active model version in ml_model_registry DB table.
"""
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.app.db.session import SessionLocal, engine, Base
from ml import config as cfg
from ml.evaluation.evaluator import ModelEvaluator
from ml.db.models import MLModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.evaluate_and_select")


def plot_model_comparison_leaderboard(df_sorted: pd.DataFrame, artifact_dir: Path):
    """Plot and save comparative model leaderboard bar chart."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.set_theme(style="whitegrid")

    # Classification F1 Scores
    if "f1" in df_sorted.columns:
        sns.barplot(x="f1", y="model", hue="model", data=df_sorted, ax=axes[0], palette="Blues", legend=False)
        axes[0].set_title("Classification Model Comparison (F1 Score)", fontsize=12, fontweight="bold")
        axes[0].set_xlim([0, 1.05])

    # Volume Regression MAE
    if "volume_mae" in df_sorted.columns:
        sns.barplot(x="volume_mae", y="model", hue="model", data=df_sorted, ax=axes[1], palette="Oranges", legend=False)
        axes[1].set_title("Regression Model Comparison (Volume MAE in L)", fontsize=12, fontweight="bold")

    fig.suptitle("Model Evaluation Leaderboard Comparison", fontsize=15, fontweight="bold")
    plt.tight_layout()

    out_path = artifact_dir / "model_comparison_leaderboard.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def run_evaluation_and_selection():
    logger.info("=== Running Model Evaluation Leaderboard & Selection ===")
    Base.metadata.create_all(bind=engine)
    evaluator = ModelEvaluator(cfg.ARTIFACT_DIR)

    summary_file = cfg.ARTIFACT_DIR / "model_comparison_summary.json"
    if not summary_file.exists():
        logger.error(f"Comparison summary file not found at {summary_file}. Run model training first.")
        return

    with open(summary_file, "r") as f:
        results = json.load(f)

    df_sorted = evaluator.compare_models(results)
    chart_path = plot_model_comparison_leaderboard(df_sorted, cfg.ARTIFACT_DIR)
    logger.info(f"Saved comparison leaderboard chart to {chart_path}")

    # Select best classification & regression models
    champion = df_sorted.iloc[0].to_dict()
    best_model_name = champion["model"]
    logger.info(f"Selected Champion Model: {best_model_name}")

    rf_path = cfg.ARTIFACT_DIR / "random_forest_v1.0.0.joblib" if (cfg.ARTIFACT_DIR / "random_forest_v1.0.0.joblib").exists() else cfg.ARTIFACT_DIR / "random_forest.joblib"
    gbm_path = cfg.ARTIFACT_DIR / "gradient_boosting_v1.0.0.joblib" if (cfg.ARTIFACT_DIR / "gradient_boosting_v1.0.0.joblib").exists() else cfg.ARTIFACT_DIR / "gradient_boosting.joblib"
    lstm_path = cfg.ARTIFACT_DIR / "lstm_v1.0.0.pt" if (cfg.ARTIFACT_DIR / "lstm_v1.0.0.pt").exists() else cfg.ARTIFACT_DIR / "lstm_model.pt"

    artifact_map = {
        "random_forest": rf_path,
        "gradient_boosting": gbm_path,
        "lstm": lstm_path,
        "baseline_rule_based": None,
    }
    best_artifact = artifact_map.get(best_model_name)

    metadata = {
        "best_model_name": best_model_name,
        "version": "1.0.0",
        "metrics": champion,
        "artifact_path": str(best_artifact) if best_artifact else None,
        "preprocessor_path": str(cfg.ARTIFACT_DIR / "preprocessor.joblib"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata_path = cfg.ARTIFACT_DIR / "best_model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Champion metadata written to {metadata_path}")

    # Record in DB Registry
    db = SessionLocal()
    try:
        db.query(MLModelRegistry).filter(MLModelRegistry.is_active == True).update({"is_active": False})
        reg_entry = MLModelRegistry(
            model_name=best_model_name,
            model_version="1.0.0",
            task_type="classification_and_regression",
            metrics_json=json.dumps(champion),
            artifact_path=str(best_artifact) if best_artifact else None,
            is_active=True,
            trained_at=datetime.now(timezone.utc)
        )
        db.add(reg_entry)
        db.commit()
        logger.info(f"Registered champion model '{best_model_name}' in ml_model_registry DB table.")
    except Exception as e:
        logger.error(f"DB registration failed: {e}")
        db.rollback()
    finally:
        db.close()

    return metadata


if __name__ == "__main__":
    run_evaluation_and_selection()
