export interface Farmer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  created_at: string;
}

export interface Field {
  id: number;
  farmer_id: number;
  name: string;
  latitude: number;
  longitude: number;
  size_hectares: number;
  soil_type: string;
  created_at: string;
  crops?: Crop[];
  sensors?: Sensor[];
}

export interface Crop {
  id: number;
  field_id: number;
  crop_type: string;
  growth_stage: string;
  planted_date: string;
  expected_harvest_date?: string;
  kc_factor: number;
  is_active: boolean;
}

export interface Sensor {
  id: string;
  field_id: number;
  sensor_type: string;
  model_name?: string;
  install_date: string;
  status: 'active' | 'stale' | 'offline' | 'error';
  battery_level?: number;
  last_seen?: string;
}

export interface SensorReading {
  id?: number;
  sensor_id: string;
  field_id: number;
  soil_moisture: number;
  temperature_soil?: number;
  battery_level?: number;
  timestamp: string;
  is_valid?: boolean;
  cleaning_flag?: string;
}

export interface WeatherData {
  id?: number;
  field_id: number;
  temperature: number;
  humidity: number;
  rainfall_1h: number;
  rainfall_24h: number;
  rain_probability: number;
  wind_speed?: number;
  solar_radiation?: number;
  forecast_json?: string;
  provider: string;
  timestamp: string;
}

export interface IrrigationHistory {
  id?: number;
  field_id: number;
  volume_liters: number;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
  trigger_source: 'manual' | 'automated_ml' | 'rule_based';
  status: 'scheduled' | 'in_progress' | 'completed' | 'aborted';
  notes?: string;
}

export interface FieldRegistrationPayload {
  farmer: {
    name: string;
    email: string;
    phone?: string;
    address?: string;
  };
  field: {
    name: string;
    latitude: number;
    longitude: number;
    size_hectares: number;
    soil_type: string;
  };
  crop: {
    crop_type: string;
    growth_stage: string;
    planted_date: string;
    kc_factor?: number;
  };
  sensor: {
    sensor_id: string;
    sensor_type: string;
    model_name?: string;
  };
}

export interface ScheduleResponse {
  field_id?: number;
  prediction_id?: number;
  irrigation_required: boolean;
  confidence_score: number;
  predicted_volume_liters?: number;
  recommended_volume_liters?: number;
  recommended_duration_minutes: number;
  recommended_start_time?: string;
  priority?: string;
  risk_level?: string;
  reason?: string;
  model_name?: string;
  model_version?: string;
  rain_postponed?: boolean;
  rain_postponed_reason?: string;
  moisture_deficit_percent?: number;
  generated_at?: string;
}

export interface ModelInfoResponse {
  active_model: string;
  version: string;
  metrics: Record<string, any>;
  trained_at?: string;
  artifact_path?: string;
}
