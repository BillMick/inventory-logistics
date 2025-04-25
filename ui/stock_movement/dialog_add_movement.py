from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QDialogButtonBox, QMessageBox
)
from db.manager import fetch_all_products, insert_stock_movement

class AddMovementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Stock Movement")

        layout = QVBoxLayout()
        form = QFormLayout()

        # Product selection dropdown
        self.product_dropdown = QComboBox()
        products = fetch_all_products()
        for product in products:
            self.product_dropdown.addItem(f"{product[1]} ({product[2]})", product[0])  # Product name and code

        # Type dropdown (IN or OUT)
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["IN", "OUT"])

        # Other input fields
        self.label_input = QLineEdit()
        self.reason_input = QLineEdit()
        self.service_input = QLineEdit()

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999999)

        # Add form rows
        form.addRow("Product", self.product_dropdown)
        form.addRow("Type", self.type_dropdown)
        form.addRow("Label", self.label_input)
        form.addRow("Reason", self.reason_input)
        form.addRow("Service", self.service_input)
        form.addRow("Quantity", self.quantity_input)

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
            label = self.label_input.text()
            reason = self.reason_input.text()
            service = self.service_input.text()
            quantity = self.quantity_input.value()

            # Insert the stock movement
            insert_stock_movement(product_id, movement_type, label, reason, service, quantity)

            QMessageBox.information(self, "Success", "Stock movement added successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add movement: {e}")
