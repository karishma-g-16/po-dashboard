import logging
from sqlalchemy import text
from backend.database.db import engine

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Programmatic migration to add missing columns without Alembic.
    Uses the central engine from backend.database.db.
    """
    logger.info("Starting database migrations...")
    try:
        with engine.begin() as conn:
            # Migration for users table
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_code VARCHAR(10);"))
                logger.info("Successfully checked/added reset_code column to users table.")
            except Exception as e:
                logger.error(f"Error adding reset_code: {e}")

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_code_expires TIMESTAMP WITH TIME ZONE;"))
                logger.info("Successfully checked/added reset_code_expires column to users table.")
            except Exception as e:
                logger.error(f"Error adding reset_code_expires: {e}")

            # Existing migration for purchase_orders
            try:
                conn.execute(text("ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS ordered_quantity INTEGER DEFAULT 0;"))
                logger.info("Successfully checked/added ordered_quantity column.")
            except Exception as e:
                logger.error(f"Error adding ordered_quantity: {e}")
                
        logger.info("Database migrations finished.")
    except Exception as overall_e:
        logger.error(f"Migration process failed: {overall_e}")

if __name__ == "__main__":
    # Setup basic logging if run directly
    logging.basicConfig(level=logging.INFO)
    run_migrations()
