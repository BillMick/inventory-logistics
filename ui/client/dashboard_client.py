from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QMessageBox,
    QTableWidgetItem, QLabel, QLineEdit, QFrame, QSizePolicy, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.manager import fetch_all_clients, delete_client_by_id, insert_client
from functools import partial
import pandas as pd


class ClientDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Clients")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- Stats Section ---
        stats_layout = QHBoxLayout()
        self.total_clients = self.create_stat_card("Total Clients", "0")
        self.latest_client = self.create_stat_card("Plus récent Client", "-")

        stats_layout.addWidget(self.total_clients)
        stats_layout.addWidget(self.latest_client)
        layout.addLayout(stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Top Controls ---
        filter_layout = QHBoxLayout()

        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Trier par nom...")
        self.name_filter.textChanged.connect(self.load_clients)

        btn_add = QPushButton("Ajouter Client")
        btn_add.clicked.connect(self.add_client)
        btn_add.setStyleSheet("background-color: #007bff; color: white")

        btn_import_excel = QPushButton("Importer Excel")
        btn_import_excel.setStyleSheet("background-color: #20c997; color: white")
        btn_import_excel.clicked.connect(self.import_from_excel)
        
        btn_export_excel = QPushButton("Exporter Excel")
        btn_export_excel.setStyleSheet("background-color: #28a745; color: white")
        btn_export_excel.clicked.connect(self.export_to_excel)
        
        btn_export_pdf = QPushButton("Exporter PDF")
        btn_export_pdf.setStyleSheet("background-color: #6c757d; color: white")
        btn_export_pdf.clicked.connect(self.export_pdf_report)

        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.load_clients)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white")

        btn_quit = QPushButton("Fermer")
        btn_quit.clicked.connect(self.close)
        btn_quit.setStyleSheet("background-color: #dc3545; color: white")

        filter_layout.addWidget(self.name_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_import_excel)
        filter_layout.addWidget(btn_export_excel)
        filter_layout.addWidget(btn_export_pdf)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "ID Fiscal", "Contact", "Email", "Adresse", "Ajouté le", "Action"])
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
            self.table.setItem(row, 5, QTableWidgetItem(address or ""))
            self.table.setItem(row, 6, QTableWidgetItem(str(created_at)))

            total += 1
            last_name = name
            # Add Delete button in Action column
            btn_delete = QPushButton("Supprimer")
            btn_delete.setStyleSheet("background-color: #dc3545; color: white")
            btn_delete.clicked.connect(partial(self.delete_client, client_id=client_id))
            self.table.setCellWidget(row, 7, btn_delete)

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
            "Confirmation de la suppression",
            "Êtes-vous sûr de vouloir supprimer ce client?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                delete_client_by_id(client_id)
                QMessageBox.information(self, "Suppression", "Client supprimé.")
                self.load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Echec de suppression de ce client:\n{str(e)}")

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
  
    def export_pdf_report(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Echec de l'exportation", "Pas de données client à exporter.")
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "Enregistrer PDF", "", "PDF Files (*.pdf)")
        if not filepath:
            return
        if not filepath.endswith(".pdf"):
            filepath += ".pdf"

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # --- Title and Timestamp ---
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "Client Report")

        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


        y = height - 100

        # --- Stat Cards ---
        stats = [
            self.total_clients,
            self.latest_client
        ]
        for stat in stats:
            title = stat.layout().itemAt(1).widget().text()
            value = stat.value_label.text()
            c.drawString(50, y, f"{title}: {value}")
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 50

        c.showPage()

        # --- Table Data ---
        headers = ["ID", "Nom", "ID Fiscal", "Contact", "Email", "Ajouté le"]
        data = [headers]

        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(6):  # Exclude Action column
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        rows_per_page = 25
        for i in range(0, len(data), rows_per_page):
            page_data = data[i:i + rows_per_page]
            table = Table(page_data, repeatRows=1, colWidths=[40, 100, 80, 80, 120, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
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

    def export_to_excel(self):
        """Export clients data to an Excel file."""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Echec de l'exportation", "Pas de données client à exporter.")
            return

        # Create a list of dictionaries for each row
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            row_data["ID"] = self.table.item(row, 0).text()
            row_data["Nom"] = self.table.item(row, 1).text()
            row_data["ID Fiscal"] = self.table.item(row, 2).text()
            row_data["Contact"] = self.table.item(row, 3).text()
            row_data["Email"] = self.table.item(row, 4).text()
            row_data["Adresse"] = self.table.item(row, 5).text()
            row_data["Ajouté le"] = self.table.item(row, 6).text()
            data.append(row_data)

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)

        # Open file dialog to save the Excel file
        filepath, _ = QFileDialog.getSaveFileName(self, "Sauvegarder Excel", "", "Excel Files (*.xlsx)")
        if not filepath:
            return
        if not filepath.endswith(".xlsx"):
            filepath += ".xlsx"

        try:
            df.to_excel(filepath, index=False)
            QMessageBox.information(self, "Exportation réussie", f"{filepath} enregistré.")
        except Exception as e:
            QMessageBox.critical(self, "Echec de l'exportation", f"Erreur: {e}")

    def import_from_excel(self):
        """Import clients data from an Excel file."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Excel", "", "Excel Files (*.xlsx)")
        if not filepath:
            return

        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(filepath)

            # Ensure the required columns are in the file
            required_columns = ["Nom", "ID Fiscal", "Contact", "Email", "Adresse"]
            if not all(col in df.columns for col in required_columns):
                QMessageBox.warning(self, "Importation échouée", "Tous les champs sont requis.")
                return

            # Insert each client into the database
            for _, row in df.iterrows():
                name = row["Nom"]
                fiscal_id = row["ID Fiscal"]
                contact = row["Contact"]
                email = row["Email"]
                address = row["Adresse"]
                
                insert_client(name, fiscal_id, contact, email, address)
            
            # Reload the clients list after import
            self.load_clients()
            QMessageBox.information(self, "Importation réussie", f"Données importées de:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Importation échouée", f"error: {e}")