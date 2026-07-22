"""
Accès aux données de vidéosurveillance — conforme au schéma SILEDJE.
Couvre : cameras, camera_events, alerts.
Schéma prêt ; aucune UI ne l'utilise encore (module IA non branché).
"""

from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SurveillanceRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ip_address TEXT NOT NULL UNIQUE,
                rtsp_url TEXT NOT NULL,
                http_url TEXT,
                location TEXT,
                resolution TEXT,
                status TEXT DEFAULT 'online',
                recording_mode TEXT DEFAULT 'motion',
                retention_days INTEGER DEFAULT 7,
                is_ai_enabled INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'low',
                ai_confidence REAL,
                description TEXT,
                video_path TEXT,
                thumbnail_path TEXT,
                sale_id INTEGER REFERENCES sales(id) ON DELETE SET NULL,
                is_reviewed INTEGER DEFAULT 0,
                review_notes TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_camera_events_detected "
                       "ON camera_events(detected_at)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
                camera_event_id INTEGER REFERENCES camera_events(id) ON DELETE SET NULL,
                is_read INTEGER DEFAULT 0,
                is_resolved INTEGER DEFAULT 0,
                resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at)")

        self.db.commit()

    # ── CAMERAS ──────────────────────────────────────────────────────

    def get_all_cameras(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM cameras ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def create_camera(self, name: str, ip_address: str, rtsp_url: str, **fields) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO cameras (name, ip_address, rtsp_url, http_url, location,
                                  resolution, recording_mode, retention_days, is_ai_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, ip_address, rtsp_url, fields.get("http_url"), fields.get("location"),
              fields.get("resolution"), fields.get("recording_mode", "motion"),
              fields.get("retention_days", 7), 1 if fields.get("is_ai_enabled", True) else 0))
        self.db.commit()
        return cursor.lastrowid

    # ── ALERTS ───────────────────────────────────────────────────────

    def create_alert(self, alert_type: str, title: str, message: str,
                      severity: str = "medium", product_id: int = None,
                      camera_event_id: int = None) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO alerts (alert_type, severity, title, message, product_id, camera_event_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (alert_type, severity, title, message, product_id, camera_event_id))
        self.db.commit()
        return cursor.lastrowid

    def get_unresolved_alerts(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT * FROM alerts WHERE is_resolved = 0 ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def resolve_alert(self, alert_id: int, user_id: int):
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE alerts SET is_resolved = 1, resolved_by = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user_id, alert_id))
        self.db.commit()