import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout
import seaborn as sns
from PyQt5.QtWidgets import QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GroupedBarPlotPopUp(QDialog):
    def __init__(self, df, metadata, features, group_labels, group_column, parent=None):
        super().__init__(parent)
        self.df = df
        self.df = (self.df > 0).astype(int)
        self.metadata = metadata
        self.features = features
        self.group_labels = group_labels
        self.group_column = group_column[0]

        # Configure dialog properties
        self.setWindowTitle("Best species combination")
        self.resize(800, 600)

        # Create layout for the dialog
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a matplotlib Figure and embed it in the Qt Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Plot the grouped bar chart
        self.plot_bar_chart()

    def plot_bar_chart(self):
        self.df = self.df[self.features]

        self.group_labels = sorted(self.group_labels)

        group_a = self.df[self.metadata[self.group_column] == self.group_labels[0]].mean(axis=0)
        group_b = self.df[self.metadata[self.group_column] == self.group_labels[1]].mean(axis=0)

        x = np.arange(len(self.features))  # the label locations
        width = 0.35  # the width of the bars

        ax = self.figure.add_subplot(111)
        rects1 = ax.bar(x - width / 2, group_a, width, label=self.group_labels[0])
        rects2 = ax.bar(x + width / 2, group_b, width, label=self.group_labels[1])

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Species Presence')
        ax.set_title(f'Presence of Selected Species')
        ax.set_xticks(x)
        ax.set_xticklabels(self.features, rotation=45, ha="right")  # Rotate x-axis labels for readability
        ax.legend()

        self.figure.tight_layout()

        # Redraw the canvas
        self.canvas.draw()

