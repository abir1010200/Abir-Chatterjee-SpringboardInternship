# Smart Irrigation System - Data Dictionary & Dataset Schema

## Overview
This dataset contains agricultural sensor telemetry, weather observations, crop growth metadata, historical irrigation records, and engineered domain features for machine learning irrigation scheduling.

## Target Variables
- **`irrigation_required`** (Binary Class: 0 or 1): Indicates whether field irrigation is required based on soil moisture deficit and weather postponement rules.
- **`irrigation_volume_liters`** (Float, Liters): Recommended water volume delivery in Liters.
- **`recommended_hour`** (Integer, Hour [0-23]): Recommended optimal dispatch hour to minimize evapotranspiration losses.

## Feature Specifications
| Feature Name | Data Type | Agricultural Rationale & Description |
|---|---|---|
| `soil_moisture` | `float64` | Current capacitive soil moisture level (volumetric %). Range: [0, 100]%. |
| `prev_soil_moisture` | `float64` | Lagged soil moisture level from previous 1-hour interval. |
| `rolling_mean_3h` | `float64` | 3-hour rolling average soil moisture (short-term trend). |
| `rolling_mean_6h` | `float64` | 6-hour rolling average soil moisture (medium-term trend). |
| `rolling_mean_12h` | `float64` | 12-hour rolling average soil moisture (daily trend). |
| `rolling_min_12h` | `float64` | 12-hour rolling minimum soil moisture level. |
| `rolling_max_12h` | `float64` | 12-hour rolling maximum soil moisture level. |
| `moisture_trend` | `float64` | 6-hour linear slope of soil moisture change (rate of drying). |
| `moisture_change_rate` | `float64` | 1-hour instant change in soil moisture level. |
| `moisture_deficit` | `float64` | Soil moisture deficit below soil Field Capacity (FC - SM). |
| `temperature` | `float64` | Ambient air temperature (°C). |
| `humidity` | `float64` | Relative atmospheric humidity (%). |
| `rainfall_1h` | `float64` | Precipitation in last 1 hour (mm). |
| `rainfall_24h` | `float64` | Precipitation in last 24 hours (mm). |
| `rain_probability` | `float64` | Forecasted precipitation probability (%). |
| `solar_radiation` | `float64` | Solar irradiance (W/m²). Drives soil evaporation. |
| `forecast_temp_6h` | `float64` | 6-hour ahead temperature forecast (°C). |
| `forecast_rain_prob_6h` | `float64` | 6-hour ahead rain probability forecast (%). |
| `kc_factor` | `float64` | Crop coefficient factor (Kc) reflecting crop water consumption multiplier. |
| `stage_water_requirement_mm` | `float64` | Daily water requirement for current crop growth stage (mm/day). |
| `size_hectares` | `float64` | Total field area in hectares. |
| `prev_irrigation_volume` | `float64` | Water volume delivered in most recent irrigation event (Liters). |
| `hours_since_last_irrigation` | `float64` | Time elapsed since last completed irrigation event (hours). |
| `rolling_7d_irrigation_liters` | `float64` | Cumulative water volume applied over the past 7 days (Liters). |
| `hour_of_day` | `int32` | Hour of day (0-23). Captures diurnal evapotranspiration cycle. |
| `day_of_week` | `int32` | Day of week (0-6). |
| `day_of_year` | `int32` | Day of year (1-365). Captures annual seasonal variations. |
| `season` | `int64` | Seasonal code (0=Winter, 1=Spring, 2=Summer, 3=Autumn). |
| `days_since_planted` | `int64` | Number of days elapsed since crop planting date. |
| `sm_x_temp` | `float64` | Interaction term: Soil moisture x Temperature. |
| `sm_x_humidity` | `float64` | Interaction term: Soil moisture x Humidity. |
| `rain_prob_x_sm` | `float64` | Interaction term: Rain probability x Soil moisture. |
| `kc_x_sm` | `float64` | Interaction term: Crop Kc x Soil moisture deficit. |
| `crop_type_encoded` | `int64` | Ordinal encoded crop category integer. |
| `growth_stage_encoded` | `int64` | Ordinal encoded crop growth stage integer. |
| `soil_type_encoded` | `int64` | Ordinal encoded soil texture type integer. |

## Train / Validation / Test Split Strategy
- **Method**: Chronological (Time-Based) Sequential Split.
- **Train Set**: First 70% of chronological time series.
- **Validation Set**: Next 15% of chronological time series.
- **Test Set**: Final 15% of chronological time series.
- **Rationale**: Operational time-series data exhibits temporal dependence and seasonal autocorrelation. Random shuffling causes data leakage from future observations into training history. Chronological split simulates realistic deployment conditions.