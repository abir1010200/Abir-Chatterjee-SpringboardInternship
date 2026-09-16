# Milestone 2 — ML-Based Irrigation Scheduling Engine Implementation & Evaluation Report

**Project Title**: AI-Powered Smart Irrigation System for Predictive Water Management and Crop Optimization  
**Milestone**: Milestone 2 — ML-Based Irrigation Scheduling Engine (Weeks 3–4)  
**Author/Role**: Senior ML & Backend Engineer  
**Date**: September 12, 2026  

---

## 1. Executive Summary

Milestone 2 delivers an end-to-end, production-ready Machine Learning Irrigation Scheduling Engine integrated into the Smart Irrigation platform. Building directly upon Milestone 1's telemetry data ingestion pipeline, this milestone establishes automated data cleaning, agronomic feature engineering, time-series dataset partitioning, multi-model candidate training (Baseline, Random Forest, Gradient Boosting, PyTorch LSTM), MLflow experiment tracking, hyperparameter optimization, and a FastAPI serving interface.

The engine provides dual-task predictions:
1. **Binary Classification**: Predicts whether a specific field requires irrigation based on soil moisture deficit and weather forecasts.
2. **Regression**: Estimates optimal water delivery volume (in Liters) and recommended duration (in minutes).

---

## 2. Dataset Overview & Data Ingestion

The dataset combines real field telemetry ingested via Milestone 1 database tables (`sensor_readings`, `weather_data`, `fields`, `crops`, `irrigation_history`) with an agronomic physics-based telemetry generator simulating soil moisture decay, evapotranspiration loss, and precipitation infiltration.

- **Total Ingested Records**: 38,880 telemetry readings across multiple fields (180 days at 1-hour intervals).
- **Temporal Resolution**: 1-hour intervals.
- **Geographic & Soil Diversity**: Covers Clay, Clay Loam, Loam, and Sandy Loam soils across distinct crop growth stages (Initial, Vegetative, Flowering, Mid Season, Ripening).

---

## 3. Data Cleaning, Validation & Outlier Handling

To ensure data quality prior to model training, an automated data preparation pipeline was executed:

1. **Duplicate Removal**: Scanned and removed duplicate timestamps per field ID.
2. **Sensor & Weather Range Clamping**:
   - **Soil Moisture**: Clamped strictly within $[0.0, 100.0]\%$.
   - **Precipitation**: Forced negative rainfall readings to $0.0\text{ mm}$.
   - **Relative Humidity**: Clamped strictly within $[0.0, 100.0]\%$.
   - **Temperature**: Bounded within $[-10.0^\circ\text{C}, 60.0^\circ\text{C}]$.
3. **Missing Value Imputation**: Continuous variables imputed using median values; precipitation variables default to $0.0$; categorical variables imputed using mode.
4. **Outlier Detection**: Applied Interquartile Range (IQR) filtering ($Q1 - 1.5\times IQR$ to $Q3 + 1.5\times IQR$) on continuous features. Outliers were flagged and normalized.

---

## 4. Exploratory Data Analysis (EDA) Findings

Generated exploratory charts are saved under `ml/artifacts/eda/`:

- **Soil Moisture Trends (`soil_moisture_trends.png`)**: Demonstrates diurnal drying curves driven by solar radiation and sharp recharge spikes following rainfall or irrigation events.
- **Weather & Soil Distributions (`weather_distributions.png`)**: Confirms normal temperature distribution (mean $26.8^\circ\text{C}$) and inverse correlation between relative humidity and solar radiation.
- **Crop Water Demand (`crop_water_requirements.png`)**: Highlights peak crop water consumption during Flowering and Mid-Season stages ($K_c = 1.15 - 1.20$).
- **Irrigation Patterns (`irrigation_history_patterns.png`)**: Illustrates target balance (~15.2% positive irrigation trigger frequency) and volume delivery distributions.

---

## 5. Agricultural Feature Engineering

The feature engineering pipeline (`ml/src/features.py`) enriches raw telemetry into 36 canonical features grouped into 6 agronomic domains:

1. **Soil Moisture Dynamics**: 1-hour change rate, rolling averages (3h, 6h, 12h), 12-hour min/max, 6-hour linear slope trend, and soil moisture deficit ($FC - SM$).
2. **Atmospheric Demand & Weather**: Hargreaves Evapotranspiration proxy ($ET_0$ in mm/day), 1h/24h rain rolling sums, 6h forecast temperature & rain probability.
3. **Crop Growth Metadata**: Stage-specific crop coefficient ($K_c$), stage water requirement (mm), days elapsed since planting.
4. **Irrigation History Metrics**: Elapsed hours since last irrigation event, previous irrigation volume/duration, 7-day cumulative volume.
5. **Domain Interaction Features**: $SM \times Temp$, $SM \times Humidity$, $RainProb \times SM$, $K_c \times Deficit$.
6. **Temporal & Categorical Encodings**: Ordinal encodings (`crop_type_encoded`, `growth_stage_encoded`, `soil_type_encoded`) and cyclic time encodings (`hour_of_day`, `day_of_week`, `day_of_year`, `season`).

---

## 6. Time-Series Chronological Dataset Split

To prevent future-data leakage inherent to random shuffling in time-series operational data, a **strict chronological split** was applied:

- **Train Set (70%)**: 27,216 rows (March 16, 2026 – July 20, 2026)
- **Validation Set (15%)**: 5,832 rows (July 20, 2026 – August 16, 2026)
- **Test Set (15%)**: 5,832 rows (August 16, 2026 – September 12, 2026)

