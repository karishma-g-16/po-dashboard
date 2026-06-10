import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Assuming db.py uses SQLALCHEMY_DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/podashboard")
engine = create_engine(DATABASE_URL)

def run_migrations():
    """
    Programmatic migration to add missing columns without Alembic.
    """
    with engine.begin() as conn:
        # Migration for users table
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_code VARCHAR(10);"))
            print("Successfully added reset_code column to users table.")
        except Exception as e:
            print("reset_code column might already exist.")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_code_expires TIMESTAMP WITH TIME ZONE;"))
            print("Successfully added reset_code_expires column to users table.")
        except Exception as e:
            print("reset_code_expires column might already exist.")

        # Existing migration for purchase_orders
        try:
            conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN ordered_quantity INTEGER DEFAULT 0;"))
            print("Successfully added ordered_quantity column.")
        except Exception as e:
            print("ordered_quantity column might already exist.")

if __name__ == "__main__":
    run_migrations()
