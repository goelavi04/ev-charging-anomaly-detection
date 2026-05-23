import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_anomalies_batch(anomalies: list):
    if not anomalies:
        return None
    try:
        chunk_size = 50
        for i in range(0, len(anomalies), chunk_size):
            chunk = anomalies[i:i + chunk_size]
            supabase.table("anomalies").insert(chunk).execute()
        print(f"[OK] Saved {len(anomalies)} anomalies to Supabase")
    except Exception as e:
        print(f"DB insert error: {e}")


def fetch_anomalies(limit: int = 500):
    try:
        response = (
            supabase.table("anomalies")
            .select("*")
            .order("detected_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"DB fetch error: {e}")
        return []