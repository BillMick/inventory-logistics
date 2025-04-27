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

        # Validate data before plotting
        if not data or all(value == 0 for value in data.values()):
            self.ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        transform=self.ax.transAxes)
            self.canvas.draw()
            return
        else:
            products = list(data.keys())
            values = list(data.values())

            self.ax.bar(products, values, color="#3498db")
            self.ax.set_title(title)
            self.ax.set_ylabel("Quantité")            
            self.ax.set_xticks(range(len(products)))  # Ensure alignment
            self.ax.set_xticklabels(products, rotation=45, ha='right')
            self.ax.grid()

        self.canvas.draw()
