from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from db.manager import update_product_by_id

class UpdateProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Mise à jour de Produit")
        self.product_id = product["id"]

        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit(product["name"])
        self.code_input = QLineEdit(product["code"])
        self.category_input = QLineEdit(product["category"])
        self.unit_input = QLineEdit(product["unit"])
        self.price_input = QLineEdit(str(product["price"]))
        self.description_input = QLineEdit(product["description"])
        self.threshold_input = QLineEdit(str(product["threshold"]))

        form.addRow("Nom", self.name_input)
        form.addRow("Code", self.code_input)
        form.addRow("Catégorie", self.category_input)
        form.addRow("Unité", self.unit_input)
        form.addRow("Prix", self.price_input)
        form.addRow("Description", self.description_input)
        form.addRow("Seuil", self.threshold_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save(self):
        try:
            update_product_by_id(
                self.product_id,
                self.name_input.text(),
                self.code_input.text(),
                self.category_input.text(),
                self.unit_input.text(),
                float(self.price_input.text()),
                self.description_input.text(),
                int(self.threshold_input.text())
            )
            QMessageBox.information(self, "Success", "Produit mis à jour.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update product.\n{e}")
