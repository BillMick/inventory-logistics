import logging
from db.config import connection
import psycopg2
import os
from utils.auth import hash_password

# Ensure the logs/ directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/db_setup.log"),     # Write to file
        logging.StreamHandler()                       # Still show in console too
    ]
)

def create_tables():
    default_password = "admin123"
    password_hashed = hash_password(default_password)
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS supplier (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            fiscal_id TEXT UNIQUE NOT NULL,
            contact TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS product (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'pcs',
            price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
            description TEXT,
            threshold INTEGER DEFAULT 3,
            supplier_id INTEGER NULL REFERENCES supplier(id) ON DELETE SET NULL,
            is_archived BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS stock_movement (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES product(id),
            type VARCHAR(10) CHECK (type IN ('IN', 'OUT')) NOT NULL,
            label TEXT NOT NULL,
            recipient TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            comment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        f"""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES ('admin', 'admin@gmail.com', '{password_hashed}', TRUE)
        ON CONFLICT (username) DO NOTHING;
        """
    ]

    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                for q in queries:
                    cur.execute(q)
                    logging.info("Executed query successfully.")
        logging.info("All tables created or verified successfully.")
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error occurred: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
