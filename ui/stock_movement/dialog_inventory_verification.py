from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd
from db.manager import fetch_all_products, get_theoretical_stock

class InventoryVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Verification")
        self.resize(800, 600)

        self.products = fetch_all_products()
        self.table = QTableWidget()
        self.table.setRowCount(len(self.products))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Product", "Theoretical Qty", "Actual Qty", "Discrepancy"])

        for row, product in enumerate(self.products):
            product_name = product[1]
            theoretical_qty = get_theoretical_stock(product[0])

            self.table.setItem(row, 0, QTableWidgetItem(product_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(theoretical_qty)))

            actual_qty_input = QLineEdit()
            actual_qty_input.setPlaceholderText("Enter actual qty")
            actual_qty_input.textChanged.connect(lambda _, r=row: self.update_discrepancy(r))
            self.table.setCellWidget(row, 2, actual_qty_input)
            self.table.setItem(row, 3, QTableWidgetItem(""))

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        # Export buttons
        btn_layout = QHBoxLayout()
        btn_export_pdf = QPushButton("Export to PDF")
        btn_export_pdf.clicked.connect(self.export_pdf)
        btn_export_excel = QPushButton("Export to Excel")
        btn_export_excel.clicked.connect(self.export_excel)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(btn_export_pdf)
        btn_layout.addWidget(btn_export_excel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_discrepancy(self, row):
        try:
            theoretical = int(self.table.item(row, 1).text())
            actual_input = self.table.cellWidget(row, 2)
            actual = int(actual_input.text())
            discrepancy = actual - theoretical

            item = QTableWidgetItem(str(discrepancy))
            if discrepancy == 0:
                item.setBackground(QColor('lightgreen'))
            else:
                item.setBackground(QColor('lightcoral'))
            self.table.setItem(row, 3, item)
        except ValueError:
            item = QTableWidgetItem("Invalid")
            item.setBackground(QColor('khaki'))
            self.table.setItem(row, 3, item)

    def export_excel(self):
        from datetime import datetime
        data = []
        for row in range(self.table.rowCount()):
            product = self.table.item(row, 0).text()
            theoretical = self.table.item(row, 1).text()
            actual_widget = self.table.cellWidget(row, 2)
            actual = actual_widget.text() if actual_widget else ""
            discrepancy = self.table.item(row, 3).text()
            data.append([product, theoretical, actual, discrepancy])

        # Prompt for save location
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if filepath:
            if not filepath.endswith(".xlsx"):
                filepath += ".xlsx"
            
            try:
                # Add date, time as metadata at the top
                # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Create a DataFrame for the data
                df = pd.DataFrame(data, columns=["Product", "Theoretical Qty", "Actual Qty", "Discrepancy"])

                # Add the metadata row as the first row of the dataframe
                # metadata = pd.DataFrame({
                #     # "Product": ["Generated on:", timestamp],
                #     "Actual Qty": [""],
                #     "Discrepancy": [""]
                # })
                df = pd.concat([df], ignore_index=True)

                # Write the DataFrame to Excel
                df.to_excel(filepath, index=False)
                QMessageBox.information(self, "Export Successful", f"Excel file saved to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")




    def export_pdf(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from PyQt5.QtWidgets import QFileDialog
        from datetime import datetime
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PDF Files (*.pdf)")
        if filepath:
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"

            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            y = height - 50

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, y, "Inventory Verification Report")

            # Timestamp
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            y -= 60
            c.setFont("Helvetica", 12)
            headers = ["Product", "Theoretical Qty", "Actual Qty", "Discrepancy"]
            col_widths = [200, 100, 100, 100]

            # Draw headers
            for i, header in enumerate(headers):
                c.drawString(40 + sum(col_widths[:i]), y, header)

            y -= 20
            c.setFont("Helvetica", 10)

            # Table content
            for row in range(self.table.rowCount()):
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 10)

                product = self.table.item(row, 0).text()
                theoretical = self.table.item(row, 1).text()
                actual_widget = self.table.cellWidget(row, 2)
                actual = actual_widget.text() if actual_widget else ""
                discrepancy = self.table.item(row, 3).text()

                row_data = [product, theoretical, actual, discrepancy]
                for i, cell in enumerate(row_data):
                    c.drawString(40 + sum(col_widths[:i]), y, str(cell))
                y -= 20

            c.save()
            QMessageBox.information(self, "Export Successful", f"PDF report saved to:\n{filepath}")
            

