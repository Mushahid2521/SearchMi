import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout
import seaborn as sns
from PyQt5.QtWidgets import QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GroupedBarPlotPopUp(QDialog):
    def __init__(self, df, metadata, features, score, group_labels, group_column, parent=None):
        super().__init__(parent)
        self.df = df
        self.df = (self.df > 0).astype(int)
        self.metadata = metadata
        self.features = features
        self.score = score
        self.group_labels = group_labels
        self.group_column = group_column[0]

        # Configure dialog properties
        self.setWindowTitle("Best species combination")
        self.resize(1200, 1000)

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

        # Calculate richness for each sample (sum across columns)
        richness_series = self.df.sum(axis=1)

        # Ensure we have sorted group labels
        self.group_labels = sorted(self.group_labels)
        palette = sns.color_palette("Set2", n_colors=len(self.group_labels))

        df_with_group = self.df.copy()
        df_with_group['Group'] = self.metadata[self.group_column].values

        df_melted = df_with_group.melt(
            id_vars='Group',  # Keep the "Group" column as is
            var_name='Feature',  # New column name for old columns
            value_name='Presence'  # Values (the species presence/abundance)
        )
        print(df_melted.Presence.sum())

        richness_df = pd.DataFrame({
            'Group': self.metadata[self.group_column].values,
            'Richness': richness_series
        })

        self.figure.clear()
        ax1 = self.figure.add_subplot(2, 1, 1)
        ax2 = self.figure.add_subplot(2, 1, 2)

        plot1 = sns.barplot(
            data=df_melted,
            x='Feature',
            y='Presence',
            hue='Group',
            order=self.features,
            hue_order=self.group_labels,
            palette=palette,
            errorbar=None,
            ax=ax1
        )
        plot1.set_title('Presence of Selected Species by Group')
        plot1.set_xlabel('Species')
        plot1.set_ylabel('Mean Presence')
        # Rotate x-ticks
        plot1.set_xticklabels(plot1.get_xticklabels(), rotation=45, ha='right')
        plot1.legend(loc='best')

        plot2 = sns.barplot(
            data=richness_df,
            x='Group',
            y='Richness',
            order=self.group_labels,
            hue='Group',
            palette=palette,
            estimator=np.mean,
            errorbar='sd',
            ax=ax2
        )
        plot2.set_title('Average Richness by Group')
        plot2.set_xlabel(self.group_column)
        plot2.set_ylabel('Richness (Sum of Selected Features)')

        # Adjust layout and reduce gap
        self.figure.tight_layout(pad=1.0)
        # If it's still too large, try adjusting hspace:
        self.figure.subplots_adjust(hspace=1.3)

        self.canvas.draw()
