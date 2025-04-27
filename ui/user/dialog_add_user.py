# ui/add_user.py

import hashlib
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox
)
from db.manager import insert_user
from utils.auth import hash_password

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        # --- Username ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # --- Email ---
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # --- Password ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # --- Is Admin ---
        self.admin_checkbox = QCheckBox("Grant admin rights")
        layout.addWidget(self.admin_checkbox)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        btn_add = QPushButton("Add")
        btn_cancel = QPushButton("Cancel")
        btn_add.clicked.connect(self.add_user)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_user(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        is_admin = self.admin_checkbox.isChecked()

        if not username or not email or not password:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        # Hash the password
        import bcrypt
        password_hash = hash_password(password)

        try:
            insert_user(username, email, password_hash, is_admin)
            QMessageBox.information(self, "Success", f"User '{username}' added successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add user:\n{str(e)}")
