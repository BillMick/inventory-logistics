from PyQt5.QtWidgets import QApplication
from ui.product.dashboard_product import ProductDashboard
from ui.stock_movement.dashboard_stock_movement import StockMovementDashboard
from ui.main_interface import MainDashboard
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainDashboard()
    # window = StockMovementDashboard()
    # window = ProductDashboard()
    window.show()
    sys.exit(app.exec_())

