from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from db.manager import update_supplier_by_id

class UpdateSupplierDialog(QDialog):
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.setWindowTitle("Update Supplier")
        self.supplier_id = supplier["id"]

        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit(supplier["name"])
        self.fiscal_id_input = QLineEdit(supplier["fiscal_id"])
        self.contact_input = QLineEdit(supplier["contact"])
        self.email_input = QLineEdit(supplier["email"])

        form.addRow("Name", self.name_input)
        form.addRow("Fiscal ID", self.fiscal_id_input)
        form.addRow("Contact", self.contact_input)
        form.addRow("Email", self.email_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save(self):
        try:
            update_supplier_by_id(
                self.supplier_id,
                self.name_input.text(),
                self.fiscal_id_input.text(),
                self.contact_input.text(),
                self.email_input.text()
            )
            QMessageBox.information(self, "Success", "Supplier updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update supplier.\n{e}")
