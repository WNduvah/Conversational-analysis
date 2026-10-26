import sqlite3
from .config import DB_PATH, MAX_ROWS

def get_connection():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

def schema_text():
    return """Table: sales
Columns:
- sale_id INTEGER
- sale_date TEXT (YYYY-MM-DD)
- region TEXT
- product TEXT
- salesperson TEXT
- quantity INTEGER
- unit_price REAL
- revenue REAL
"""

def execute_read_only(sql):
    conn = get_connection()
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description or []]
        rows = cur.fetchmany(MAX_ROWS)
        return columns, [list(row) for row in rows]
    finally:
        conn.close()
