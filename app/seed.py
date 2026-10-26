import sqlite3
import random
from datetime import date, timedelta
from .config import DB_PATH

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headset"]
PEOPLE = ["Ama", "Kofi", "Yaw", "Esi", "Kojo", "Abena"]
PRICES = {"Laptop": 1200, "Monitor": 300, "Keyboard": 80, "Mouse": 40, "Headset": 120}

def seed():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS sales")
    cur.execute("""
        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY,
            sale_date TEXT NOT NULL,
            region TEXT NOT NULL,
            product TEXT NOT NULL,
            salesperson TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            revenue REAL NOT NULL
        )
    """)

    random.seed(42)
    start = date(2026, 1, 1)
    rows = []

    for sale_id in range(1, 1001):
        sale_date = start + timedelta(days=random.randint(0, 273))
        product = random.choice(PRODUCTS)
        quantity = random.randint(1, 8)
        unit_price = round(PRICES[product] * random.uniform(0.9, 1.1), 2)
        revenue = round(quantity * unit_price, 2)

        rows.append((
            sale_id,
            sale_date.isoformat(),
            random.choice(REGIONS),
            product,
            random.choice(PEOPLE),
            quantity,
            unit_price,
            revenue,
        ))

    cur.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()
    print(f"Seeded {len(rows)} sales rows into {DB_PATH}")

if __name__ == "__main__":
    seed()
