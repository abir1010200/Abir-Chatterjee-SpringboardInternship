# Machine Learning & Exploratory Data Analysis (Milestone 1 & 2)

This directory contains exploratory data analysis (EDA), sensor validation notebooks, and data sanity checks that prepare the feature pipelines for **Milestone 2 (Irrigation Scheduling via Random Forest & LSTM)**.

## Notebooks & Scripts
- `exploratory_data_checks.ipynb`: Inspects PostgreSQL / TimescaleDB sensor telemetry, calculates diurnal moisture decay, verifies weather forecast alignment, and exports baseline feature matrices.
- `seed_and_verify.py`: Quick verification script to query ingested sensor telemetry and weather data for ML feature readiness.

## Target Feature Vector (Milestone 2 Model Input)
- $X = [\text{soil\_moisture}_{t-k..t}, \text{soil\_temp}_t, \text{air\_temp}_t, \text{humidity}_t, \text{rain\_prob}_t, \text{rain\_1h}_t, K_c(\text{crop}, \text{stage}), \text{soil\_type\_code}]$
- $Y = [\text{irrigation\_needed\_boolean}, \text{recommended\_volume\_liters}]$
