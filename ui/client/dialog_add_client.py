from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QVBoxLayout
from db.manager import insert_client

class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter Client")
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.fiscal_id_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()

        form.addRow("Nom", self.name_input)
        form.addRow("ID Fiscal", self.fiscal_id_input)
        form.addRow("Contact", self.contact_input)
        form.addRow("Email", self.email_input)
        form.addRow("Adresse", self.address_input)

        layout.addLayout(form)

        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_client)
        layout.addWidget(save_btn)

        self.setLayout(layout)
        
        self.new_client_id = None

    def save_client(self):
        try:
            self.new_client_id = insert_client(
                self.name_input.text(),
                self.fiscal_id_input.text(),
                self.contact_input.text(),
                self.email_input.text(),
                self.address_input.text()
            )
            QMessageBox.information(self, "Succès", "Client ajouté.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def get_new_client_id(self):
        # Return the ID of the newly added client
        return self.new_client_id