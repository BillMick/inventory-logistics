import pandas as pd
from datetime import datetime
from db.manager import get_or_create_supplier_id, insert_product, insert_stock_movement

def import_products_from_excel(file_path):
    df = pd.read_excel(file_path)
    # df.fillna("", inplace=True)

    for _, row in df.iterrows():
        name = row["Name"]
        code = row["Code"]
        category = row["Category"]
        unit = row["Unit"] or "pcs"
        price = float(row["Price"] or 0.0)
        threshold = int(row["Threshold"] or 3)
        description = row["Description"] or ""
        supplier_name = row["Supplier"]
        stock = int(row["Stock"] or 0)
        
        supplier_id = get_or_create_supplier_id(supplier_name)
        
        product_id, _ = insert_product(name, category, supplier_id, unit, price, description, threshold)
        
        insert_stock_movement(product_id, "IN", "Incoming", "Stock added during import", "Service", stock)
        
