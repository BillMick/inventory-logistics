from PyQt5.QtWidgets import QApplication, QDialog
from ui.main_interface import MainDashboard
from ui.login_dialog import LoginDialog
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = MainDashboard(user=login.user_data)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

