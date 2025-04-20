from db.config import connection

def create_tables():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS product (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            unit TEXT DEFAULT 'pcs',
            price FLOAT DEFAULT 0.0,
            description TEXT,
            threshold INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS stock_movement (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
            type VARCHAR(10) CHECK (type IN ('IN', 'OUT')) NOT NULL,
            label TEXT NOT NULL,
            reason TEXT,
            service TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    conn = connection()
    cur = conn.cursor()
    for q in queries:
        cur.execute(q)
    conn.commit()
    cur.close()
    conn.close()
