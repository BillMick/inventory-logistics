from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QStackedWidget, QStyle, QSizePolicy,
    QGridLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, Qt
from PyQt5.QtGui import QFont, QPainter
from ui.widgets.pie_chart import PieChartWidget
from ui.widgets.bar_chart import BarChartWidget
from db.manager import fetch_all_stock_movements, fetch_product_stats, fetch_all_products_with_stock, fetch_all_clients, fetch_all_suppliers
from ui.product.dashboard_product import ProductDashboard
from ui.stock_movement.dashboard_stock_movement import StockMovementDashboard
from ui.user.dashboard_user import UserDashboard
from ui.supplier.dashboard_supplier import SupplierDashboard
from ui.client.dashboard_client import ClientDashboard

class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._target_index = None

    def setOpacity(self, opacity):
        self._opacity = opacity
        self.repaint()

    def getOpacity(self):
        return self._opacity

    opacity = pyqtProperty(float, fget=getOpacity, fset=setOpacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        super().paintEvent(event)
    
    def fadeToIndex(self, index):
        self._animation.stop()
        self._target_index = index
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)

        try:
            self._animation.finished.disconnect()
        except TypeError:
            pass

        def on_fade_out_finished():
            self.setCurrentIndex(self._target_index)
            self._animation.setStartValue(0.0)
            self._animation.setEndValue(1.0)
            self._animation.start()

        self._animation.finished.connect(on_fade_out_finished)
        self._animation.start()


