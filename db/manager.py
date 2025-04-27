import logging
import psycopg2
from db.config import connection
import os
import psycopg2.extras
from psycopg2.extras import DictCursor


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
def insert_product(name, category, supplier_id, unit = "pcs", price = 0.0, description = "", threshold = 3):
    code = generate_product_code()
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO product (name, code, category, unit, price, description, threshold, supplier_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (name, code, category, unit, price, description, threshold, supplier_id))
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
def insert_stock_movement(product_id, type_, label, comment, recipient, quantity):
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO stock_movement 
                    (product_id, type, label, comment, recipient, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (product_id, type_, label, comment, recipient, quantity))
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
                    s.name AS supplier_name,
                    p.threshold,
                    COALESCE(SUM(CASE WHEN sm.type = 'IN' THEN sm.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN sm.type = 'OUT' THEN sm.quantity ELSE 0 END), 0) AS stock,
                    p.created_at,
                    p.description,
                    p.is_archived
                FROM product p
                LEFT JOIN supplier s ON p.supplier_id = s.id
                LEFT JOIN stock_movement sm ON p.id = sm.product_id
                GROUP BY p.id, s.name
                ORDER BY p.name;
            """)
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error fetching products with stock: {e}")
        return []

def get_theoretical_stock(product_id):
    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN sm.type = 'IN' THEN sm.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN sm.type = 'OUT' THEN sm.quantity ELSE 0 END), 0) AS stock
                FROM product p
                LEFT JOIN stock_movement sm ON p.id = sm.product_id
                WHERE p.id = %s
            """, (product_id,))
            result = cur.fetchone()
            return result[0] if result else 0
            
            
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
            
def update_supplier_by_id(supplier_id, name, fiscal_id, contact, email):
    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE supplier
                SET name = %s,
                    fiscal_id = %s,
                    contact = %s,
                    email = %s
                WHERE id = %s
            """, (name, fiscal_id, contact, email, supplier_id))

def fetch_all_stock_movements():
    conn = connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                sm.id,
                p.name AS product,
                sm.type,
                sm.label,
                sm.recipient,
                sm.quantity,
                sm.comment,
                sm.timestamp
            FROM stock_movement sm
            JOIN product p ON p.id = sm.product_id
            ORDER BY sm.timestamp DESC
        """)
        return cur.fetchall()

def fetch_product_stats():
    conn = connection()

    cur = conn.cursor(cursor_factory=DictCursor)

    # Total products
    cur.execute("SELECT COUNT(*) FROM product")
    total_products = cur.fetchone()[0]

    # Current stock per product (product_id -> stock)
    cur.execute("""
        SELECT p.id, p.name, p.threshold, 
               COALESCE(SUM(CASE sm.type WHEN 'IN' THEN sm.quantity ELSE -sm.quantity END), 0) AS stock
        FROM product p
        LEFT JOIN stock_movement sm ON p.id = sm.product_id
        GROUP BY p.id
    """)
    rows = cur.fetchall()

    total_stock = 0
    below_threshold = 0
    out_of_stock = 0
    stock_by_product = {}

    for row in rows:
        stock = row['stock']
        total_stock += stock
        stock_by_product[row['name']] = stock

        if stock == 0:
            out_of_stock += 1
        if stock < row['threshold']:
            below_threshold += 1

    # Top 5 products by stock
    top_products = dict(sorted(stock_by_product.items(), key=lambda x: x[1], reverse=True)[:5])

    cur.close()
    conn.close()

    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "below_threshold": below_threshold,
        "out_of_stock": out_of_stock,
        "top_products": top_products
    }

def fetch_stock_movement_stats():
    query = """
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE type = 'IN') AS total_in,
            COUNT(*) FILTER (WHERE type = 'OUT') AS total_out
        FROM stock_movement;
    """

    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result:
                return {
                    "total": result[0],
                    "in": result[1],
                    "out": result[2]
                }
    return {"total": 0, "in": 0, "out": 0}


