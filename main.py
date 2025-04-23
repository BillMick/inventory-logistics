from PyQt5.QtWidgets import QApplication
from ui.product_dashboard import ProductDashboard
from ui.stock_movement_dashboard import StockMovementDashboard
from ui.main_interface import MainDashboard
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainDashboard()
    # window = StockMovementDashboard()
    # window = ProductDashboard()
    window.show()
    sys.exit(app.exec_())

