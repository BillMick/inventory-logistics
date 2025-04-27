from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit,
    QHeaderView, QFileDialog, QMessageBox
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
        # self.avg_qty_label = self.create_stat_card("Avg Quantity", "0")
        self.last_movement_label = self.create_stat_card("Last Movement", "-")
        
        self.label_stats_layout = QHBoxLayout()
        self.label_stats_layout.setSpacing(10)
        self.incoming_label = self.create_stat_card("Incoming", "0", "#6f42c1")
        self.back_label = self.create_stat_card("Back", "0", "#20c997")
        self.delivery_label = self.create_stat_card("Delivery", "0", "#fd7e14")
        self.restocking_label = self.create_stat_card("Restocking", "0", "#ffc107")

        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.in_label)
        self.stats_layout.addWidget(self.out_label)
        # self.stats_layout.addWidget(self.avg_qty_label)
        self.stats_layout.addWidget(self.last_movement_label)
        self.label_stats_layout.addWidget(self.incoming_label)
        self.label_stats_layout.addWidget(self.back_label)
        self.label_stats_layout.addWidget(self.delivery_label)
        self.label_stats_layout.addWidget(self.restocking_label)

        layout.addLayout(self.stats_layout)
        layout.addWidget(self.horizontal_line())
        layout.addLayout(self.label_stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Filter + Buttons Section ---
        filter_layout = QHBoxLayout()

        self.base_filter = QLineEdit()
        self.base_filter.setPlaceholderText("Filter by base name...")
        self.base_filter.textChanged.connect(self.load_movements)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "IN", "OUT"])
        self.type_filter.currentIndexChanged.connect(self.load_movements)
        
        btn_export = QPushButton("Export PDF")
        btn_export.clicked.connect(self.export_pdf_report)
        btn_export.setStyleSheet("background-color: #6c757d; color: white;")

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_movements)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white;")

        btn_add = QPushButton("Add Movement")
        btn_add.clicked.connect(self.add_movement)
        btn_add.setStyleSheet("background-color: #007bff; color: white;")
        
        btn_verify_inventory = QPushButton("Verify Inventory")
        btn_verify_inventory.clicked.connect(self.open_inventory_verification)
        btn_verify_inventory.setStyleSheet("background-color: #343a40; color: white;")

        btn_quit = QPushButton("Quit")
        btn_quit.setStyleSheet("background-color: #dc3545; color: white;")
        btn_quit.clicked.connect(self.close)

        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.base_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_export)
        filter_layout.addWidget(btn_verify_inventory)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Type", "Label", "Recipient", "Quantity", "Comment", "Timestamp"
        ])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)

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
        incoming_count = back_count = delivery_count = restocking_count = 0

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
            total_qty += m[5]
            last_movement = m[7]
            label = m[3]
            if label == "Incoming":
                incoming_count += 1
            elif label == "Back":
                back_count += 1
            elif label == "Delivery":
                delivery_count += 1
            elif label == "Restocking":
                restocking_count += 1


        for row_num, m in enumerate(filtered):
            self.table.insertRow(row_num)
            for col_idx, value in enumerate(m):
                item = QTableWidgetItem(str(value))
                if col_idx == 2:
                    item.setForeground(QColor("green") if m[2] == "IN" else QColor("red"))
                self.table.setItem(row_num, col_idx, item)

        total_count = len(filtered)
        self.total_label.value_label.setText(str(total_count))
        self.in_label.value_label.setText(str(in_count))
        self.out_label.value_label.setText(str(out_count))
        self.last_movement_label.value_label.setText(str(last_movement))
        self.incoming_label.value_label.setText(str(incoming_count))
        self.back_label.value_label.setText(str(back_count))
        self.delivery_label.value_label.setText(str(delivery_count))
        self.restocking_label.value_label.setText(str(restocking_count))

    def add_movement(self):
        from ui.stock_movement.dialog_add_movement import AddMovementDialog
        dialog = AddMovementDialog(self)
        if dialog.exec_():
            self.load_movements()

    def export_pdf_report(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from datetime import datetime

        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PDF Files (*.pdf)")
        if filepath:
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "Stock Movement Report")

        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y_pos = height - 100

        # --- Add KPI Cards ---
        kpis = [
            self.total_label,
            self.in_label,
            self.out_label,
            self.last_movement_label,
            self.incoming_label,
            self.back_label,
            self.delivery_label,
            self.restocking_label
        ]
        for card in kpis:
            label = card.layout().itemAt(1).widget().text()
            value = card.value_label.text()
            c.drawString(50, y_pos, f"{label}: {value}")
            y_pos -= 15
            if y_pos < 100:
                c.showPage()
                y_pos = height - 50

        c.showPage()

        # --- Add Table Content ---
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        data = [headers]

        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Paginate if too long
        rows_per_page = 25
        for i in range(0, len(data), rows_per_page):
            table_data = data[i:i + rows_per_page]
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ]))
            w, h = table.wrapOn(c, width - 100, height)
            table.drawOn(c, 50, height - h - 50)
            c.showPage()

        c.save()
        print(f"Stock movement report saved as {filepath}")
        QMessageBox.information(self, "Export Successful", f"PDF report saved to:\n{filepath}")
        
    def open_inventory_verification(self):
        from ui.stock_movement.dialog_inventory_verification import InventoryVerificationDialog
        dialog = InventoryVerificationDialog(self)
        dialog.exec_()