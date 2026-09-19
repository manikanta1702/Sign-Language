import os
import sqlite3

os.makedirs("backend", exist_ok=True)

DB_PATH = os.path.join("backend", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        predicted_sign TEXT,
        confidence REAL,
        model_version TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)

conn.commit()
conn.close()

print(f"Created or verified {DB_PATH} with 'logs' table")
