"""
ml/notebooks_or_scripts/01_eda.py
Week 3: Exploratory Data Analysis, Data Cleaning, Outlier Detection & Visualizations.

Performs:
1. Telemetry Data Loading & Range Validation.
2. Missing Value & Duplicate Handling.
3. Outlier Detection (IQR Method) & Sensor Range Correction.
4. Statistical Summaries & Distribution Analysis.
5. Visualizations Saved to ml/artifacts/eda/:
   - Soil moisture trends over time.
   - Weather and rainfall distribution histograms/boxplots.
   - Crop water requirement comparison by growth stage.
   - Historical irrigation volume & frequency patterns.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Tuple, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.data.loader import load_all_fields_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.eda")

EDA_DIR = cfg.ARTIFACT_DIR / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)


def clean_and_validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Apply data cleaning, validation, outlier handling, and duplicate removal.
    """
    cleaning_report = {
        "initial_rows": len(df),
        "initial_columns": list(df.columns),
        "missing_values_before": {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
        "duplicates_removed": 0,
        "outliers_detected": {},
        "sensor_corrections": {},
    }

    # 1. Remove duplicate timestamps per field
    if "timestamp" in df.columns and "field_id" in df.columns:
        dups = df.duplicated(subset=["field_id", "timestamp"]).sum()
        df = df.drop_duplicates(subset=["field_id", "timestamp"]).reset_index(drop=True)
        cleaning_report["duplicates_removed"] = int(dups)

    # 2. Correct out-of-range sensor and weather values
    sensor_corrections = {}
    if "soil_moisture" in df.columns:
        invalid_sm = ((df["soil_moisture"] < 0) | (df["soil_moisture"] > 100)).sum()
        df["soil_moisture"] = df["soil_moisture"].clip(0.0, 100.0)
        sensor_corrections["soil_moisture_clamped"] = int(invalid_sm)

    if "rainfall_1h" in df.columns:
        neg_rain = (df["rainfall_1h"] < 0).sum()
        df["rainfall_1h"] = df["rainfall_1h"].clip(lower=0.0)
        sensor_corrections["negative_rain_fixed"] = int(neg_rain)

    if "humidity" in df.columns:
        inv_hum = ((df["humidity"] < 0) | (df["humidity"] > 100)).sum()
        df["humidity"] = df["humidity"].clip(0.0, 100.0)
        sensor_corrections["humidity_clamped"] = int(inv_hum)

    if "temperature" in df.columns:
        inv_temp = ((df["temperature"] < -10) | (df["temperature"] > 60)).sum()
        df["temperature"] = df["temperature"].clip(-10.0, 60.0)
        sensor_corrections["temperature_clamped"] = int(inv_temp)

    cleaning_report["sensor_corrections"] = sensor_corrections

    # 3. Missing Value Handling (Impute / Flag / Drop strategy)
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].isnull().sum() > 0:
            if "rain" in col:
                df[col] = df[col].fillna(0.0)
            else:
                df[col] = df[col].fillna(df[col].median())

    for col in df.columns:
        if df[col].dtype == "object" or isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == "string":
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].mode()[0])

    # 4. Outlier Detection using IQR Method
    outliers_summary = {}
    numeric_cols = ["soil_moisture", "temperature", "humidity", "rainfall_1h", "solar_radiation"]
    for col in numeric_cols:
        if col in df.columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
            outliers_summary[col] = {
                "q1": float(q1),
                "q3": float(q3),
                "iqr": float(iqr),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "n_outliers": n_outliers,
            }

    cleaning_report["outliers_detected"] = outliers_summary
    cleaning_report["final_rows"] = len(df)
    return df, cleaning_report


