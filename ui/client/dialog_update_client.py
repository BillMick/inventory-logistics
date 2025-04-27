from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QVBoxLayout
from db.manager import update_client

class UpdateClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Client")
        self.client_data = client_data

        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit(client_data["name"])
        self.fiscal_id_input = QLineEdit(client_data["fiscal_id"])
        self.contact_input = QLineEdit(client_data["contact"])
        self.email_input = QLineEdit(client_data["email"])
        self.address_input = QLineEdit(client_data.get("address", ""))

        form.addRow("Name", self.name_input)
        form.addRow("Fiscal ID", self.fiscal_id_input)
        form.addRow("Contact", self.contact_input)
        form.addRow("Email", self.email_input)
        form.addRow("Address", self.address_input)

        layout.addLayout(form)

        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self.update_client)
        layout.addWidget(update_btn)

        self.setLayout(layout)

    def update_client(self):
        try:
            update_client(
                self.client_data["id"],
                self.name_input.text(),
                self.fiscal_id_input.text(),
                self.contact_input.text(),
                self.email_input.text(),
                self.address_input.text()
            )
            QMessageBox.information(self, "Updated", "Client updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
