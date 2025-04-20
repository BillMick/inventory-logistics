from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel
)
from PyQt5.QtGui import QColor
from db.manager import *

class StockMovementDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Movement Dashboard")
        self.resize(900, 500)

        layout = QVBoxLayout()

        # --- Top Controls ---
        filter_layout = QHBoxLayout()
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "IN", "OUT"])
        self.type_filter.currentIndexChanged.connect(self.load_movements)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_movements)

        btn_add = QPushButton("Add Movement")
        btn_add.clicked.connect(self.add_movement)

        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_refresh)

        layout.addLayout(filter_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Type", "Label", "Reason", "Service", "Quantity", "Timestamp"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_movements()

    def load_movements(self):
        self.table.setRowCount(0)
        movements = fetch_all_stock_movements()
        selected_type = self.type_filter.currentText()
        row_num = 0
        for row_idx, m in enumerate(movements):
            if selected_type != "All" and m[2] != selected_type:
                continue

            self.table.insertRow(row_num)
            for col_idx, value in enumerate(m):
                item = QTableWidgetItem(str(value))
                if col_idx == 2:
                    item.setForeground(QColor("green") if m[2] == "IN" else QColor("red"))
                self.table.setItem(row_num, col_idx, item)
            row_num += 1

    def add_movement(self):
        from ui.add_movement import AddMovementDialog
        dialog = AddMovementDialog(self)
        if dialog.exec_():
            self.load_movements()