def generate_eda_visualizations(df: pd.DataFrame) -> List[Path]:
    """Generate and save EDA plots."""
    plot_files = []
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

    # Plot 1: Soil Moisture Patterns Over Time
    fig, ax = plt.subplots(figsize=(12, 5))
    if "timestamp" in df.columns:
        sample_df = df.head(500)
        ax.plot(sample_df["timestamp"], sample_df["soil_moisture"], label="Soil Moisture (%)", color="#1f77b4", linewidth=1.5)
        if "irrigation_required" in sample_df.columns:
            irr_pts = sample_df[sample_df["irrigation_required"] == 1]
            ax.scatter(irr_pts["timestamp"], irr_pts["soil_moisture"], color="red", label="Irrigation Triggered", zorder=5, s=30)
    ax.set_title("Soil Moisture Dynamics & Irrigation Triggers Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Soil Moisture (%)")
    ax.legend(loc="upper right")
    p1 = EDA_DIR / "soil_moisture_trends.png"
    fig.savefig(p1, dpi=200)
    plt.close(fig)
    plot_files.append(p1)

    # Plot 2: Weather & Rainfall Distributions (Histograms & Boxplots)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    sns.histplot(df["temperature"], kde=True, ax=axes[0, 0], color="#ff7f0e")
    axes[0, 0].set_title("Temperature Distribution (°C)")
    
    sns.histplot(df["humidity"], kde=True, ax=axes[0, 1], color="#2ca02c")
    axes[0, 1].set_title("Relative Humidity Distribution (%)")

    sns.boxplot(y=df["rainfall_1h"], ax=axes[1, 0], color="#9467bd")
    axes[1, 0].set_title("Hourly Rainfall Boxplot (mm)")

    sns.boxplot(x=df["soil_type"], y=df["soil_moisture"], hue=df["soil_type"], ax=axes[1, 1], palette="Blues", legend=False)
    axes[1, 1].set_title("Soil Moisture Distribution by Soil Type")
    
    fig.suptitle("Telemetry Weather & Soil Parameter Distributions", fontsize=16, fontweight="bold")
    p2 = EDA_DIR / "weather_distributions.png"
    fig.savefig(p2, dpi=200)
    plt.close(fig)
    plot_files.append(p2)

    # Plot 3: Crop-wise Water Requirements & Kc Factors
    fig, ax1 = plt.subplots(figsize=(10, 5))
    if "growth_stage" in df.columns and "kc_factor" in df.columns:
        stage_group = df.groupby("growth_stage", as_index=False)["kc_factor"].mean()
        sns.barplot(x="growth_stage", y="kc_factor", hue="growth_stage", data=stage_group, ax=ax1, palette="viridis", legend=False)
        ax1.set_title("Average Crop Coefficient (Kc) by Growth Stage", fontsize=14, fontweight="bold")
        ax1.set_xlabel("Growth Stage")
        ax1.set_ylabel("Crop Coefficient (Kc)")
    p3 = EDA_DIR / "crop_water_requirements.png"
    fig.savefig(p3, dpi=200)
    plt.close(fig)
    plot_files.append(p3)

    # Plot 4: Historical Irrigation Volume & Target Balance
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    if "irrigation_required" in df.columns:
        counts = df["irrigation_required"].value_counts()
        axes[0].pie(counts, labels=["No Irrigation", "Irrigation Needed"], autopct="%1.1f%%", colors=["#2ca02c", "#d62728"], startangle=90)
        axes[0].set_title("Target Classification Balance")

    if "irrigation_volume_liters" in df.columns:
        active_vol = df[df["irrigation_volume_liters"] > 0]["irrigation_volume_liters"]
        if not active_vol.empty:
            sns.histplot(active_vol, kde=True, ax=axes[1], color="#17becf")
            axes[1].set_title("Dispatched Water Volume Distribution (L)")
    
    fig.suptitle("Historical Irrigation Patterns & Event Balances", fontsize=16, fontweight="bold")
    p4 = EDA_DIR / "irrigation_history_patterns.png"
    fig.savefig(p4, dpi=200)
    plt.close(fig)
    plot_files.append(p4)

    return plot_files


def run_eda_pipeline() -> Tuple[pd.DataFrame, dict]:
    """Execute complete EDA pipeline."""
    logger.info("=== Running Week 3 EDA & Data Preparation Pipeline ===")
    df_raw = load_all_fields_dataset(min_rows=cfg.SYNTHETIC_MIN_ROWS)
    logger.info(f"Loaded dataset with {len(df_raw)} records and {len(df_raw.columns)} columns.")

    df_cleaned, report = clean_and_validate_data(df_raw)
    logger.info(f"Data cleaning completed: {report['final_rows']} valid rows retained.")

    # Save summary report JSON
    with open(EDA_DIR / "eda_summary.json", "w") as f:
        json.dump(report, f, indent=2)

    plot_paths = generate_eda_visualizations(df_cleaned)
    logger.info(f"Generated {len(plot_paths)} EDA visualization charts in {EDA_DIR}")

    return df_cleaned, report


if __name__ == "__main__":
    df, report = run_eda_pipeline()
    print("EDA Complete. Report summary:")
    print(json.dumps(report, indent=2))
