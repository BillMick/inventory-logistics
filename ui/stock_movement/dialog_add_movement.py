from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QDialogButtonBox, QMessageBox
)
from db.manager import fetch_all_products, insert_stock_movement, fetch_all_clients

class AddMovementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter mouvement de stock")

        layout = QVBoxLayout()
        form = QFormLayout()

        # Produit selection dropdown
        self.product_dropdown = QComboBox()
        products = fetch_all_products()
        for product in products:
            self.product_dropdown.addItem(f"{product[1]} ({product[2]})", product[0])  # Produit name and code

        # Type dropdown (IN or OUT)
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["IN", "OUT"])

        # Other input fields
        self.label_input = QLineEdit()
        # Label dropdown (will update based on type)
        self.label_input = QComboBox()
        self.update_label_options("IN")

        # Connect type change to update label options
        self.type_dropdown.currentTextChanged.connect(self.update_label_options)
        self.type_dropdown.currentTextChanged.connect(self.toggle_recipient_visibility)
        
        # self.recipient_input = QLineEdit()
        # Editable client selection dropdown (existing or custom)
        self.recipient_input = QComboBox()
        self.recipient_input.setEditable(True)  # Make it editable
        self.recipient_input.addItem("Sélectionner client")  # Default prompt text
        self.clients = fetch_all_clients()
        for client in self.clients:
            self.recipient_input.addItem(client[1], client[0])  # client name, client id
        self.recipient_input.setVisible(False)
        
        self.comment_input = QLineEdit()

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999999)

        # Add form rows
        form.addRow("Produit", self.product_dropdown)
        form.addRow("Type", self.type_dropdown)
        form.addRow("Label", self.label_input)
        form.addRow("Récepteur", self.recipient_input)
        form.addRow("Quantité", self.quantity_input)
        form.addRow("Commentaire", self.comment_input)

        layout.addLayout(form)

        # Buttons (Save / Cancel)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_movement)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_movement(self):
        try:
            product_id = self.product_dropdown.currentData()  # Get selected product ID
            movement_type = self.type_dropdown.currentText()
            label = self.label_input.currentText()
            comment = self.comment_input.text()
            recipient = self.recipient_input.currentText()
            quantity = self.quantity_input.value()
            
            if movement_type == "OUT" and recipient == "Sélectionner client":
                QMessageBox.warning(self, "Warning", "Sélectionnez ou ajoutez un client.")
                return

            # Check if recipient exists in the list or is new
            recipient_id = None
            if movement_type == "OUT":
                for client in self.clients:
                    if client[1].lower() == recipient.lower():
                        recipient_id = client[0]  # Existing client ID
                        break
            elif movement_type == "IN":
                recipient = "Service"  # Default recipient for "IN" movement
                recipient_id = 0

            # If the recipient is new (not found in the list), add them to the database
            if recipient_id is None:
                recipient_id = self.add_new_client(recipient)  # Function to add new client

            # Insert the stock movement
            insert_stock_movement(product_id, movement_type, label, comment, recipient, quantity)

            QMessageBox.information(self, "Success", "Mouvement de Stock ajouté.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Echec d'ajout: {e}")
    
    def update_label_options(self, movement_type):
        self.label_input.clear()
        if movement_type == "IN":
            self.label_input.addItems(["Nouvel arrivage", "Retour"])
        elif movement_type == "OUT":
            self.label_input.addItems(["Livraison", "Réassortiment"])

    def toggle_recipient_visibility(self, movement_type):
        if movement_type == "IN":
            self.recipient_input.setVisible(False)  # Hide recipient input for "IN"
        else:
            self.recipient_input.setVisible(True)  # Show recipient input for "OUT"
            if self.recipient_input.currentText() == "Sélectionner client":
                self.recipient_input.setCurrentText("")
    def add_new_client(self, client_name):
        # Function to add a new client to the database
        from ui.client.dialog_add_client import AddClientDialog
        dialog = AddClientDialog(self)
        dialog.name_input.setText(client_name)
        if dialog.exec_():
            # After adding the client, refresh the client list
            self.recipient_input.clear()
            self.recipient_input.addItem("Sélectionner client")
            self.clients = fetch_all_clients()
            for client in self.clients:
                self.recipient_input.addItem(client[1], client[0])  # client name, client id
            return dialog.get_new_client_id()
        return None