from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from db.manager import fetch_all_products_with_stock
from ui.add_product_dialog import AddProductDialog  # Assuming you have this dialog

class ProductDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Dashboard")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        # Header buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Product")
        btn_refresh = QPushButton("Refresh")
        btn_add.clicked.connect(self.add_product)
        btn_refresh.clicked.connect(self.load_products)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_refresh)
        layout.addLayout(btn_layout)

        # Table setup
        self.table = QTableWidget()
        self.table.cellDoubleClicked.connect(self.edit_product)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Code", "Category", "Unit", "Price", "Threshold", "Stock", "Added at", "Description"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        products = fetch_all_products_with_stock()
        # print(products)

        for row_idx, product in enumerate(products):
            self.table.insertRow(row_idx)

            # Fill regular columns
            for col_idx in range(10):  # 10 columns as defined above
                item = QTableWidgetItem(str(product[col_idx]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            # Highlight based on stock
            stock = product[7] # 40
            threshold = product[6]

            if stock == 0:
                color = QColor(255, 102, 102)  # red
                status = "❌"
            elif stock <= threshold:
                color = QColor(255, 153, 51)  # orange
                status = "⚠️"
            else:
                color = QColor(153, 255, 153)  # green
                status = "✅"

            # Set background color for all columns
            # for col in range(10):
            #     self.table.item(row_idx, col).setBackground(color)
            self.table.item(row_idx, 7).setBackground(color)
            
            # Override status cell with icon or emoji
            # self.table.setItem(row_idx, 9, QTableWidgetItem(status))

    def add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec_():
            self.load_products()
    
    def edit_product(self, row, column):
        product_id = int(self.table.item(row, 0).text())
        product_data = {
            "id": product_id,
            "name": self.table.item(row, 1).text(),
            "code": self.table.item(row, 2).text(),
            "category": self.table.item(row, 3).text(),
            "unit": self.table.item(row, 4).text(),
            "price": float(self.table.item(row, 5).text()),
            "threshold": int(self.table.item(row, 6).text()),
            "description": self.table.item(row, 9).text(),
        }

        from ui.update_product import UpdateProductDialog
        dialog = UpdateProductDialog(self, product_data)
        if dialog.exec_():
            self.load_products()
