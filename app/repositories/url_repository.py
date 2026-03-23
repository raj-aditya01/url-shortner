from __future__ import annotations

import sqlite3
from threading import Lock
from typing import Dict, Optional, Protocol


class UrlRepository(Protocol):
    """Interface that defines all database operations needed for URLs.
    
    Any class implementing these methods can be used as the storage layer.
    """

    def save_and_get_id(self, original_url: str) -> int:
        ...

    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        ...

    def get_original_url(self, short_hash: str) -> Optional[str]:
        ...

    def increment_click_count(self, short_hash: str) -> None:
        ...

    def get_all(self) -> Dict[str, dict]:
        ...


class MockUrlRepository:
    """In-memory storage implementation for testing.
    
    Stores URLs in a dictionary instead of a database.
    Uses locks to safely handle multiple requests at the same time.
    """

    def __init__(self) -> None:
        self.db: Dict[str, dict] = {}
        self._auto_increment_id = 1_000_000
        self._lock = Lock()  # Prevents data corruption in concurrent requests

    def save_and_get_id(self, original_url: str) -> int:
        """Save URL and return its auto-incremented ID."""
        with self._lock:
            self._auto_increment_id += 1
            return self._auto_increment_id

    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        """Store the short hash for a URL ID."""
        with self._lock:
            self.db[short_hash] = {
                "url_id": url_id,
                "original_url": original_url,
                "click_count": 0,
            }

    def get_original_url(self, short_hash: str) -> Optional[str]:
        """Retrieve the original URL for a short hash."""
        record = self.db.get(short_hash)
        return record["original_url"] if record else None

    def increment_click_count(self, short_hash: str) -> None:
        """Increase click counter for a short hash."""
        with self._lock:
            if short_hash in self.db:
                self.db[short_hash]["click_count"] += 1

    def get_all(self) -> Dict[str, dict]:
        """Return all stored URLs."""
        return self.db


class SQLiteUrlRepository:
    """Database storage using SQLite for persistent data.
    
    All data is saved to a SQLite database file.
    Uses locks to handle multiple requests safely.
    """

    def __init__(self, db_path: str) -> None:
        self._lock = Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS url_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_hash TEXT UNIQUE,
                    click_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def save_and_get_id(self, original_url: str) -> int:
        with self._lock:
            with self._conn:
                cursor = self._conn.execute(
                    "INSERT INTO url_mappings (original_url) VALUES (?)",
                    (original_url,),
                )
                return int(cursor.lastrowid)

    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    UPDATE url_mappings
                    SET short_hash = ?, original_url = ?
                    WHERE id = ?
                    """,
                    (short_hash, original_url, url_id),
                )

    def get_original_url(self, short_hash: str) -> Optional[str]:
        row = self._conn.execute(
            "SELECT original_url FROM url_mappings WHERE short_hash = ?",
            (short_hash,),
        ).fetchone()
        return str(row["original_url"]) if row else None

    def increment_click_count(self, short_hash: str) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    UPDATE url_mappings
                    SET click_count = click_count + 1
                    WHERE short_hash = ?
                    """,
                    (short_hash,),
                )

    def get_all(self) -> Dict[str, dict]:
        rows = self._conn.execute(
            """
            SELECT id, short_hash, original_url, click_count
            FROM url_mappings
            WHERE short_hash IS NOT NULL
            """
        ).fetchall()
        return {
            str(row["short_hash"]): {
                "url_id": int(row["id"]),
                "original_url": str(row["original_url"]),
                "click_count": int(row["click_count"]),
            }
            for row in rows
        }