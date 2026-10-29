import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # PredictionHistory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PredictionHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitted_url TEXT NOT NULL,
        normalized_domain TEXT NOT NULL,
        prediction TEXT NOT NULL,
        model_score REAL NOT NULL,
        analysis_mode TEXT NOT NULL,
        fetch_status TEXT NOT NULL,
        model_version TEXT NOT NULL,
        feature_schema_version TEXT NOT NULL,
        explanation_json TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # DatasetMetadata
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DatasetMetadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        source TEXT NOT NULL,
        dataset_fingerprint TEXT NOT NULL,
        retrieval_date TEXT NOT NULL,
        sample_count INTEGER NOT NULL,
        label_distribution TEXT NOT NULL,
        license_notes TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # ModelMetadata
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ModelMetadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_version TEXT NOT NULL UNIQUE,
        algorithm TEXT NOT NULL,
        training_dataset_fingerprint TEXT NOT NULL,
        feature_schema_version TEXT NOT NULL,
        training_date TEXT NOT NULL,
        evaluation_summary TEXT NOT NULL,
        artifact_location TEXT NOT NULL
    );
    """)

    # TrainingJob
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TrainingJob (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT NOT NULL,
        progress INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        error_summary TEXT
    );
    """)

    # AuditLog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AuditLog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        resource TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

