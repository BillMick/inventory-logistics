from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel, QFrame, QSizePolicy,
    QLineEdit, QHeaderView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from db.manager import fetch_all_products_with_stock, update_product_archived_status
from utils.excel_importer import import_products_from_excel
from ui.product.dialog_add_product import AddProductDialog
import pandas as pd

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
        self.value_label = self.create_stat_card("Stock Value", "$0.00", "#6f42c1")

        self.kpi_layout.addWidget(self.total_label)
        self.kpi_layout.addWidget(self.stock_label)
        self.kpi_layout.addWidget(self.below_label)
        self.kpi_layout.addWidget(self.out_label)
        self.kpi_layout.addWidget(self.value_label)

        layout.addLayout(self.kpi_layout)
        layout.addWidget(self.horizontal_line())

        # --- Filter Bar ---
        filter_layout = QHBoxLayout()

        self.name_filter = QLineEdit()
        self.is_archived_filter = QComboBox()
        self.is_archived_filter.addItems(["Not Archived", "Archived", "All"])
        self.is_archived_filter.currentIndexChanged.connect(self.load_products)

        self.name_filter.setPlaceholderText("Filter by product name...")
        self.name_filter.textChanged.connect(self.load_products)
        
        btn_add = QPushButton("Add Product")
        btn_add.clicked.connect(self.add_product)
        btn_add.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        
        btn_import = QPushButton("Import from Excel")
        btn_import.clicked.connect(self.import_products)
        btn_import.setStyleSheet("background-color: #20c997; color: white; font-weight: bold;")
        
        btn_export = QPushButton("Export to Excel")
        btn_export.clicked.connect(self.export_to_excel)
        btn_export.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_products)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")

        filter_layout.addStretch()
        filter_layout.addWidget(self.name_filter)
        filter_layout.addWidget(self.is_archived_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_import)
        filter_layout.addWidget(btn_export)
        filter_layout.addWidget(btn_refresh)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Code", "Category", "Unit", "Price", 
            "Supplier", "Threshold", "Stock", "Total Value", "Added at", 
            "Description", "Action"
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
        inventory_value = 0.0
        self.table.setRowCount(0)
        products = fetch_all_products_with_stock()
        # print(products)

        total_stock = 0
        below_threshold = 0
        out_of_stock = 0

        name_filter_text = self.name_filter.text().lower()
        archived_filter = self.is_archived_filter.currentText()
        filtered_products = []

        for product in products:
            if name_filter_text and name_filter_text not in product[1].lower():
                continue

            is_archived = product[11]  # Assuming index 11 is is_archived, update if needed

            if archived_filter == "Not Archived" and is_archived:
                continue
            elif archived_filter == "Archived" and not is_archived:
                continue

            filtered_products.append(product)

        for row_idx, product in enumerate(filtered_products):
            self.table.insertRow(row_idx)
            for col_idx in range(11):
                item = QTableWidgetItem(str(product[col_idx]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

            stock = product[8]
            threshold = product[7]
            total_stock += stock
            price = float(product[5])
            total_value = stock * price
            
            # Insert total value in column 9 (after Stock)
            total_item = QTableWidgetItem(f"${total_value:,.2f}")
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 9, total_item)

            # Shift "Added at" and "Description" to next columns
            added_item = QTableWidgetItem(str(product[9]))
            added_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 10, added_item)

            desc_item = QTableWidgetItem(str(product[10]))
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 11, desc_item)

            if stock > 0 and stock <= threshold:
                below_threshold += 1
                color = QColor(255, 153, 51)  # Orange
            elif stock > threshold:
                color = QColor(153, 255, 153)  # Green
            elif stock == 0:
                below_threshold += 1
                out_of_stock += 1
                color = QColor(255, 102, 102)  # Red

            self.table.item(row_idx, 8).setBackground(color)
            
            inventory_value += stock * price
            
            # Add Archive/Unarchive button
            action_btn = QPushButton("Unarchive" if product[11] else "Archive")  # Assuming is_archived is at index 11
            action_btn.setStyleSheet("background-color: #6c757d; color: white;")
            action_btn.clicked.connect(lambda checked, pid=product[0], archived=product[11]: self.toggle_archive(pid, archived))
            self.table.setCellWidget(row_idx, 12, action_btn)

        # --- Update KPI cards ---
        self.total_label.value_label.setText(str(len(filtered_products)))
        self.stock_label.value_label.setText(str(total_stock))
        self.below_label.value_label.setText(str(below_threshold))
        self.out_label.value_label.setText(str(out_of_stock))
        self.value_label.value_label.setText(f"${inventory_value:,.2f}")


    def import_products(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            try:
                import_products_from_excel(path)
                QMessageBox.information(self, "Success", "Products imported successfully!")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import products:\n{str(e)}")

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
            "threshold": int(self.table.item(row, 7).text()),
            "description": self.table.item(row, 11).text(),
        }

        from ui.product.dialog_update_product import UpdateProductDialog
        dialog = UpdateProductDialog(self, product_data)
        if dialog.exec_():
            self.load_products()

    def export_to_excel(self):
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        if row_count == 0:
            QMessageBox.warning(self, "Export Failed", "No data to export.")
            return

        # Extract data from QTableWidget
        data = []
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(col_count)]

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Ask user where to save the file
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if filepath:
            if not filepath.endswith(".xlsx"):
                filepath += ".xlsx"
            try:
                df.to_excel(filepath, index=False, engine='openpyxl')
                QMessageBox.information(self, "Export Successful", f"Products exported to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred:\n{str(e)}")
        self.load_products()

    def toggle_archive(self, product_id, currently_archived):
        try:
            update_product_archived_status(product_id, not currently_archived)
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update archive status:\n{str(e)}")