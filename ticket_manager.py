from typing import Optional
"""
UniDesk AI — Ticket Manager
=============================
SQLite-backed ticket store for managing triaged IT support tickets.
Provides CRUD operations and aggregate statistics.
"""

import sqlite3
import os
from datetime import datetime, timezone
from config import CATEGORIES, URGENCY_LEVELS

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/triage.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "triage.db")

class TicketManager:
    """Manages IT support tickets in SQLite."""

    def __init__(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _get_conn(self):
        # check_same_thread=False allows FastAPI threads to share connection
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_number TEXT UNIQUE,
                    category TEXT,
                    category_name TEXT,
                    category_icon TEXT,
                    assigned_team TEXT,
                    urgency TEXT,
                    urgency_name TEXT,
                    urgency_color TEXT,
                    sla TEXT,
                    summary TEXT,
                    status TEXT,
                    escalated BOOLEAN,
                    escalation_reason TEXT,
                    session_id TEXT,
                    user_id TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

    def _dict_from_row(self, row) -> dict:
        d = dict(row)
        # Rename ticket_number to id for frontend compatibility
        d["id"] = d.pop("ticket_number")
        # Convert escalated to bool
        d["escalated"] = bool(d["escalated"])
        return d

    def create_ticket(
        self,
        category: str,
        urgency: str,
        summary: str,
        session_id: str,
        escalated: bool = False,
        escalation_reason: Optional[str] = None,
        user_id: Optional[str] = None,
        is_resolved: bool = False,
    ) -> dict:
        cat_info = CATEGORIES.get(category, CATEGORIES["other"])
        urg_info = URGENCY_LEVELS.get(urgency, URGENCY_LEVELS["P3"])
        
        now = datetime.now(timezone.utc).isoformat()
        
        if is_resolved:
            status = "resolved"
        elif escalated:
            status = "escalated"
        else:
            status = "open"

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tickets (
                    category, category_name, category_icon, assigned_team,
                    urgency, urgency_name, urgency_color, sla,
                    summary, status, escalated, escalation_reason,
                    session_id, user_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category, cat_info["name"], cat_info["icon"], cat_info["team"],
                urgency, urg_info["name"], urg_info["color"], urg_info["sla"],
                summary, status, escalated, escalation_reason,
                session_id, user_id, now, now
            ))
            row_id = cursor.lastrowid
            # Format ticket number UNID-0001
            ticket_number = f"UNID-{row_id:04d}"
            cursor.execute("UPDATE tickets SET ticket_number = ? WHERE id = ?", (ticket_number, row_id))
            
            cursor.execute("SELECT * FROM tickets WHERE id = ?", (row_id,))
            return self._dict_from_row(cursor.fetchone())

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_id,))
            row = cursor.fetchone()
            return self._dict_from_row(row) if row else None

    def get_tickets(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        urgency: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if category:
            query += " AND category = ?"
            params.append(category)
        if urgency:
            query += " AND urgency = ?"
            params.append(urgency)
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._dict_from_row(row) for row in cursor.fetchall()]

    def update_status(self, ticket_id: str, new_status: str) -> Optional[dict]:
        now = datetime.now(timezone.utc).isoformat()
        escalated_clause = "escalated = 1," if new_status == "escalated" else ""
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE tickets 
                SET status = ?, {escalated_clause} updated_at = ?
                WHERE ticket_number = ?
            """, (new_status, now, ticket_id))
            
            if cursor.rowcount == 0:
                return None
                
            cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_id,))
            return self._dict_from_row(cursor.fetchone())

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tickets")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            for st in ["open", "in_progress", "resolved", "escalated"]:
                if st not in status_counts:
                    status_counts[st] = 0

            cursor.execute("SELECT urgency, COUNT(*) FROM tickets GROUP BY urgency")
            urgency_counts = {row[0]: row[1] for row in cursor.fetchall()}
            for u in ["P1", "P2", "P3", "P4"]:
                if u not in urgency_counts:
                    urgency_counts[u] = 0

            cursor.execute("SELECT category, COUNT(*) FROM tickets GROUP BY category")
            cat_db = {row[0]: row[1] for row in cursor.fetchall()}
            
            category_counts = {}
            for cat_key in CATEGORIES:
                if cat_key in cat_db and cat_db[cat_key] > 0:
                    category_counts[cat_key] = {
                        "count": cat_db[cat_key],
                        "name": CATEGORIES[cat_key]["name"],
                        "icon": CATEGORIES[cat_key]["icon"],
                    }

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE escalated = 1")
            escalated_count = cursor.fetchone()[0]
            escalation_rate = round(escalated_count / total * 100, 1) if total > 0 else 0

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'")
            auto_resolved = cursor.fetchone()[0]

            return {
                "total": total,
                "status": status_counts,
                "urgency": urgency_counts,
                "categories": category_counts,
                "escalation_rate": escalation_rate,
                "auto_resolved": auto_resolved,
            }