class MainDashboard(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user  # Save the user info
        self.setWindowTitle(f"Main Inventory Dashboard - Logged in as {self.user['username']}")
        self.showMaximized()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        user_label = QLabel(f"Logged in as: {self.user['username']}")
        user_label.setAlignment(Qt.AlignRight)
        user_label.setStyleSheet("color: #6c757d; font-style: italic;")
        main_layout.addWidget(user_label)

        # --- Menu Bar ---
        icons = {
            "Dashboard": self.style().standardIcon(QStyle.SP_ComputerIcon),
            "Movements": self.style().standardIcon(QStyle.SP_FileDialogContentsView),
            "Products": self.style().standardIcon(QStyle.SP_DirIcon),
            "Suppliers": self.style().standardIcon(QStyle.SP_DriveNetIcon),
            "Clients": self.style().standardIcon(QStyle.SP_DirHomeIcon),
            "Users": self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
        }

        menu_layout = QHBoxLayout()
        for i, name in enumerate(["Dashboard", "Movements", "Products", "Suppliers", "Clients", "Users"]):
            if name == "Users" and not self.user.get("is_admin"):
                continue
            btn = QPushButton(icons[name], name)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1c5980;
                }
            """)
            if name == "Dashboard":
                btn.clicked.connect(lambda _, idx=0: self.stack.fadeToIndex(idx))
            elif name == "Movements":
                btn.clicked.connect(lambda _, idx=1: self.stack.fadeToIndex(idx))
            elif name == "Products":
                btn.clicked.connect(lambda _, idx=2: self.stack.fadeToIndex(idx))
            elif name == "Users":
                btn.clicked.connect(lambda _, idx=3: self.stack.fadeToIndex(idx))
            elif name == "Suppliers":
                btn.clicked.connect(lambda _, idx=4: self.stack.fadeToIndex(idx))
            elif name == "Clients":
                btn.clicked.connect(lambda _, idx=5: self.stack.fadeToIndex(idx))
                
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        btn_refresh = QPushButton("Main interface Refresh")
        btn_refresh.clicked.connect(self.update_dashboard)
        btn_refresh.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 16px; border-radius: 6px;")
        
        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 6px;")
        quit_btn.clicked.connect(self.close)
        
        btn_export_pdf = QPushButton("Export Report as PDF")
        btn_export_pdf.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px; border-radius: 6px;")
        btn_export_pdf.clicked.connect(self.export_pdf_report)
        
        menu_layout.addWidget(btn_export_pdf)
        menu_layout.addWidget(btn_refresh)
        menu_layout.addWidget(quit_btn)

        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.hr())

        # --- Stack Pages ---
        self.stack = FadeStackedWidget()

        # Dashboard Page
        self.dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setSpacing(15)

        # --- KPI Section (Now includes Product KPIs too) ---
        self.kpi_layout = QGridLayout()
        self.kpi_layout.setSpacing(10)

        self.total_movements_card = self.create_stat_card("Total Movements", "0", "#007bff")
        self.in_card = self.create_stat_card("IN", "0", "#28a745")
        self.out_card = self.create_stat_card("OUT", "0", "#dc3545")
        self.total_products_card = self.create_stat_card("Total Products", "0", "#17a2b8")

        self.total_stock_card = self.create_stat_card("Total Stock", "0", "#20c997")
        self.below_threshold_card = self.create_stat_card("Below Threshold", "0", "#ffc107")
        self.out_of_stock_card = self.create_stat_card("Out of Stock", "0", "#e74c3c")
        self.value_label_card = self.create_stat_card("Stock Value", "$0.00", "#6f42c1")
        self.total_suppliers_card = self.create_stat_card("Total Suppliers", "0", "#17a2b8")
        self.total_clients_card = self.create_stat_card("Total Clients", "0", "#17a2b8")

        # Add all KPI cards to layout
        cards = [
            self.total_movements_card, self.in_card, self.out_card, self.total_products_card,
            self.total_stock_card, self.below_threshold_card, self.out_of_stock_card, self.value_label_card,
            self.total_suppliers_card, self.total_clients_card
        ]

        for i, card in enumerate(cards):
            row = i // 4
            col = i % 4
            self.kpi_layout.addWidget(card, row, col)

        dashboard_layout.addLayout(self.kpi_layout)
        dashboard_layout.addWidget(self.hr())


        # --- Charts Section ---
        charts_layout = QHBoxLayout()
        self.movement_chart = PieChartWidget({}, "Stock Movement Distribution")
        self.evolution_chart = PieChartWidget({}, "Movement Category Distribution")
        self.top_products_chart = BarChartWidget({}, "Top Products")

        charts_layout.addWidget(self.movement_chart)
        charts_layout.addWidget(self.evolution_chart)
        charts_layout.addWidget(self.top_products_chart)

        dashboard_layout.addLayout(charts_layout)
        self.dashboard_page.setLayout(dashboard_layout)

        # --- Add Pages to Stack ---
        self.stack.addWidget(self.dashboard_page)            # index 0
        self.stack.addWidget(StockMovementDashboard())       # index 1
        self.stack.addWidget(ProductDashboard())             # index 2
        if self.user.get("is_admin"):
            self.stack.addWidget(UserDashboard())            # index 3
        else:
            self.stack.addWidget(QWidget())
        self.stack.addWidget(SupplierDashboard())            # index 4
        self.stack.addWidget(ClientDashboard())            # index 5

        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.update_dashboard()

    def hr(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #ced4da;")
        return line

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

    def update_dashboard(self):
        # Fetch data from the database
        movements = fetch_all_stock_movements()
        stats = fetch_product_stats()
        products = fetch_all_products_with_stock()
        inventory_value = 0.0
        suppliers = fetch_all_suppliers()
        clients = fetch_all_clients()

        # Compute movement stats
        in_count = sum(1 for m in movements if m[2] == "IN")
        out_count = sum(1 for m in movements if m[2] == "OUT")
        total_movements = len(movements)

        # Compute product stats with default fallback
        total_products = stats.get("total_products", 0)
        total_stock = stats.get("total_stock", 0)
        below_threshold = stats.get("below_threshold", 0)
        out_of_stock = stats.get("out_of_stock", 0)
        top_products = stats.get("top_products", {})
        
        incoming_count = sum(1 for m in movements if m[3] == "Incoming")
        back_count = sum(1 for m in movements if m[3] == "Back")
        delivery_count = sum(1 for m in movements if m[3] == "Delivery")
        restocking_count = sum(1 for m in movements if m[3] == "Restocking")
        
        for row_idx, product in enumerate(products):
            stock = product[8]
            price = float(product[5])
            inventory_value += stock * price

        # --- Update KPI cards ---
        self.total_movements_card.value_label.setText(str(total_movements))
        self.in_card.value_label.setText(str(in_count))
        self.out_card.value_label.setText(str(out_count))

        self.total_products_card.value_label.setText(str(total_products))
        self.total_stock_card.value_label.setText(str(total_stock))
        self.below_threshold_card.value_label.setText(str(below_threshold))
        self.out_of_stock_card.value_label.setText(str(out_of_stock))
        self.value_label_card.value_label.setText(f"${inventory_value:,.2f}")
        self.total_suppliers_card.value_label.setText(str(len(suppliers)))
        self.total_clients_card.value_label.setText(str(len(clients)))
        

        # --- Update charts ---
        self.movement_chart.plot(
            {"IN": in_count, "OUT": out_count},
            "Stock Movement Distribution"
        )
        self.top_products_chart.plot(
            top_products,
            "Top Products"
        )
        # --- Update Evolution Chart ---
        evolution_data = {
            "Incoming": incoming_count,
            "Back": back_count,
            "Delivery": delivery_count,
            "Restocking": restocking_count
        }

        self.evolution_chart.plot(
            evolution_data,
            "Label Evolution"
        )

    def export_pdf_report(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import tempfile
        from datetime import datetime
        import os

        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PDF Files (*.pdf)")
        if filepath:
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 50, "Inventory Dashboard Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y_pos = height - 120

        # KPI text
        kpis = [
            self.total_movements_card,
            self.in_card,
            self.out_card,
            self.total_products_card,
            self.total_stock_card,
            self.below_threshold_card,
            self.out_of_stock_card,
            self.value_label_card,
            self.total_suppliers_card,
            self.total_clients_card
        ]
        c.setFont("Helvetica", 10)
        for kpi in kpis:
            label = kpi.layout().itemAt(1).widget().text()
            value = kpi.value_label.text()
            c.drawString(50, y_pos, f"{label}: {value}")
            y_pos -= 15
            if y_pos < 100:
                c.showPage()
                y_pos = height - 50

        c.showPage()

        # --- Save Matplotlib Figures directly ---
        charts = [
            (self.movement_chart.figure, "Stock Movement Distribution"),
            (self.evolution_chart.figure, "Movement Category Distribution"),
            (self.top_products_chart.figure, "Top Products")
        ]

        for fig, title in charts:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                fig.savefig(tmp_file.name, bbox_inches='tight')
                c.drawString(50, height - 80, title)
                c.drawImage(tmp_file.name, 50, height / 2 - 100, width=500, height=250)
                c.showPage()
                os.unlink(tmp_file.name)
        c.save()
        print(f"PDF report saved as {filepath}")
        QMessageBox.information(self, "Export Successful", f"PDF report saved to:\n{filepath}")
        
