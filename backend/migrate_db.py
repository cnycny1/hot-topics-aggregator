import sqlite3
import sys
from pathlib import Path

db_path = Path(__file__).parent / "hot_topics.db"

if not db_path.exists():
    print(f"Database not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add summary column if not exists
try:
    cursor.execute("ALTER TABLE hot_topics ADD COLUMN summary TEXT")
    print("Successfully added 'summary' column to hot_topics table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'summary' already exists")
    else:
        print(f"Error adding summary: {e}")

# Add is_deleted column if not exists
try:
    cursor.execute("ALTER TABLE hot_topics ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
    print("Successfully added 'is_deleted' column to hot_topics table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'is_deleted' already exists")
    else:
        print(f"Error adding is_deleted: {e}")

# Add deleted_at column if not exists
try:
    cursor.execute("ALTER TABLE hot_topics ADD COLUMN deleted_at DATETIME")
    print("Successfully added 'deleted_at' column to hot_topics table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'deleted_at' already exists")
    else:
        print(f"Error adding deleted_at: {e}")

# Add deleted_by column if not exists
try:
    cursor.execute("ALTER TABLE hot_topics ADD COLUMN deleted_by TEXT")
    print("Successfully added 'deleted_by' column to hot_topics table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'deleted_by' already exists")
    else:
        print(f"Error adding deleted_by: {e}")

# Create audit_logs table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            operator TEXT NOT NULL,
            operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            old_value TEXT,
            new_value TEXT
        )
    """)
    print("Successfully created 'audit_logs' table")
except sqlite3.OperationalError as e:
    print(f"Error creating audit_logs: {e}")

# Add indexes
try:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(operation_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hot_deleted ON hot_topics(is_deleted)")
    print("Successfully created indexes")
except sqlite3.OperationalError as e:
    print(f"Error creating indexes: {e}")

conn.commit()
conn.close()
print("Database migration completed!")