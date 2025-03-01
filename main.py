import sys
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QTableView,
    QVBoxLayout, QWidget, QStackedWidget, QPushButton
)

from DataProcessing import DataFile
from GeneticAlgorithm import GeneticAlgorithm
from GeneticAlgorithmPageWidget import GeneticAlgorithmPageWidget
from ImportPageWidget import ImportPageWidget
from PreprocessingPageWidget import PreprocessingPageWidget
from SearchSelectionPageWidget import SearchSelectionPageWidget
from SimulatedAnnealing import SimulatedAnnealing
from SimulatedAnnealingPageWidget import SimulatedAnnealingPageWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔎SearchMi")
        # Set a "regular" window size
        self.resize(800, 600)

        # Data files and interactions with the GA
        self.data_file = DataFile()
        self.ga_run_instance = GeneticAlgorithm()
        self.sa_run_instance = SimulatedAnnealing()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pages = {}

        # Add any navigation bar later if needed
        # self.nav_bar = self.create_nav_bar()

        # A container widget that has both the nav bar and stacked pages
        container = QWidget()
        container_layout = QVBoxLayout(container)
        # container_layout.addWidget(self.nav_bar)

        container_layout.addWidget(self.stacked_widget)

        self.setCentralWidget(container)

        # Start with Import page
        self.show_import_page()

    def show_import_page(self):
        """
        Lazy-load Page1 if it's not already created,
        then set it as the current widget in the stack.
        """
        if "import_page" not in self.pages:
            self.pages["import_page"] = ImportPageWidget(data=self.data_file)
            self.pages["import_page"].signal_to_preprocessing_page.connect(self.show_preprocessing_page)
            self.stacked_widget.addWidget(self.pages["import_page"])

        # No need to refresh anything for now
        else:
            # self.pages["import_page"].refresh_ui()
            pass
        self.stacked_widget.setCurrentWidget(self.pages["import_page"])

    def show_preprocessing_page(self):
        if "preprocessing_page" not in self.pages:
            self.pages["preprocessing_page"] = PreprocessingPageWidget(data=self.data_file)
            self.pages["preprocessing_page"].signal_to_import_page.connect(self.show_import_page)
            self.pages['preprocessing_page'].signal_to_search_selection_page.connect(
                self.show_search_algorithm_selection_page)
            self.stacked_widget.addWidget(self.pages["preprocessing_page"])

        else:
            self.pages["preprocessing_page"].refresh_ui()

        self.stacked_widget.setCurrentWidget(self.pages["preprocessing_page"])

    def show_search_algorithm_selection_page(self):
        if 'search_selection_page' not in self.pages:
            self.pages['search_selection_page'] = SearchSelectionPageWidget(data=self.data_file,
                                                                            ga_data=self.ga_run_instance,
                                                                            sa_data=self.sa_run_instance)
            self.pages['search_selection_page'].signal_to_preprocessing_page.connect(self.show_preprocessing_page)
            self.pages['search_selection_page'].signal_to_ga_page.connect(self.show_genetic_algorithm_page)
            self.pages['search_selection_page'].signal_to_sa_page.connect(self.show_simulated_annealing_page)
            self.stacked_widget.addWidget(self.pages['search_selection_page'])

        else:
            self.pages['search_selection_page'].refresh_ui()

        self.stacked_widget.setCurrentWidget(self.pages['search_selection_page'])

    def show_genetic_algorithm_page(self):
        if 'genetic_algorithm' not in self.pages:
            self.pages['genetic_algorithm'] = GeneticAlgorithmPageWidget(data=self.data_file,
                                                                         ga_data=self.ga_run_instance)
            # self.pages['genetic_algorithm'].signal_to_ga_page.connect()
            self.pages['genetic_algorithm'].signal_to_search_selection_page.connect(
                self.show_search_algorithm_selection_page)
            self.stacked_widget.addWidget(self.pages['genetic_algorithm'])

        else:
            self.pages['genetic_algorithm'].refresh_ui()

        self.stacked_widget.setCurrentWidget(self.pages['genetic_algorithm'])

    def show_simulated_annealing_page(self):
        if 'simulated_annealing' not in self.pages:
            self.pages['simulated_annealing'] = SimulatedAnnealingPageWidget(data=self.data_file,
                                                                             sa_data=self.sa_run_instance)

            self.pages['simulated_annealing'].signal_to_search_selection_page.connect(
                self.show_search_algorithm_selection_page)
            self.stacked_widget.addWidget(self.pages['simulated_annealing'])

        else:
            self.pages['simulated_annealing'].refresh_ui()

        self.stacked_widget.setCurrentWidget(self.pages['simulated_annealing'])

    # def create_nav_bar(self):
    #     """
    #     Example 'navigation bar' widget with two buttons:
    #     - Go to Page1
    #     - Go to Page2
    #     """
    #     nav_widget = QWidget()
    #     layout = QVBoxLayout(nav_widget)
    #
    #     btn_page1 = QPushButton("Go to Page1")
    #     btn_page1.clicked.connect(self.show_page1)
    #
    #     btn_page2 = QPushButton("Go to Page2")
    #     btn_page2.clicked.connect(self.show_page2)
    #
    #     layout.addWidget(btn_page1)
    #     layout.addWidget(btn_page2)
    #
    #     return nav_widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
            /* Example: Style for ALL QPushButtons */
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px;
                width: 100px;
            }

            QPushButton:hover {
                background-color: #5dade2;
            }
            /* Example: Style for ALL QLabel */
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            /* Example: Style for QTableView */
            QTableView {
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                background-color: #ecf0f1;
                alternate-background-color: #ffffff;
            }
            QTableView::item {
                padding: 4px;
            }
            QLineEdit {
                font-size: 14px;
                color: #2c3e50;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
        """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