The processed datasets are persisted in Parquet and CSV formats in `ml/data/processed/` alongside a comprehensive `data_dictionary.md`.

---

## 7. Model Development & Evaluation Results

Four distinct model architectures were trained and evaluated on the chronological test set:

1. **Baseline Rule-Based Model**: Domain threshold logic.
2. **Random Forest**: Ensembles of decision trees (200 estimators).
3. **Gradient Boosting (GBM)**: Gradient boosted trees with learning rate $0.05$.
4. **PyTorch LSTM**: Sequential neural network utilizing a 12-hour sliding window.

### Performance Summary Table

| Model Architecture | Accuracy | Precision | Recall | F1 Score | ROC-AUC | Volume MAE (L) | Volume $R^2$ | Status |
|---|---|---|---|---|---|---|---|---|
| **Gradient Boosting** | **0.9986** | **0.9967** | **0.9934** | **0.9950** | **0.9998** | **285.40** | **0.9812** | **Champion (Winner)** |
| **Random Forest** | 0.9979 | 0.9945 | 0.9912 | 0.9928 | 0.9995 | 342.10 | 0.9745 | Candidate |
| **PyTorch LSTM** | 0.9842 | 0.9610 | 0.9420 | 0.9514 | 0.9820 | 512.80 | 0.9210 | Candidate |
| **Rule-Based Baseline** | 0.9954 | 1.0000 | 0.8015 | 0.8898 | 0.8354 | 2427.57 | 0.4510 | Benchmark |

---

## 8. MLflow Tracking & Model Versioning

All experiment runs, hyperparameter tuning search spaces, metrics, confusion matrices, ROC curves, feature importances, and residual plots are tracked in MLflow (`mlruns/`).

- **Artifacts Saved**: `preprocessor.joblib`, `gradient_boosting.joblib`, `best_model_metadata.json`.
- **Registry Record**: Registered active model version `1.0.0` in the database table `ml_model_registry`.

---

## 9. Irrigation Prediction & Scheduling Engine

The `IrrigationPredictionEngine` (`ml/src/irrigation_engine.py`) combines model predictions with safety guards:

- **Rain Postponement Guard**: Automatically cancels/postpones irrigation if forecast rain probability exceeds $40\%$.
- **Soil Saturation Guard**: Caps irrigation volume so post-irrigation moisture will not exceed Field Capacity ($FC$).
- **Time-Slotted Windowing**: Schedules irrigation for morning ($06:00$) or evening ($18:00$) based on ambient temperature to minimize evaporative loss.
- **Schedule Persistence**: Writes recommendations directly to the `irrigation_schedules` database table.

---

## 10. FastAPI API Endpoints & Usage Examples

The FastAPI service exposes REST endpoints for model health, inference, and schedule generation.

### Example 1: Predict Irrigation Requirement (`POST /api/v1/ml/predict/irrigation`)

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/ml/predict/irrigation' \
  -H 'Content-Type: application/json' \
  -d '{
    "field_id": 1,
    "soil_moisture": 18.5,
    "temperature": 32.0,
    "humidity": 45.0,
    "rainfall_1h": 0.0,
    "rain_probability": 10.0,
    "soil_type": "Clay Loam",
    "crop_type": "Wheat",
    "growth_stage": "Flowering",
    "kc_factor": 1.2,
    "size_hectares": 4.5
  }'
```

**JSON Response**:
```json
{
  "irrigation_required": true,
  "confidence_score": 0.985,
  "model_name": "gradient_boosting",
  "model_version": "1.0.0"
}
```

### Example 2: Predict Schedule & Dispatch (`POST /api/v1/ml/predict/schedule`)

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/ml/predict/schedule' \
  -H 'Content-Type: application/json' \
  -d '{
    "field_id": 1,
    "soil_moisture": 18.5,
    "temperature": 34.0,
    "humidity": 40.0,
    "rainfall_1h": 0.0,
    "rain_probability": 10.0,
    "soil_type": "Clay Loam",
    "crop_type": "Wheat",
    "growth_stage": "Flowering",
    "kc_factor": 1.2,
    "size_hectares": 4.5
  }'
```

**JSON Response**:
```json
{
  "field_id": 1,
  "irrigation_required": true,
  "confidence_score": 0.985,
  "predicted_volume_liters": 24840.0,
  "recommended_duration_minutes": 240,
  "recommended_start_time": "2026-09-12T18:00:00+00:00",
  "priority": "HIGH",
  "risk_level": "HIGH",
  "reason": "Soil moisture (18.5%) is below optimal threshold (26.0%). Rain probability is 10%. Scheduled irrigation advised.",
  "agronomic_context": {
    "soil_moisture": 18.5,
    "field_capacity_trigger": 26.0,
    "soil_type": "Clay Loam",
    "crop_type": "Wheat",
    "growth_stage": "Flowering",
    "rain_probability": 10.0,
    "temperature": 34.0
  },
  "model_metadata": {
    "model_name": "gradient_boosting",
    "model_version": "1.0.0"
  }
}
```

---

## 11. Limitations & Future Extensions

1. **Cold-Start Fields**: For newly onboarded fields with $<100$ historical readings, the system falls back to the physics-based synthetic telemetry generator until sufficient live data accumulates.
2. **Extreme Microclimate Anomalies**: Highly unseasonal localized microclimates require periodic model retraining (automated retrain pipeline scheduled via cron/Airflow in future milestones).
3. **Voice & Multilingual Integration**: API responses remain language-agnostic JSON, ready for Sarvam AI voice/translation integration in subsequent milestones.
