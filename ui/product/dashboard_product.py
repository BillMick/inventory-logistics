from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel, QFrame, QSizePolicy,
    QLineEdit, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from db.manager import fetch_all_products_with_stock
from ui.product.dialog_add_product import AddProductDialog


class ProductDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Dashboard")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- KPI Section ---
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(10)

        self.total_label = self.create_stat_card("Total Products", "0")
        self.stock_label = self.create_stat_card("Total Stock", "0", "#28a745")
        self.below_label = self.create_stat_card("Below Threshold", "0", "#ffc107")
        self.out_label = self.create_stat_card("Out of Stock", "0", "#dc3545")

        self.kpi_layout.addWidget(self.total_label)
        self.kpi_layout.addWidget(self.stock_label)
        self.kpi_layout.addWidget(self.below_label)
        self.kpi_layout.addWidget(self.out_label)

        layout.addLayout(self.kpi_layout)
        layout.addWidget(self.horizontal_line())

        # --- Filter Bar ---
        filter_layout = QHBoxLayout()

        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Filter by product name...")
        self.name_filter.textChanged.connect(self.load_products)

        btn_add = QPushButton("Add Product")
        btn_add.clicked.connect(self.add_product)
        btn_add.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_products)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")

        filter_layout.addStretch()
        filter_layout.addWidget(self.name_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_refresh)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Code", "Category", "Unit", "Price", "Threshold", "Stock", "Added at", "Description"
        ])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.edit_product)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

    def create_stat_card(self, title, value, color="#007bff"):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        frame.setLayout(layout)
        frame.value_label = value_label
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return frame

    def horizontal_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #ced4da;")
        return line

    def load_products(self):
        self.table.setRowCount(0)
        products = fetch_all_products_with_stock()

        total_stock = 0
        below_threshold = 0
        out_of_stock = 0

        name_filter_text = self.name_filter.text().lower()
        filtered_products = []

        for product in products:
            if name_filter_text and name_filter_text not in product[1].lower():
                continue
            filtered_products.append(product)

        for row_idx, product in enumerate(filtered_products):
            self.table.insertRow(row_idx)
            for col_idx in range(10):
                item = QTableWidgetItem(str(product[col_idx]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            stock = product[7]
            threshold = product[6]
            total_stock += stock

            if stock <= threshold:
                below_threshold += 1
                color = QColor(255, 153, 51)  # Orange
            if stock == 0:
                out_of_stock += 1
                color = QColor(255, 102, 102)  # Red
            else:
                color = QColor(153, 255, 153)  # Green

            self.table.item(row_idx, 7).setBackground(color)

        # --- Update KPI cards ---
        self.total_label.value_label.setText(str(len(filtered_products)))
        self.stock_label.value_label.setText(str(total_stock))
        self.below_label.value_label.setText(str(below_threshold))
        self.out_label.value_label.setText(str(out_of_stock))

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

        from ui.product.dialog_update_product import UpdateProductDialog
        dialog = UpdateProductDialog(self, product_data)
        if dialog.exec_():
            self.load_products()
