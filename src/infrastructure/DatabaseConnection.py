import os
import sqlite3
import sys
from contextlib import contextmanager
from typing import Optional


class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _persistentConnection: Optional[sqlite3.Connection] = None

    def __new__(cls, db_path: str = ":File:"):
        if db_path == ":memory:":
            return super(DatabaseConnection, cls).__new__(cls)

        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = ":File:"):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True

        if db_path == ":memory:":
            self._dbPath = db_path
            self._persistentConnection = sqlite3.connect(":memory:")
            self._persistentConnection.row_factory = sqlite3.Row
            self._initializeDatabase()
        else:
            self._dbPath = DatabaseConnection.get_db_path()
            self._initializeDatabase()

    def _initializeDatabase(self) -> None:
        with self.getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_results (
                    id TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    feature_vector TEXT NOT NULL,
                    is_malignant INTEGER NOT NULL,
                    time_stamp TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    @contextmanager
    def getConnection(self):
        if self._dbPath == ":memory:":
            yield self._persistentConnection
        else:
            conn = sqlite3.connect(self._dbPath)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    @staticmethod
    def enableForeignKeys(conn: sqlite3.Connection) -> None:
        conn.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        if self._persistentConnection:
            self._persistentConnection.close()
            self._persistentConnection = None

    def reset(self) -> None:
        """
        Reset the database (useful for testing).

        WARNING: This will delete all data!
        """
        if self._dbPath == ":memory:":
            if self._persistentConnection:
                self._persistentConnection.close()
            self._persistentConnection = sqlite3.connect(":memory:")
            self._persistentConnection.row_factory = sqlite3.Row
            self._initializeDatabase()
        else:
            if os.path.exists(self._dbPath):
                os.remove(self._dbPath)
            self._initializeDatabase()

    @staticmethod
    def get_db_path() -> str:
        """
        Returns a writable path for prediction.db regardless of platform
        or whether the app is running bundled or from source.

        Windows : C:/Users/<name>/AppData/Local/CardioAI/prediction.db
        macOS   : ~/Library/Application Support/CardioAI/prediction.db
        Linux   : ~/.local/share/CardioAI/prediction.db
        """
        app_name = "CardioAI"

        if sys.platform == "win32":
            base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        elif sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support")
        else:
            base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

        db_dir = os.path.join(base, app_name)
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "prediction_results.db")
