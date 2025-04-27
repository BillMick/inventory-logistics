from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QMessageBox,
    QTableWidgetItem, QLabel, QLineEdit, QFrame, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.manager import fetch_all_clients, delete_client_by_id
from functools import partial


class ClientDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Management Dashboard")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- Stats Section ---
        stats_layout = QHBoxLayout()
        self.total_clients = self.create_stat_card("Total Clients", "0")
        self.latest_client = self.create_stat_card("Last Client", "-")

        stats_layout.addWidget(self.total_clients)
        stats_layout.addWidget(self.latest_client)
        layout.addLayout(stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Top Controls ---
        filter_layout = QHBoxLayout()

        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Filter by name...")
        self.name_filter.textChanged.connect(self.load_clients)

        btn_add = QPushButton("Add Client")
        btn_add.clicked.connect(self.add_client)
        btn_add.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_clients)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")

        btn_quit = QPushButton("Quit")
        btn_quit.clicked.connect(self.close)
        btn_quit.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")

        filter_layout.addWidget(self.name_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Fiscal ID", "Contact", "Email", "Created At", "Action"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.edit_client)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_clients()

    def create_stat_card(self, title, value, color="#007bff"):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #6c757d;")

        layout.addWidget(value_label)
        layout.addWidget(title_label)
        frame.setLayout(layout)
        frame.value_label = value_label
        return frame

    def horizontal_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #ced4da;")
        return line

    def load_clients(self):
        self.table.setRowCount(0)
        clients = fetch_all_clients()
        filter_text = self.name_filter.text().lower()

        total = 0
        last_name = "-"

        for client in clients:
            client_id, name, fiscal_id, contact, email, address, created_at = client
            if filter_text and filter_text not in name.lower():
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(client_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(fiscal_id))
            self.table.setItem(row, 3, QTableWidgetItem(contact or ""))
            self.table.setItem(row, 4, QTableWidgetItem(email or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(created_at)))

            total += 1
            last_name = name
            # Add Delete button in Action column
            btn_delete = QPushButton("Delete")
            btn_delete.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
            btn_delete.clicked.connect(partial(self.delete_client, client_id=client_id))
            self.table.setCellWidget(row, 6, btn_delete)

        self.total_clients.value_label.setText(str(total))
        self.latest_client.value_label.setText(last_name)

    def add_client(self):
        from ui.client.dialog_add_client import AddClientDialog
        dialog = AddClientDialog(self)
        if dialog.exec_():
            self.load_clients()
            
    def delete_client(self, client_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this client?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                delete_client_by_id(client_id)
                QMessageBox.information(self, "Deleted", "Client deleted successfully.")
                self.load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete client:\n{str(e)}")

    def edit_client(self, row, column):
        client_data = {
            "id": int(self.table.item(row, 0).text()),
            "name": self.table.item(row, 1).text(),
            "fiscal_id": self.table.item(row, 2).text(),
            "contact": self.table.item(row, 3).text(),
            "email": self.table.item(row, 4).text(),
        }

        from ui.client.dialog_update_client import UpdateClientDialog
        dialog = UpdateClientDialog(self, client_data)
        if dialog.exec_():
            self.load_clients()