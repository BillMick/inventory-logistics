import pandas as pd
from datetime import datetime
from db.manager import get_or_create_supplier_id, insert_product, insert_stock_movement

def import_products_from_excel(file_path):
    df = pd.read_excel(file_path)
    # df.fillna("", inplace=True)

    for _, row in df.iterrows():
        name = row["Nom"]
        code = row["Code"]
        category = row["Catégorie"]
        unit = row["Unité"] or "pcs"
        price = float(row["Prix"] or 0.0)
        threshold = int(row["Seuil"] or 3)
        description = row["Description"] or ""
        supplier_name = row["Fournisseur"]
        stock = int(row["Stock"] or 0)
        
        supplier_id = get_or_create_supplier_id(supplier_name)
        
        product_id, _ = insert_product(name, category, supplier_id, unit, price, description, threshold)
        
        insert_stock_movement(product_id, "IN", "Nouvel arrivage", "Stock ajouté par importation de fichier", "Service", stock)
        
