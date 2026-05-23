import os
import sys
import json
import joblib
import io
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))
from label_engineering import engineer_features, get_feature_columns

from backend.database import save_anomalies_batch, fetch_anomalies
from backend.models import PredictionResponse

app = FastAPI(title="EV Anomaly Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR      = os.path.dirname(__file__)
MODELS_DIR    = os.path.join(BASE_DIR, '..', 'ml', 'models')
FRONTEND_DIST = os.path.join(BASE_DIR, '..', 'frontend', 'dist')

try:
    model    = joblib.load(os.path.join(MODELS_DIR, 'best_model.pkl'))
    le       = joblib.load(os.path.join(MODELS_DIR, 'label_encoder.pkl'))
    scaler   = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))

    with open(os.path.join(MODELS_DIR, 'model_metadata.json')) as f:
        metadata = json.load(f)

    print(f"[OK] Model loaded   : {metadata['best_model']}")
    print(f"     Test Accuracy  : {metadata['test_accuracy']}%")
    print(f"     CV F1 Macro    : {metadata['cv_f1_macro']}%")

except Exception as e:
    print(f"[ERR] Model load failed: {e}")
    model = le = scaler = metadata = None


def prepare_input(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        'Station_Name':              'station_id',
        'Start_Date___Time':         'start_time',
        'End_Date___Time':           'end_time',
        'Total_Duration__hh_mm_ss_': 'total_duration',
        'Charging_Time__hh_mm_ss_':  'charging_time',
        'Energy__kWh_':              'energy_kwh',
        'Port_Type':                 'port_type',
        'GHG_Savings__kg_':          'ghg_savings',
        'ObjectID':                  'session_id',
    })

    df['start_time'] = pd.to_datetime(
        df['start_time'], format='mixed', dayfirst=False)
    df['end_time'] = pd.to_datetime(
        df['end_time'], format='mixed', dayfirst=False, errors='coerce')

    df = df.dropna(subset=['end_time'])

    df['total_duration_mins'] = pd.to_timedelta(
        df['total_duration']).dt.total_seconds() / 60
    df['charging_time_mins'] = pd.to_timedelta(
        df['charging_time']).dt.total_seconds() / 60

    df = df[df['total_duration_mins'] >= 0]
    df = df[df['charging_time_mins']  >= 0]
    df = df[df['energy_kwh']          >= 0]
    df = df[df['charging_time_mins']  <= df['total_duration_mins'] + 1]

    df = df.reset_index(drop=True)

    # fast=True skips the slow burst detection loop
    df = engineer_features(df, fast=True)
    return df


@app.get("/health")
def health():
    return {
        "status":       "ok",
        "model_loaded": model is not None,
        "model_name":   metadata['best_model'] if metadata else None,
        "accuracy":     metadata['test_accuracy'] if metadata else None,
    }


MAX_ROWS = 20_000


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        contents = await file.read()
        df_raw   = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

    if len(df_raw) > MAX_ROWS:
        raise HTTPException(
            status_code=400,
            detail=f"File has {len(df_raw):,} rows. Maximum allowed is {MAX_ROWS:,}. "
                   f"Please upload a sampled subset of your data."
        )

    try:
        df = prepare_input(df_raw.copy())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Feature engineering failed: {e}")

    FEATURES = get_feature_columns()
    missing  = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns after processing: {missing}"
        )

    X             = df[FEATURES].fillna(0)
    predictions   = model.predict(X)
    probabilities = model.predict_proba(X)
    pred_labels   = le.inverse_transform(predictions)
    confidence    = probabilities.max(axis=1)

    df['_pred']       = pred_labels
    df['_confidence'] = confidence
    anomaly_df = df[df['_pred'] != 'normal'].copy()

    anomalies = [
        {
            "session_id":          str(r.get('session_id', i)),
            "station_id":          str(r.get('station_id', '')),
            "anomaly_type":        r['_pred'],
            "confidence":          round(float(r['_confidence']), 4),
            "energy_kwh":          round(float(r.get('energy_kwh', 0)), 3),
            "total_duration_mins": round(float(r.get('total_duration_mins', 0)), 2),
            "charging_time_mins":  round(float(r.get('charging_time_mins', 0)), 2),
            "idle_ratio":          round(float(r.get('idle_ratio', 0)), 4),
            "energy_zscore":       round(float(r.get('energy_zscore', 0)), 4),
            "port_type":           str(r.get('port_type', '')),
            "start_time":          str(r.get('start_time', '')),
        }
        for i, r in anomaly_df.iterrows()
    ]

    save_anomalies_batch(anomalies)

    return PredictionResponse(
        filename        = file.filename,
        total_sessions  = len(df),
        anomalies_found = len(anomalies),
        anomaly_rate    = round(len(anomalies) / len(df) * 100, 2) if len(df) > 0 else 0,
        anomalies       = anomalies,
        model_used      = metadata['best_model'],
        accuracy        = metadata['test_accuracy'],
        f1_macro        = metadata['cv_f1_macro'],
    )


@app.get("/anomalies")
def get_anomalies(limit: int = 500):
    data = fetch_anomalies(limit)
    return {"total": len(data), "anomalies": data}


@app.get("/stats")
def get_stats():
    data = fetch_anomalies(1000)
    if not data:
        return {"total": 0, "by_type": {}}

    by_type = {}
    for record in data:
        t = record.get('anomaly_type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total":   len(data),
        "by_type": by_type,
    }


# Serve built frontend — must be last so API routes take priority
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")