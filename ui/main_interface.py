from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget, QStyle
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtCore import Qt
from ui.widgets.pie_chart import PieChartWidget
from ui.widgets.bar_chart import BarChartWidget
from db.manager import fetch_all_stock_movements, fetch_product_stats
from ui.product_dashboard import ProductDashboard
from ui.stock_movement_dashboard import StockMovementDashboard

class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(2000)  # smoother, faster
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

        # --- Menu Bar (Always Visible) ---
        icons = {
            "Dashboard": self.style().standardIcon(QStyle.SP_ComputerIcon),
            "Movements": self.style().standardIcon(QStyle.SP_FileDialogContentsView),
            "Products": self.style().standardIcon(QStyle.SP_DirIcon),
            "Settings": self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
        }
        menu_layout = QHBoxLayout()
        for i, name in enumerate(["Dashboard", "Movements", "Products", "Settings"]):
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
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 6px;")
        quit_btn.clicked.connect(self.close)
        menu_layout.addWidget(quit_btn)

        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.hr())

        # --- Stack Pages (Dashboard, Movements, Products) ---
        self.stack = FadeStackedWidget()

        # Dashboard Page
        self.dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout()

        # --- Stats Section ---
        stats_layout = QHBoxLayout()
        self.stats_labels = {}
        for label in ["Total Movements", "IN", "OUT", "Total Products"]:
            lbl = QLabel(f"{label}: 0")
            lbl.setFont(QFont("Arial", 12, QFont.Bold))
            lbl.setStyleSheet("padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; border-radius: 8px;")
            self.stats_labels[label] = lbl
            stats_layout.addWidget(lbl)

        dashboard_layout.addLayout(stats_layout)
        dashboard_layout.addWidget(self.hr())

        # --- Charts Section ---
        charts_layout = QHBoxLayout()
        self.movement_chart = PieChartWidget({}, "Stock Movement Distribution")
        self.top_products_chart = BarChartWidget({}, "Top Products")
        charts_layout.addWidget(self.movement_chart)
        charts_layout.addWidget(self.top_products_chart)

        dashboard_layout.addLayout(charts_layout)
        self.dashboard_page.setLayout(dashboard_layout)

        # Add pages to stack
        self.stack.addWidget(self.dashboard_page)            # index 0
        self.stack.addWidget(StockMovementDashboard())       # index 1
        self.stack.addWidget(ProductDashboard())             # index 2

        # Add stack to main layout
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        # Populate dashboard initially
        self.update_dashboard()


    def hr(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: gray;")
        return line

    def update_dashboard(self):
        movements = fetch_all_stock_movements()
        stats = fetch_product_stats()

        in_count = sum(1 for m in movements if m[2] == "IN")
        out_count = sum(1 for m in movements if m[2] == "OUT")

        self.stats_labels["Total Movements"].setText(f"Total Movements: {len(movements)}")
        self.stats_labels["IN"].setText(f"IN: {in_count}")
        self.stats_labels["OUT"].setText(f"OUT: {out_count}")
        self.stats_labels["Total Products"].setText(f"Total Products: {stats.get('total_products', 0)}")

        self.movement_chart.plot({"IN": in_count, "OUT": out_count}, "Stock Movement Distribution")
        self.top_products_chart.plot(stats.get("top_products", {}), "Top Products")
