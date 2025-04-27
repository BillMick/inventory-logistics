# ui/add_product_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from db.manager import insert_product, fetch_all_suppliers_id_name

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter nouveau produit")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.unit_input = QComboBox()
        self.unit_input.addItems(["pcs", "kg", "litre", "box"])

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999999999)
        self.price_input.setDecimals(2)

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(60)
        
        self.threshold_input = QSpinBox()
        self.threshold_input.setMaximum(100000)
        
        self.supplier_input = QComboBox()
        self.supplier_map = {}
        self.load_suppliers()

        layout.addWidget(QLabel("Nom"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Catégorie"))
        layout.addWidget(self.category_input)

        layout.addWidget(QLabel("Unité"))
        layout.addWidget(self.unit_input)

        layout.addWidget(QLabel("Prix"))
        layout.addWidget(self.price_input)

        layout.addWidget(QLabel("Description"))
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("Seuil d'alerte"))
        layout.addWidget(self.threshold_input)
        
        layout.addWidget(QLabel("Fournisseur"))
        layout.addWidget(self.supplier_input)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Ajouter")
        btn_cancel = QPushButton("Annuler")

        btn_add.clicked.connect(self.submit)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_suppliers(self):
        self.supplier_input.addItem("— None —", None)
        suppliers = fetch_all_suppliers_id_name()  # Should return list of (id, name)
        if suppliers:
            for sid, name in suppliers:
                self.supplier_input.addItem(name, sid)
                self.supplier_map[name] = sid

    def submit(self):
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        unit = self.unit_input.currentText()
        price = self.price_input.value()
        description = self.description_input.toPlainText().strip()
        threshold = self.threshold_input.value()
        supplier_id = self.supplier_input.currentData()

        if not name or not category:
            QMessageBox.warning(self, "Données manquantes", "Remplissez tous les champs requis.")
            return

        success = insert_product(name, category, supplier_id, unit, price, description, threshold)
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Echec d'ajout du produit.")
