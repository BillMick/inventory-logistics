from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit,
    QHeaderView, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from db.manager import fetch_all_users, delete_user_by_id
from functools import partial


class UserDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Management Dashboard")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- KPI Section ---
        self.stats_layout = QHBoxLayout()
        self.total_users = self.create_stat_card("Total Users", "0")
        self.admins = self.create_stat_card("Admins", "0", "#ffc107")
        self.last_user = self.create_stat_card("Last User", "-")

        self.stats_layout.addWidget(self.total_users)
        self.stats_layout.addWidget(self.admins)
        self.stats_layout.addWidget(self.last_user)

        layout.addLayout(self.stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Filter + Buttons Section ---
        filter_layout = QHBoxLayout()

        self.role_filter = QComboBox()
        self.role_filter.addItems(["All", "admin", "user"])
        self.role_filter.currentIndexChanged.connect(self.load_users)

        self.username_filter = QLineEdit()
        self.username_filter.setPlaceholderText("Filter by username...")
        self.username_filter.textChanged.connect(self.load_users)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_users)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white")

        btn_add = QPushButton("Add User")
        btn_add.clicked.connect(self.add_user)
        btn_add.setStyleSheet("background-color: #007bff; color: white")
        
        btn_pdf = QPushButton("Export to PDF")
        btn_pdf.clicked.connect(self.export_pdf_report)
        btn_pdf.setStyleSheet("background-color: #6c757d; color: white;")

        btn_quit = QPushButton("Quit")
        btn_quit.setStyleSheet("background-color: #dc3545; color: white")
        btn_quit.clicked.connect(self.close)

        filter_layout.addWidget(QLabel("Role:"))
        filter_layout.addWidget(self.role_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.username_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_pdf)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role","Created At", "Action"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_users()

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

    def load_users(self):
        self.table.setRowCount(0)
        users = fetch_all_users()

        selected_role = self.role_filter.currentText()
        username_filter_text = self.username_filter.text().lower()

        total_users = admins_count = 0
        last_user = "-"

        if users:
            for user in users:
                user_id, username, email, is_admin, created_at = user
                role_str = "admin" if is_admin else "user"

                if selected_role != "All" and role_str != selected_role:
                    continue
                if username_filter_text and username_filter_text not in username.lower():
                    continue

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(user_id)))
                self.table.setItem(row, 1, QTableWidgetItem(username))
                self.table.setItem(row, 2, QTableWidgetItem(email))
                self.table.setItem(row, 3, QTableWidgetItem("Admin" if is_admin else "Not admin"))
                self.table.setItem(row, 4, QTableWidgetItem(str(created_at)))

                # Add Delete button in Action column
                btn_delete = QPushButton("Delete")
                btn_delete.setStyleSheet("background-color: #dc3545; color: white;")
                btn_delete.clicked.connect(partial(self.delete_user, user_id=user_id))
                self.table.setCellWidget(row, 5, btn_delete)

                total_users += 1
                if is_admin:
                    admins_count += 1
                last_user = username

        self.total_users.value_label.setText(str(total_users))
        self.admins.value_label.setText(str(admins_count))
        self.last_user.value_label.setText(last_user)
        
    def delete_user(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this user?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                delete_user_by_id(user_id)
                QMessageBox.information(self, "Deleted", "User deleted successfully.")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user:\n{str(e)}")

    def add_user(self):
        from ui.user.dialog_add_user import AddUserDialog
        dialog = AddUserDialog(self)
        if dialog.exec_():
            self.load_users()

    def export_pdf_report(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Export Failed", "No data to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not filepath:
            return
        if not filepath.endswith(".pdf"):
            filepath += ".pdf"

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # --- Title and Timestamp ---
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "User Report")

        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by: {self.user['username']}")

        y = height - 100

        # --- Stat cards ---
        kpis = [
            self.total_users,
            self.admins,
            self.last_user,
        ]
        for card in kpis:
            title = card.layout().itemAt(1).widget().text()
            value = card.value_label.text()
            c.drawString(50, y, f"{title}: {value}")
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 50

        c.showPage()

        # --- Table Headers + Data ---
        headers = ["ID", "Username", "Email", "Role", "Created At"]
        data = [headers]

        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(5):  # Skip "Action"
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # --- Paginate table ---
        rows_per_page = 25
        for i in range(0, len(data), rows_per_page):
            page_data = data[i:i + rows_per_page]
            table = Table(page_data, repeatRows=1, colWidths=[60, 100, 150, 80, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ]))
            w, h = table.wrapOn(c, width - 80, height)
            table.drawOn(c, 40, height - h - 50)
            c.showPage()

        c.save()
        QMessageBox.information(self, "Export Successful", f"PDF report saved to:\n{filepath}")
