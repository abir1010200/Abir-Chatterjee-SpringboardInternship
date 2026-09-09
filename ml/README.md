# 🧠 Machine Learning Engine — Milestone 2

> **AI-Powered Precision Irrigation & Volume Optimization Engine**

This directory contains the feature engineering pipelines, model training suite, experiment tracking, physics-constrained optimization scheduler, and FastAPI serving microservice for **Milestone 2**.

---

## 🏗️ ML Module Directory Structure

```
ml/
├── artifacts/                 # Serialized model weights (.joblib, .pt), confusion matrices, & ROC plots
├── config.py                  # ML configuration constants & threshold parameters
├── data/                      # Dataset loaders, synthetic diurnal telemetry generator, chron-splitter
├── db/                        # ML database models (`ml_model_registry`, `irrigation_predictions`) & SQL migrations
├── evaluation/                # Evaluator metrics calculator & MLflow experiment tracking logger
├── features/                  # 47-feature domain engineering pipeline (`engineering.py`)
├── models/                    # Model implementations:
│   ├── baseline.py            # FAO-56 physics rule-based model
│   ├── random_forest.py       # Random Forest classifier & regressor
│   ├── gradient_boosting.py   # Gradient Boosted Decision Trees (Champion)
│   └── lstm.py                # PyTorch 2-layer LSTM time-series model
├── optimization/              # Irrigation scheduler, rain postponed shields, & over-watering locks
├── preprocessing/             # ColumnTransformer, StandardScaler, and OneHotEncoder pipeline
├── serving/                   # FastAPI serving application (`api.py` on port 8001)
├── tests/                     # 15 Pytest unit tests covering ML models, features, & API endpoints
└── training/                  # End-to-end model training orchestrator (`train_all.py`)
```

---

## 🚀 Model Training & Evaluation Workflow

To train all models, log runs to MLflow, and register the active champion model into the database:

```bash
python -m ml.training.train_all --synthetic
```

### Model Benchmark Leaderboard

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Volume MAE (L) | $R^2$ Score | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (FAO-56 Physics)** | 99.42% | 1.0000 | 0.8515 | 0.9198 | 0.9089 | 1,967.8 L | N/A | Fallback |
| **Random Forest (100 Trees)** | **99.42%** | **1.0000** | **0.8515** | **0.9198** | **0.9998** | 3,283.9 L | -1.69 | Qualified |
| **Gradient Boosting (GBM)** ⭐ | **99.27%** | **0.8661** | **0.9604** | **0.9108** | **0.9892** | **576.2 L** | **0.781** | **Champion** |
| **PyTorch LSTM Network** | 95.97% | 0.4769 | 0.3069 | 0.3735 | 0.8387 | 12,028.1 L | N/A | Qualified |

---

## 🔌 ML Serving Microservice (Port 8001)

Start the standalone ML serving FastAPI server:
```bash
python -m uvicorn ml.serving.api:app --host 0.0.0.0 --port 8001 --reload
```

### API Endpoints
- `GET /health`: Liveness probe reporting model status.
- `GET /model/info`: Active champion model metadata, version, and metrics.
- `POST /predict/irrigation`: Binary classification prediction.
- `POST /predict/volume`: Water volume regression prediction in Liters.
- `POST /predict/schedule`: Actionable field schedule with rain delay constraints.
- `GET /recommendation/{field_id}`: Real-time DB lookup + ML inference + schedule generation.

---

## 🧪 Unit Testing
Run the 15-test ML engine test suite:
```bash
python -m pytest ml/tests/ -v
```
