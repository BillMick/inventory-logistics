from db.config import connection
from models.models import Product, StockMovement
from datetime import datetime

# ---- Helper: Generate Product Code ----
def generate_product_code():
    conn = connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM product;")
    count = cur.fetchone()[0] + 1
    code = f"PRD-{str(count).zfill(4)}"
    cur.close()
    conn.close()
    return code

# Insert Product
def insert_product(name, description="", threshold=0, unit="pcs"):
    code = generate_product_code()
    conn = connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO product (name, code, category, price, description, threshold, unit)
        VALUES (%s, %s, %s, %f, %s, %s, %s)
        RETURNING *;
    """, (name, code, description, threshold, unit))

    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return Product(*row)

# Insert Stock Movement
def insert_stock_movement(product_id, type_, label, reason, service, quantity):
    conn = connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO stock_movement (product_id, type, label, reason, service, quantity)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *;
    """, (product_id, type_, label, reason, service, quantity))

    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return StockMovement(*row)

# Fetch All Products
def get_all_products():
    conn = connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM product ORDER BY name;")
    rows = cur.fetchall()

    products = [Product(*row) for row in rows]

    cur.close()
    conn.close()
    return products

# Fetch Stock Movements (Optionally filter by product)
def get_stock_movements(product_id=None):
    conn = connection()
    cur = conn.cursor()

    if product_id:
        cur.execute("SELECT * FROM stock_movement WHERE product_id = %s ORDER BY timestamp DESC;", (product_id,))
    else:
        cur.execute("SELECT * FROM stock_movement ORDER BY timestamp DESC;")

    rows = cur.fetchall()
    movements = [StockMovement(*row) for row in rows]

    cur.close()
    conn.close()
    return movements
