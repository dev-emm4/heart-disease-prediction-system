import os
import sqlite3
import sys

import pytest

from src.infrastructure import DatabaseConnection

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestDatabaseConnection:
    """Tests for DatabaseConnection."""

    def test_singletonBehavior(self):
        """Test that DatabaseConnection creates separate instances for in-memory DBs (test isolation)."""
        db1 = DatabaseConnection(db_path=":memory:")
        db2 = DatabaseConnection(db_path=":memory:")

        # In-memory databases should NOT be singletons (for test isolation)
        assert db1 is not db2

        # But file-based databases should be singletons
        db3 = DatabaseConnection(db_path="../../../test.db")
        db4 = DatabaseConnection(db_path="../../../test.db")
        assert db3 is db4

    def test_getConnection_returnConnectionContextmanager(self):
        """Test that get_connection works as a context manager."""
        db = DatabaseConnection(db_path=":memory:")

        with db.getConnection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
