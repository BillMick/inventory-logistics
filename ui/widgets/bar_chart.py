from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BarChartWidget(QWidget):
    def __init__(self, data, title):
        super().__init__()
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot(data, title)

    def plot(self, data, title):
        self.ax.clear()
        products = list(data.keys())
        values = list(data.values())

        self.ax.bar(products, values, color="#3498db")
        self.ax.set_title(title)
        self.ax.set_ylabel("Quantity")
        self.ax.set_xticklabels(products, rotation=45, ha='right')
        self.ax.grid()

        self.canvas.draw()
