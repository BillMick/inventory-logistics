# ui/widgets/pie_chart.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PieChartWidget(QWidget):
    def __init__(self, data, title="Statistics"):
        super().__init__()
        layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot(data, title)

    def plot(self, data, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        labels = list(data.keys())
        sizes = list(data.values())
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title(title)
        ax.axis('equal')  # Equal aspect ratio
        self.canvas.draw()
