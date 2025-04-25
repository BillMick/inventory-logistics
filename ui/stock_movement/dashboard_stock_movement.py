from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit,
    QHeaderView
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from db.manager import *


class StockMovementDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Movement Dashboard")
        self.showMaximized()  # ← This opens it maximized, not fullscreen

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- KPI Section ---
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(10)
        self.total_label = self.create_stat_card("Total Movements", "0")
        self.in_label = self.create_stat_card("Total IN", "0", "#28a745")
        self.out_label = self.create_stat_card("Total OUT", "0", "#dc3545")
        self.avg_qty_label = self.create_stat_card("Avg Quantity", "0")
        self.last_movement_label = self.create_stat_card("Last Movement", "-")

        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.in_label)
        self.stats_layout.addWidget(self.out_label)
        self.stats_layout.addWidget(self.avg_qty_label)
        self.stats_layout.addWidget(self.last_movement_label)

        layout.addLayout(self.stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Filter + Buttons Section ---
        filter_layout = QHBoxLayout()

        self.base_filter = QLineEdit()
        self.base_filter.setPlaceholderText("Filter by base name...")
        self.base_filter.textChanged.connect(self.load_movements)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "IN", "OUT"])
        self.type_filter.currentIndexChanged.connect(self.load_movements)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_movements)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")

        btn_add = QPushButton("Add Movement")
        btn_add.clicked.connect(self.add_movement)
        btn_add.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")

        btn_quit = QPushButton("Quit")
        btn_quit.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        btn_quit.clicked.connect(self.close)

        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.base_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Type", "Label", "Reason", "Service", "Quantity", "Timestamp"
        ])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)  # ✅ Enable sorting

        # Optional: Resize columns to content initially
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_movements()
        

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

    def load_movements(self):
        self.table.setRowCount(0)
        movements = fetch_all_stock_movements()

        selected_type = self.type_filter.currentText()
        base_filter_text = self.base_filter.text().lower()
        filtered = []

        in_count = out_count = total_qty = 0
        last_movement = "-"

        for m in movements:
            base_name = m[1].lower()
            if selected_type != "All" and m[2] != selected_type:
                continue
            if base_filter_text and base_filter_text not in base_name:
                continue
            filtered.append(m)
            if m[2] == "IN":
                in_count += 1
            elif m[2] == "OUT":
                out_count += 1
            total_qty += m[6]
            last_movement = m[7]

        for row_num, m in enumerate(filtered):
            self.table.insertRow(row_num)
            for col_idx, value in enumerate(m):
                item = QTableWidgetItem(str(value))
                if col_idx == 2:
                    item.setForeground(QColor("green") if m[2] == "IN" else QColor("red"))
                self.table.setItem(row_num, col_idx, item)

        total_count = len(filtered)
        avg_qty = round(total_qty / total_count, 2) if total_count else 0
        self.total_label.value_label.setText(str(total_count))
        self.in_label.value_label.setText(str(in_count))
        self.out_label.value_label.setText(str(out_count))
        self.avg_qty_label.value_label.setText(str(avg_qty))
        self.last_movement_label.value_label.setText(str(last_movement))

    def add_movement(self):
        from ui.stock_movement.dialog_add_movement import AddMovementDialog
        dialog = AddMovementDialog(self)
        if dialog.exec_():
            self.load_movements()
