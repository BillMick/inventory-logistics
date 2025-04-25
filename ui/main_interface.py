from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QStackedWidget, QStyle, QSizePolicy,
    QGridLayout
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, Qt
from PyQt5.QtGui import QFont, QPainter
from ui.widgets.pie_chart import PieChartWidget
from ui.widgets.bar_chart import BarChartWidget
from db.manager import fetch_all_stock_movements, fetch_product_stats
from ui.product.dashboard_product import ProductDashboard
from ui.stock_movement.dashboard_stock_movement import StockMovementDashboard
from ui.user.dashboard_user import UserDashboard
from ui.supplier.dashboard_supplier import SupplierDashboard

class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(600)
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Inventory Dashboard")
        self.showMaximized()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # --- Menu Bar ---
        icons = {
            "Dashboard": self.style().standardIcon(QStyle.SP_ComputerIcon),
            "Movements": self.style().standardIcon(QStyle.SP_FileDialogContentsView),
            "Products": self.style().standardIcon(QStyle.SP_DirIcon),
            "Users": self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
            "Suppliers": self.style().standardIcon(QStyle.SP_DriveNetIcon),
        }

        menu_layout = QHBoxLayout()
        for i, name in enumerate(["Dashboard", "Movements", "Products", "Users", "Suppliers"]):
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
                
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 6px;")
        quit_btn.clicked.connect(self.close)
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

        # Add all KPI cards to layout
        cards = [
            self.total_movements_card, self.in_card, self.out_card, self.total_products_card,
            self.total_stock_card, self.below_threshold_card, self.out_of_stock_card
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
        self.top_products_chart = BarChartWidget({}, "Top Products")

        charts_layout.addWidget(self.movement_chart)
        charts_layout.addWidget(self.top_products_chart)

        dashboard_layout.addLayout(charts_layout)
        self.dashboard_page.setLayout(dashboard_layout)

        # --- Add Pages to Stack ---
        self.stack.addWidget(self.dashboard_page)            # index 0
        self.stack.addWidget(StockMovementDashboard())       # index 1
        self.stack.addWidget(ProductDashboard())             # index 2
        self.stack.addWidget(UserDashboard())                # index 3
        self.stack.addWidget(SupplierDashboard())            # index 4

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
        movements = fetch_all_stock_movements()
        stats = fetch_product_stats()

        in_count = sum(1 for m in movements if m[2] == "IN")
        out_count = sum(1 for m in movements if m[2] == "OUT")

        total_movements = len(movements)
        total_products = stats.get("total_products", 0)

        # Set movement KPIs
        self.total_movements_card.value_label.setText(str(len(movements)))
        self.in_card.value_label.setText(str(in_count))
        self.out_card.value_label.setText(str(out_count))

        # Set product KPIs
        self.total_products_card.value_label.setText(str(stats.get("total_products", 0)))
        self.total_stock_card.value_label.setText(str(stats.get("total_stock", 0)))
        self.below_threshold_card.value_label.setText(str(stats.get("below_threshold", 0)))
        self.out_of_stock_card.value_label.setText(str(stats.get("out_of_stock", 0)))

        # Update charts
        self.movement_chart.plot({"IN": in_count, "OUT": out_count}, "Stock Movement Distribution")
        self.top_products_chart.plot(stats.get("top_products", {}), "Top Products")