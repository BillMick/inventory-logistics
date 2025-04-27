from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QMessageBox,
    QTableWidgetItem, QLabel, QLineEdit, QFrame, QSizePolicy, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.manager import fetch_all_suppliers, delete_supplier_by_id, insert_supplier
from functools import partial
import pandas as pd

class SupplierDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Fournisseur")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- Stats Section ---
        stats_layout = QHBoxLayout()
        self.total_suppliers = self.create_stat_card("Fournisseur Total", "0")
        self.latest_supplier = self.create_stat_card("Récent Fournisseur", "-")

        stats_layout.addWidget(self.total_suppliers)
        stats_layout.addWidget(self.latest_supplier)
        layout.addLayout(stats_layout)
        layout.addWidget(self.horizontal_line())

        # --- Top Controls ---
        filter_layout = QHBoxLayout()

        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Filtrer par nom...")
        self.name_filter.textChanged.connect(self.load_suppliers)

        btn_add = QPushButton("Ajouter Fournisseur")
        btn_add.clicked.connect(self.add_supplier)
        btn_add.setStyleSheet("background-color: #007bff; color: white")
        
        btn_import = QPushButton("Importer Excel")
        btn_import.clicked.connect(self.import_suppliers_from_excel)
        btn_import.setStyleSheet("background-color: #20c997; color: white")
        
        btn_export = QPushButton("Exporter Excel")
        btn_export.clicked.connect(self.export_suppliers_to_excel)
        btn_export.setStyleSheet("background-color: #28a745; color: white")
        
        btn_export_pdf = QPushButton("Exporter PDF")
        btn_export_pdf.setStyleSheet("background-color: #6c757d; color: white")
        btn_export_pdf.clicked.connect(self.export_pdf_report)


        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.load_suppliers)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white")

        btn_quit = QPushButton("Fermer")
        btn_quit.clicked.connect(self.close)
        btn_quit.setStyleSheet("background-color: #dc3545; color: white")

        filter_layout.addWidget(self.name_filter)
        filter_layout.addWidget(btn_add)
        filter_layout.addWidget(btn_import)
        filter_layout.addWidget(btn_export)
        filter_layout.addWidget(btn_export_pdf)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_quit)

        layout.addLayout(filter_layout)
        layout.addWidget(self.horizontal_line())

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "ID Fiscal", "Contact", "Email", "Adresse" , "Ajouté le", "Action"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.edit_supplier)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_suppliers()

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

    def load_suppliers(self):
        self.table.setRowCount(0)
        suppliers = fetch_all_suppliers()
        filter_text = self.name_filter.text().lower()

        total = 0
        last_name = "-"

        for supplier in suppliers:
            supplier_id, name, fiscal_id, contact, email, address, created_at = supplier
            if filter_text and filter_text not in name.lower():
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier_id)))
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
            btn_delete.clicked.connect(partial(self.delete_supplier, supplier_id=supplier_id))
            self.table.setCellWidget(row, 7, btn_delete)

        self.total_suppliers.value_label.setText(str(total))
        self.latest_supplier.value_label.setText(last_name)

    def add_supplier(self):
        from ui.supplier.dialog_add_supplier import AddSupplierDialog
        dialog = AddSupplierDialog(self)
        if dialog.exec_():
            self.load_suppliers()
            
    def delete_supplier(self, supplier_id):
        confirm = QMessageBox.question(
            self,
            "Confirmer la Suppression",
            "Êtes-vous sûr de vouloir supprimer ce fournisseur ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                delete_supplier_by_id(supplier_id)
                QMessageBox.information(self, "Suppression", "Fournisseur supprimé.")
                self.load_suppliers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Echec de suppression du fournisseur:\n{str(e)}")

    def edit_supplier(self, row, column):
        supplier_data = {
            "id": int(self.table.item(row, 0).text()),
            "name": self.table.item(row, 1).text(),
            "fiscal_id": self.table.item(row, 2).text(),
            "contact": self.table.item(row, 3).text(),
            "email": self.table.item(row, 4).text(),
            "address": self.table.item(row, 5).text(),
        }

        from ui.supplier.dialog_update_supplier import UpdateSupplierDialog
        dialog = UpdateSupplierDialog(self, supplier_data)
        if dialog.exec_():
            self.load_suppliers()
            
    def export_pdf_report(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Echec de l'exportation", "Pas de données fournisseur à exporter.")
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
        c.drawCentredString(width / 2, height - 50, "Rapport Fournisseur")

        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y = height - 100

        # --- Stat cards ---
        kpis = [
            self.total_suppliers,
            self.latest_supplier,
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
        QMessageBox.information(self, "Exportation réussie", f"{filepath} enregistré")

    def import_suppliers_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir fichier Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            df = pd.read_excel(file_path)

            # Make sure the required columns exist in the file
            required_columns = ["Nom", "ID Fiscal", "Contact", "Email", "Adresse"]
            if not all(col in df.columns for col in required_columns):
                QMessageBox.warning(self, "Fichier invalide", "Structure nom respectée.")
                return

            # Insert each supplier into the database
            for _, row in df.iterrows():
                name = row["Nom"]
                fiscal_id = row["ID Fiscal"]
                contact = row["Contact"]
                email = row["Email"]
                address = row["Adresse"]
                
                # Insert supplier into the database
                insert_supplier(name, fiscal_id, contact, email, address)
            
            # Reload the supplier list after import
            self.load_suppliers()
            QMessageBox.information(self, "Importation réussie", "Fournisseurs importés.")
        
        except Exception as e:
            QMessageBox.critical(self, "Echec d'importation", f"Erreur:\n{str(e)}")
            
    def export_suppliers_to_excel(self):
        # Get the suppliers data from the table
        suppliers_data = []
        for row in range(self.table.rowCount()):
            supplier_id = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            fiscal_id = self.table.item(row, 2).text()
            contact = self.table.item(row, 3).text()
            email = self.table.item(row, 4).text()
            address = self.table.item(row, 5).text()
            created_at = self.table.item(row, 6).text()

            suppliers_data.append([supplier_id, name, fiscal_id, contact, email, address, created_at])
        
        if not suppliers_data:
            QMessageBox.warning(self, "Echec de l'exportation", "Pas de données fournisseur à exporter.")
            return

        # Open a save file dialog to select the destination for the Excel file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        # Create a DataFrame and save it to an Excel file
        try:
            df = pd.DataFrame(suppliers_data, columns=["ID", "Nom", "ID Fiscal", "Contact", "Email", "Adresse" ,"Ajouté le"])
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Exportation réussie", f"{file_path} enregistré")
        except Exception as e:
            QMessageBox.critical(self, "Echec de l'exportation", f"Erreur:\n{str(e)}")