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
        # Restrict df columns to features of interest
        self.df = self.df[self.features]

        # Ensure we have sorted group labels
        self.group_labels = sorted(self.group_labels)

        # Create a dict that maps each group_label to its mean values (by column)
        group_val_dict = {}
        for label in self.group_labels:
            group_val_dict[label] = self.df[self.metadata[self.group_column] == label].mean(axis=0)

        # x-axis positions: one position per feature
        x = np.arange(len(self.features))

        # Number of groups (e.g. 3 groups)
        n_groups = len(self.group_labels)

        # Choose a total group width;
        # we divide it by the number of groups to get each bar width
        total_bar_width = 0.8
        bar_width = total_bar_width / n_groups

        ax = self.figure.add_subplot(111)

        # Plot each category with a distinct offset
        for i, label in enumerate(self.group_labels):
            # Calculate offset for this group
            # Example: if there are 3 groups, i in [0,1,2]
            # we shift them by -1*bar_width, 0, +1*bar_width (centered around x)
            offset = (i - (n_groups - 1) / 2.0) * bar_width

            # Retrieve the mean values for this category
            vals = group_val_dict[label]

            # Plot bars for this category
            ax.bar(x + offset, vals, bar_width, label=label)

        # Labeling and formatting
        ax.set_ylabel('Species Presence')
        ax.set_title('Presence of Selected Species')
        ax.set_xticks(x)
        ax.set_xticklabels(self.features, rotation=45, ha='right')
        ax.legend()

        # Tight layout to prevent label overlap
        self.figure.tight_layout()

        # Redraw
        self.canvas.draw()

