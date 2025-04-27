from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from db.manager import get_user_by_email
from utils.auth import verify_password

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.resize(300, 150)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.user_data = None

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        user = get_user_by_email(email)
        if user and verify_password(password, user["password_hash"]):
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid email or password.")
