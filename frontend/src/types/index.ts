export interface Anomaly {
  session_id: string;
  station_id: string;
  anomaly_type: string;
  confidence: number;
  energy_kwh: number;
  total_duration_mins: number;
  charging_time_mins: number;
  idle_ratio: number;
  energy_zscore: number;
  port_type: string;
  start_time: string;
}

export interface PredictionResponse {
  filename: string;
  total_sessions: number;
  anomalies_found: number;
  anomaly_rate: number;
  anomalies: Anomaly[];
  model_used: string;
  accuracy: number;
  f1_macro: number;
}

export interface AnomaliesResponse {
  total: number;
  anomalies: Anomaly[];
}

export interface StatsResponse {
  total: number;
  by_type: Record<string, number>;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string | null;
  accuracy: number | null;
}
