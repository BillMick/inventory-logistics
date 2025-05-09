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
        self.username_input.setPlaceholderText("Entrer le nom")
        layout.addWidget(QLabel("Nom d'utilisateur:"))
        layout.addWidget(self.username_input)

        # --- Email ---
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Entrer email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # --- Password ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Mot de passe:"))
        layout.addWidget(self.password_input)

        # --- Is Admin ---
        self.admin_checkbox = QCheckBox("Accorder les droits d'admin")
        layout.addWidget(self.admin_checkbox)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        btn_add = QPushButton("Ajouter")
        btn_cancel = QPushButton("Annuler")
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
            QMessageBox.warning(self, "Erreur de Validation", "Tous les champs sont requis.")
            return

        # Hash the password
        import bcrypt
        password_hash = hash_password(password)

        try:
            insert_user(username, email, password_hash, is_admin)
            QMessageBox.information(self, "Succès", f"Utilisateur '{username}' ajouté.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Echec d'ajout:\n{str(e)}")
