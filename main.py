from PyQt5.QtWidgets import QApplication
from ui.product_dashboard import ProductDashboard
from ui.stock_movement_dashboard import StockMovementDashboard
import sys

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # window = ProductDashboard()
    # window.show()
    # sys.exit(app.exec_())
    
    app = QApplication(sys.argv)
    window = StockMovementDashboard()
    window.show()
    sys.exit(app.exec_())
