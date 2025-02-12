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



# If you want to run this file alone to test, uncomment the following:
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     # Sample data
#     data = {
#         'group':  ['GroupA','GroupA','GroupA','GroupB','GroupB','GroupB'],
#         'Feat1':  [10,  5,  7,  2,  9,  3],
#         'Feat2':  [4,   8,  3,  10, 6,  1],
#         'Feat3':  [7,   2,  9,   3, 8,  5]
#     }
#     df_sample = pd.DataFrame(data)
#
#     features = ['Feat1', 'Feat2', 'Feat3']
#     group_labels = ['GroupA', 'GroupB']
#
#     popup = GroupedBarPlotPopUp(df_sample, features, group_labels)
#     popup.exec_()  # or popup.show()
#     sys.exit(app.exec_())

# def plot_bar_chart(self):
#     ax = self.figure.add_subplot(111)
#
#     # Prepare the X-axis positions for each feature
#     x = np.arange(len(self.features))
#     bar_width = 0.35
#
#     current_abundance_df = self.df[self.features]
#     richness_df = current_abundance_df.apply(lambda x: x.sum(), axis=1)
#     data = pd.concat([richness_df.rename('richness'), self.metadata], axis=1)
#
#     # TODO, Fix the output column label
#     GroupA_data = data[data['study_condition'] == self.group_labels[0]]['richness']
#     GroupB_data = data[data['study_condition'] != self.group_labels[1]]['richness']
#
#     # Create the bars for each group
#     ax.bar(
#         x - bar_width / 2,
#         GroupA_data,
#         bar_width,
#         label=self.group_labels[0],
#         color='steelblue'
#     )
#     ax.bar(
#         x + bar_width / 2,
#         GroupB_data,
#         bar_width,
#         label=self.group_labels[1],
#         color='orange'
#     )
#
#     # Set X-axis tick positions and labels
#     ax.set_xticks(x)
#     ax.set_xticklabels(self.features)
#
#     # Labeling
#     ax.set_xlabel("Features")
#     ax.set_ylabel("Richness")
#     ax.legend()
#
#     # Refresh the canvas
#     self.canvas.draw()
