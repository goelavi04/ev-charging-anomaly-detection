from pydantic import BaseModel
from typing import Optional


class AnomalyRecord(BaseModel):
    session_id:         Optional[str]   = None
    station_id:         Optional[str]   = None
    anomaly_type:       str
    confidence:         float
    energy_kwh:         Optional[float] = None
    total_duration_mins:Optional[float] = None
    charging_time_mins: Optional[float] = None
    idle_ratio:         Optional[float] = None
    energy_zscore:      Optional[float] = None
    port_type:          Optional[str]   = None
    start_time:         Optional[str]   = None


class PredictionResponse(BaseModel):
    filename:         str
    total_sessions:   int
    anomalies_found:  int
    anomaly_rate:     float
    anomalies:        list
    model_used:       str
    accuracy:         float
    f1_macro:         float