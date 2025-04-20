import logging
import psycopg2
from db.config import connection
from datetime import datetime
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Logging configuration (shared)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/db_operations.log"),
        logging.StreamHandler()
    ]
)

# Auto-generate Product Code
def generate_product_code():
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM product;")
                count = cur.fetchone()[0] + 1
                code = f"PRD-{str(count).zfill(5)}"
                logging.info(f"Generated product code: {code}")
                return code
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in generate_product_code: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in generate_product_code: {e}")

# Insert Product
def insert_product(name, category, unit = "pcs", price = 0.0, description = "", threshold = 3):
    code = generate_product_code()
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO product (name, code, category, unit, price, description, threshold)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (name, code, category, unit, price, description, threshold))
                product_id = cur.fetchone()[0]
                logging.info(f"Inserted product '{name}' with ID {product_id} and code {code}")
                return product_id, code
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in insert_product: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in insert_product: {e}")

# Fetch All Products
def fetch_all_products():
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM product ORDER BY name;")
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} products.")
                return rows
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in fetch_all_products: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_all_products: {e}")

# Insert Stock Movement
def insert_stock_movement(product_id, type_, label, reason, service, quantity):
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO stock_movement 
                    (product_id, type, label, reason, service, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (product_id, type_, label, reason, service, quantity))
                movement_id = cur.fetchone()[0]
                logging.info(f"Inserted stock movement ID {movement_id} for product {product_id} ({type_}, {label})")
                return movement_id
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in insert_stock_movement: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in insert_stock_movement: {e}")

# Fetch Stock Movements
def fetch_stock_movements(product_id=None):
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                if product_id:
                    cur.execute("SELECT * FROM stock_movement WHERE product_id = %s ORDER BY timestamp DESC;", (product_id,))
                else:
                    cur.execute("SELECT * FROM stock_movement ORDER BY timestamp DESC;")
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} stock movements{' for product ' + str(product_id) if product_id else ''}.")
                return rows
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in fetch_stock_movements: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_stock_movements: {e}")

def fetch_all_products_with_stock():
    try:
        conn = connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.code,
                    p.category,
                    p.unit,
                    p.price,
                    p.threshold,
                    COALESCE(SUM(CASE WHEN sm.type = 'IN' THEN sm.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN sm.type = 'OUT' THEN sm.quantity ELSE 0 END), 0) AS stock,
                    p.created_at,
                    p.description
                FROM product p
                LEFT JOIN stock_movement sm ON p.id = sm.product_id
                GROUP BY p.id
                ORDER BY p.name;
            """)
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error fetching products with stock: {e}")
        return []

def update_product_by_id(product_id, name, code, category, unit, price, description, threshold):
    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE product
                SET name = %s,
                    code = %s,
                    category = %s,
                    unit = %s,
                    price = %s,
                    description = %s,
                    threshold = %s
                WHERE id = %s
            """, (name, code, category, unit, price, description, threshold, product_id))
