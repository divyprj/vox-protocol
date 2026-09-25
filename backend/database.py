"""
SQLite Database Layer for VOX//PROTOCOL
Persists generation history and telemetry records.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DB_DIR, "vox_protocol.db")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                voice_id TEXT NOT NULL,
                voice_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                language TEXT NOT NULL,
                filename TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                speed REAL NOT NULL,
                pitch INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_generations_created ON generations(created_at DESC)
        """)
    conn.close()


def save_generation(record: Dict[str, Any]):
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT INTO generations (
                id, text, voice_id, voice_name, gender, language,
                filename, duration_seconds, file_size_bytes, latency_ms,
                speed, pitch, created_at
            ) VALUES (
                :id, :text, :voice_id, :voice_name, :gender, :language,
                :filename, :duration_seconds, :file_size_bytes, :latency_ms,
                :speed, :pitch, :created_at
            )
        """, record)
    conn.close()


def get_all_generations(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM generations ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_generation_record(gen_id: str) -> Optional[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM generations WHERE id = ?", (gen_id,))
    row = cursor.fetchone()
    if row:
        filename = row["filename"]
        with conn:
            conn.execute("DELETE FROM generations WHERE id = ?", (gen_id,))
        conn.close()
        return filename
    conn.close()
    return None


def get_analytics_metrics() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(duration_seconds), 0.0) as total_duration,
            COALESCE(SUM(LENGTH(text)), 0) as total_chars,
            COALESCE(AVG(latency_ms), 0.0) as avg_latency
        FROM generations
    """)
    row = cursor.fetchone()
    conn.close()

    total_count = row["total_count"]
    total_dur = float(row["total_duration"])
    total_chars = int(row["total_chars"])
    avg_lat = float(row["avg_latency"])

    avg_rtf = (avg_lat / 1000.0) / (total_dur / total_count) if total_count > 0 and total_dur > 0 else 0.25
    speedup = 1.0 / avg_rtf if avg_rtf > 0 else 4.0

    return {
        "total_generations": total_count,
        "total_audio_seconds": round(total_dur, 2),
        "total_characters_processed": total_chars,
        "mean_latency_ms": round(avg_lat, 1),
        "mean_rtf": round(avg_rtf, 4),
        "realtime_speedup": round(speedup, 1),
    }
