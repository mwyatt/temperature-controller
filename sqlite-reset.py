import sqlite3
import os

con = sqlite3.connect(os.getenv('DB_NAME'))
cur = con.cursor()

# drop all tables
# cur.execute("DROP TABLE IF EXISTS settings")
cur.execute("DROP TABLE IF EXISTS temp_history")

con.commit()