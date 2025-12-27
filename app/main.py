from datetime import datetime
import os

from fastapi import FastAPI
from psycopg2 import connect

app = FastAPI()

def _get_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return connect(db_url)

def _record_visit() -> list[datetime]:
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
            """
                CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY,
                visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
            )
            conn.commit()
            cur.execute("INSERT INTO visits (visited_at) VALUES (NOW())")

            cur.execute(
                "SELECT visited_at FROM visits ORDER BY visited_at DESC LIMIT 20"
            )
            return [row[0] for row in cur.fetchall()]

@app.get("/")
def read_root():
    try:
        recent_visits = _record_visit()
    except Exception as exc:  # pragma: no cover - errors are surfaced in response
        return {"status": "error", "detail": str(exc)}

    return {
        "status": "Cloud Environment Ready (Handled by CI/CD Take 2)",
        "recent_visits": [timestamp.isoformat() for timestamp in recent_visits],
        "database_url": os.getenv("DATABASE_URL"),
    }

@app.get("/database_url")
def connect_database():
    return {"database_url": os.getenv("DATABASE_URL")}

