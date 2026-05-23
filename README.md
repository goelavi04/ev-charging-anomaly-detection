# EV Charging Anomaly Detection

A full-stack machine learning application that detects anomalous behaviour in EV charging sessions — including fraud, DoS attacks, energy spikes, and idle abuse — using a trained Decision Tree classifier served via a FastAPI backend and a React dashboard.

**Live Demo:** https://ev-anomaly-backend.onrender.com

---

## Dashboard Preview

> Upload any CSV from the `ml/dataset/` folder to see the dashboard in action.

![EV Anomaly Detection Dashboard](https://ev-anomaly-backend.onrender.com)

The dashboard shows real-time anomaly detection results including:
- Total dataset entries, anomaly counts by category, critical alerts and warnings
- Interactive anomaly table with session-level detail
- Pie and bar charts broken down by anomaly type
- Per-session alert panel with confidence scores and timestamps
- Historical logs viewer connected to Supabase

---

## Features

- **CSV Upload** — Upload any EV charging session CSV; get instant anomaly predictions
- **5 Anomaly Types** — Ghost sessions, DoS attacks, energy spikes, burst patterns, idle abuse
- **Real-time Dashboard** — Stats cards, filterable tables, interactive charts, alert panels
- **Historical Logs** — All detected anomalies stored in Supabase and retrievable via the Logs viewer
- **Single URL Deployment** — React SPA served directly by FastAPI; no separate frontend host needed
- **20,000-row cap** with a clear error message for oversized uploads

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts, Axios |
| Backend | Python 3.12, FastAPI, Uvicorn, Pandas, NumPy, scikit-learn, Joblib |
| ML | Decision Tree Classifier (scikit-learn), custom feature engineering |
| Database | Supabase (PostgreSQL) |
| Deployment | Render (Python web service, single URL) |
| Version Control | GitHub |

---

## Project Structure

```
ev-detection-project/
├── backend/
│   ├── main.py              # FastAPI app — predict, health, anomalies, stats endpoints
│   ├── models.py            # Pydantic response models
│   ├── database.py          # Supabase insert / fetch helpers
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EVDashboard.tsx      # Root dashboard layout & state
│   │   │   ├── StatsCards.tsx       # 4-card top row + 4-card anomaly row
│   │   │   ├── FileUpload.tsx       # CSV upload with drag-and-drop
│   │   │   ├── AnomalyTable.tsx     # Filterable session table
│   │   │   ├── AnomalyCharts.tsx    # Pie + bar charts (Recharts)
│   │   │   ├── AlertPanel.tsx       # Per-session detail panel
│   │   │   ├── LogsViewer.tsx       # Historical Supabase log viewer
│   │   │   └── ui/                  # shadcn/ui primitives
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios API calls (predict, anomalies, stats, health)
│   │   │   └── transformers.ts      # Backend → UI type mapping
│   │   └── types/index.ts           # TypeScript interfaces
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── ml/
│   ├── train.py                     # Model training script
│   ├── label_engineering.py         # Feature engineering + anomaly labelling
│   ├── eda.py                       # Exploratory data analysis
│   ├── models/
│   │   ├── best_model.pkl           # Trained Decision Tree
│   │   ├── label_encoder.pkl        # Class label encoder
│   │   ├── scaler.pkl               # Feature scaler
│   │   └── model_metadata.json      # Accuracy, F1, feature list
│   └── dataset/
│       ├── ev_charging_data.csv     # Full dataset (148,136 rows) — gitignored
│       ├── ev_data_2018.csv
│       ├── ev_data_2019.csv
│       ├── ev_data_2020.csv
│       ├── ev_data_2021.csv
│       ├── ev_data_2022_h1.csv
│       ├── ev_data_2022_h2.csv
│       ├── ev_data_2023_h1.csv
│       ├── ev_data_2023_h2.csv
│       └── test_sample.csv
│
├── Dockerfile                       # Multi-stage: Node (frontend build) → Python
├── render.yaml                      # Render deploy config
└── .gitignore
```

---

## Machine Learning Model

### Dataset

**Source:** [City of Boulder — EV Charging Station Sessions](https://open-data.bouldercolorado.gov/datasets/95992b3938be4622b07f0b05eba95d4c_0/explore)

Real-world public EV charging session data from the City of Boulder, Colorado. Covers **January 2018 – November 2023** across **50 charging stations**, totalling **148,136 sessions**.

### Anomaly Types

| Anomaly | Label | Detection Rule |
|---------|-------|----------------|
| Ghost Session | `ghost_session` | `energy_kwh == 0` — plugged in but no energy drawn |
| Energy Spike | `energy_spike` | `energy_zscore > 3.0` AND `energy_vs_median > 4.0` |
| DoS Attack | `dos_attack` | `duration < 5 min` AND `energy < 0.5 kWh` |
| Burst Pattern | `burst_pattern` | `8+ sessions` at same station within 30 minutes |
| Idle Abuse | `idle_abuse` | `idle_ratio > 0.92` AND `duration > 120 min` AND `energy > 2 kWh` |

> Labels are synthetically generated from domain rules applied to real session data, with a random flip rate (8–12%) to simulate real-world noise.

### Feature Engineering

23 features are engineered from raw session data:

| Category | Features |
|----------|----------|
| Energy | `energy_kwh`, `energy_per_min`, `energy_zscore`, `energy_vs_median`, `ghg_savings` |
| Duration | `total_duration_mins`, `charging_time_mins`, `idle_mins`, `duration_zscore` |
| Ratios | `idle_ratio`, `charge_efficiency` |
| Station Stats | `station_mean_energy`, `station_std_energy`, `station_median_energy`, `station_session_count`, `station_mean_dur` |
| Temporal | `hour`, `day_of_week`, `month`, `is_weekend`, `is_night` |
| Burst | `sessions_last_30min` |
| Port | `port_type_num` |

### Model Performance

Two classifiers were trained and evaluated:

| Model | Accuracy | F1 Macro (Test) | CV F1 Macro | CV Std |
|-------|----------|-----------------|-------------|--------|
| **Decision Tree** ✓ | 65.92% | 80.91% | **79.71%** | ±1.14% |
| Random Forest | 66.47% | 78.80% | 77.05% | ±1.38% |

The **Decision Tree** was selected as the best model based on its higher macro F1 score and lower cross-validation variance, indicating better generalisation across all anomaly classes including minority classes.

---

## Sample Datasets

The full 148K-row dataset is split into yearly/half-yearly files, each under the 20,000-row upload limit:

| File | Period | Rows | Size |
|------|--------|------|------|
| `ev_data_2018.csv` | Full year 2018 | 13,710 | 2.2 MB |
| `ev_data_2019.csv` | Full year 2019 | 18,000 | 2.8 MB |
| `ev_data_2020.csv` | Full year 2020 | 10,200 | 1.6 MB |
| `ev_data_2021.csv` | Full year 2021 | 18,000 | 2.8 MB |
| `ev_data_2022_h1.csv` | Jan–Jun 2022 | 16,224 | 2.6 MB |
| `ev_data_2022_h2.csv` | Jul–Dec 2022 | 18,000 | 2.8 MB |
| `ev_data_2023_h1.csv` | Jan–Jun 2023 | 18,000 | 2.8 MB |
| `ev_data_2023_h2.csv` | Jul–Nov 2023 | 18,000 | 2.8 MB |
| `test_sample.csv` | Mixed sample | 500 | 78 KB |

All files are located in `ml/dataset/` and can be uploaded directly to the live dashboard.

---

## API Reference

Base URL: `https://ev-anomaly-backend.onrender.com`

### `POST /predict`
Upload a CSV file for anomaly detection.

**Request:** `multipart/form-data` with field `file` (`.csv` only, max 20,000 rows)

**Response:**
```json
{
  "filename": "ev_data_2022_h1.csv",
  "total_sessions": 16222,
  "anomalies_found": 2162,
  "anomaly_rate": 13.33,
  "model_used": "Decision Tree",
  "accuracy": 65.92,
  "f1_macro": 79.71,
  "anomalies": [
    {
      "session_id": "33698",
      "station_id": "COMM VITALITY / 1000WALNUT1",
      "anomaly_type": "ghost_session",
      "confidence": 0.9107,
      "energy_kwh": 0.0,
      "total_duration_mins": 1.98,
      "charging_time_mins": 0.0,
      "idle_ratio": 0.9995,
      "energy_zscore": -1.0154,
      "port_type": "Level 2",
      "start_time": "2022-01-01 15:17:00"
    }
  ]
}
```

### `GET /health`
Returns model load status and accuracy.
```json
{ "status": "ok", "model_loaded": true, "model_name": "Decision Tree", "accuracy": 65.92 }
```

### `GET /anomalies?limit=500`
Fetches previously detected anomalies from Supabase.

### `GET /stats`
Returns total anomaly count grouped by type.

---

## Running Locally

### Prerequisites
- Python 3.12+
- Node.js 20+
- A Supabase project with an `anomalies` table

### Backend
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# Start the server
uvicorn backend.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install

# For local development pointing to local backend
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Open `http://localhost:5173` in your browser.

### Docker (full stack)
```bash
docker build -t ev-anomaly .
docker run -p 10000:10000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  ev-anomaly
```

---

## Deployment

The app is deployed as a **single service on Render** using a Python runtime.

**Build command:**
```
pip install -r backend/requirements.txt && npm --prefix frontend ci && npm --prefix frontend run build
```

**Start command:**
```
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

The React build output (`frontend/dist/`) is served as static files by FastAPI using `StaticFiles(html=True)` mounted at `/`, ensuring the SPA works with client-side routing while all `/predict`, `/health`, `/anomalies`, and `/stats` API routes take priority.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon/public key |

---

## Supabase Schema

```sql
create table anomalies (
  id            bigserial primary key,
  session_id    text,
  station_id    text,
  anomaly_type  text,
  confidence    float,
  energy_kwh    float,
  total_duration_mins float,
  charging_time_mins  float,
  idle_ratio    float,
  energy_zscore float,
  port_type     text,
  start_time    text,
  detected_at   timestamptz default now()
);
```

---

## Repository

**GitHub:** https://github.com/goelavi04/ev-charging-anomaly-detection

---

## Data Source

City of Boulder Open Data Portal — EV Charging Station Sessions
https://open-data.bouldercolorado.gov/datasets/95992b3938be4622b07f0b05eba95d4c_0/explore

Data is publicly available under the City of Boulder's open data licence.
