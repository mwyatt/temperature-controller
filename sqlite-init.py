import os
import sqlite3

con = sqlite3.connect(os.getenv('DB_NAME'))
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """
)
cur.execute(
    """
    INSERT OR IGNORE INTO settings (key, value) VALUES ('target_temp', '10')
    """
)
cur.execute(
    """
    INSERT OR IGNORE INTO settings (key, value) VALUES ('heater_on_override', '')
    """
)
cur.execute(
    """
    INSERT OR IGNORE INTO settings (key, value) VALUES ('current_temp', '0')
    """
)
cur.execute(
    """
    INSERT OR IGNORE INTO settings (key, value) VALUES ('buffer_temp', '0')
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS temp_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_temp REAL,
        heater_on INTEGER,
        timestamp INTEGER
    )
    """
)

con.commit()