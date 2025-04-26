import pandas as pd
from datetime import datetime
from db.manager import get_or_create_supplier_id, insert_product

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
        # created_at = row["Added at"]

        # if isinstance(created_at, str):
        #     created_at = datetime.strptime(created_at, "%Y-%m-%d")
        # elif pd.isna(created_at):
        #     created_at = datetime.now()

        supplier_id = get_or_create_supplier_id(supplier_name)
        # insert_product(name, code, category, unit, price, threshold, description, supplier_id, created_at)
        insert_product(name, category, supplier_id, unit, price, description, threshold)
