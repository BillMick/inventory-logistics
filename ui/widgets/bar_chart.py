from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

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
        self.ax.clear()  # Clear any previous data/plot

        # Validate and clean data (remove NaN or Inf values)
        if not data or all(value == 0 for value in data.values()):
            print("Warning: Data is empty or contains only zero values.")
            return

        # Ensure there are no NaN or Inf values in the data
        products = list(data.keys())
        values = list(data.values())

        # Remove invalid values (NaN, Inf)
        valid_data = [(product, value) for product, value in zip(products, values) if not np.isnan(value) and not np.isinf(value)]

        if not valid_data:
            print("Warning: No valid data available to plot.")
            return

        valid_products, valid_values = zip(*valid_data)

        # Plot the bar chart
        bars = self.ax.bar(valid_products, valid_values, color="#3498db")

        # Setting title and labels
        self.ax.set_title(title)
        self.ax.set_ylabel("Quantity")
        self.ax.set_xlabel("Products")

        # Explicitly set xticks to match the position of the bar labels
        self.ax.set_xticks(range(len(valid_products)))

        # Set the labels with rotation
        self.ax.set_xticklabels(valid_products, rotation=45, ha='right')

        # Enable grid for easier readability
        self.ax.grid(True)

        # Manually set axis limits (to prevent NaN/Inf issues)
        min_value = min(valid_values)
        max_value = max(valid_values)
        if min_value == max_value:
            min_value -= 1  # To prevent zero-length axis range
            max_value += 1

        self.ax.set_ylim(min_value, max_value)

        # Redraw the canvas with the new plot
        self.canvas.draw()
