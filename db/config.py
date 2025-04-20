import psycopg2

def connection():
    return psycopg2.connect(
        dbname = "inventory_logistics",
        user = "postgres",
        password = "",
        host = "localhost",
        port = "5432"
    )