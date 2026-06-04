import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Assuming db.py uses SQLALCHEMY_DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/podashboard")
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN ordered_quantity INTEGER DEFAULT 0;"))
        print("Successfully added ordered_quantity column.")
    except Exception as e:
        print("Column might already exist or error occurred:", str(e))
