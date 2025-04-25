from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from db.manager import insert_supplier

class AddSupplierDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Supplier")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.fiscal_id_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Fiscal ID:"))
        layout.addWidget(self.fiscal_id_input)
        layout.addWidget(QLabel("Contact:"))
        layout.addWidget(self.contact_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)

        button_layout = QHBoxLayout()
        btn_add = QPushButton("Add")
        btn_cancel = QPushButton("Cancel")
        btn_add.clicked.connect(self.add_supplier)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_supplier(self):
        name = self.name_input.text().strip()
        fiscal_id = self.fiscal_id_input.text().strip()
        contact = self.contact_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not fiscal_id:
            QMessageBox.warning(self, "Validation Error", "Name and Fiscal ID are required.")
            return

        try:
            insert_supplier(name, fiscal_id, contact, email, address)
            QMessageBox.information(self, "Success", f"Supplier '{name}' added successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add supplier:\n{str(e)}")