def fetch_bar_chart_data():
    """
    Returns data for the BarChartWidget: movement count per day over the past week.
    """
    query = """
        SELECT
            DATE(timestamp) AS day,
            COUNT(*) FILTER (WHERE type = 'IN') AS in_count,
            COUNT(*) FILTER (WHERE type = 'OUT') AS out_count
        FROM stock_movement
        WHERE timestamp >= CURRENT_DATE - INTERVAL '6 days'
        GROUP BY day
        ORDER BY day;
    """

    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    labels = []
    in_counts = []
    out_counts = []
    for r in rows:
        labels.append(r[0].strftime("%a"))  # e.g., Mon, Tue...
        in_counts.append(r[1] or 0)
        out_counts.append(r[2] or 0)

    return {
        "labels": labels,
        "datasets": [
            {"label": "IN", "data": in_counts, "backgroundColor": "#28a745"},
            {"label": "OUT", "data": out_counts, "backgroundColor": "#dc3545"},
        ]
    }


def fetch_pie_chart_data():
    """
    Returns data for the PieChartWidget: total quantity IN vs OUT.
    """
    query = """
        SELECT
            SUM(quantity) FILTER (WHERE type = 'IN') AS in_qty,
            SUM(quantity) FILTER (WHERE type = 'OUT') AS out_qty
        FROM stock_movement;
    """

    conn = connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()

    in_qty = result[0] or 0
    out_qty = result[1] or 0

    return {
        "labels": ["IN", "OUT"],
        "data": [in_qty, out_qty],
        "backgroundColor": ["#28a745", "#dc3545"]
    }


def fetch_all_users():
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, email, is_admin, created_at FROM users ORDER BY username;")
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} users.")
                return rows
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in fetch_all_users: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_all_users: {e}")
        
def insert_user(username, email, password_hash, is_admin=False):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (%s, %s, %s, %s)
    """, (username, email, password_hash, is_admin))
    conn.commit()
    conn.close()

def fetch_all_suppliers_id_name():
    try:
        conn = connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM supplier ORDER BY name;")
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} suppliers.")
                return rows
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error in fetch_all_suppliers_id_name: {e.pgerror}")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_all_suppliers_id_name: {e}")

def insert_supplier(name, fiscal_id, contact, email, address):
    conn = connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO supplier (name, fiscal_id, contact, email, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, fiscal_id, contact, email, address))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        
def fetch_all_suppliers():
    conn = connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id, name, fiscal_id, contact, email, address, created_at FROM supplier ORDER BY created_at DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()


def get_or_create_supplier_id(name):
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM supplier WHERE name = %s", (name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute(
            "INSERT INTO supplier (name, fiscal_id) VALUES (%s, %s) RETURNING id",
            (name, f"AUTO-{name[:3].upper()}"),
        )
        conn.commit()
        return cursor.fetchone()[0]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def delete_user_by_id(user_id):
    conn = connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
def delete_supplier_by_id(supplier_id):
    conn = connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM supplier WHERE id = %s", (supplier_id,))
        conn.commit()

def update_product_archived_status(product_id, archived):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE product SET is_archived = %s WHERE id = %s", (archived, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    

def get_user_by_email(email):
    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None


def fetch_all_clients():
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM client ORDER BY created_at DESC;")
            return cur.fetchall()

def delete_client_by_id(client_id):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM client WHERE id = %s;", (client_id,))

def insert_client(name, fiscal_id="", contact="", email="", address=""):
    with connection() as conn:
        with conn.cursor() as cur:
            # Use the RETURNING clause to get the last inserted ID
            cur.execute("""
                INSERT INTO client (name, fiscal_id, contact, email, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (name, fiscal_id, contact, email, address))

            # Fetch the returned ID of the newly inserted client
            new_client_id = cur.fetchone()[0]  # Fetch the first column (id)

            return new_client_id


def update_client(client_id, name, fiscal_id, contact, email, address):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE client
                SET name = %s, fiscal_id = %s, contact = %s, email = %s, address = %s
                WHERE id = %s
            """, (name, fiscal_id, contact, email, address, client_id))
