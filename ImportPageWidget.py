import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

import DataProcessing
from mainwindow import PandasModel


class ImportPageWidget(QWidget):
    signal_to_preprocessing_page = pyqtSignal()

    def __init__(self, data: DataProcessing.DataFile, parent=None):
        """
        :param data: Shared dictionary or object for application data
        :param parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.data_file = data  # Keep a reference to the shared data
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        title_label = QLabel("Data Import")
        # Optionally style title (e.g., larger font, alignment, etc.)
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 1) Button to import CSV
        self.import_btn = QtWidgets.QPushButton("Import CSV")
        self.path_label = QtWidgets.QLabel("Location: path")
        self.table_view = QtWidgets.QTableView()
        output_columns_label = QtWidgets.QLabel("Metadata Columns (comma-separated):")
        self.output_columns_edit = QtWidgets.QLineEdit()
        self.output_columns_edit.setPlaceholderText(
            "e.g. Column1,Column2,Column3"
        )
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red;")  # Make text red
        self.error_label.setVisible(False)  # Hide it by default
        self.next_btn = QtWidgets.QPushButton("Next")

        layout.addWidget(self.import_btn)
        layout.addWidget(self.path_label)
        layout.addWidget(self.table_view)
        layout.addWidget(output_columns_label)
        layout.addWidget(self.output_columns_edit)
        layout.addWidget(self.error_label)
        layout.addWidget(self.next_btn)

        self.import_btn.clicked.connect(self.import_csv)
        self.next_btn.clicked.connect(self.go_to_preprocessing_page)

    def import_csv(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select CSV or Excel file",
            "",
            "CSV/Excel files (*.csv *.xlsx *.xls)"
        )
        if filename:
            self.path_label.setText(f"Location: {filename}")
            try:
                self.data_file.read_file(file_path=filename)
                model = PandasModel(self.data_file.get_input_dataframe())
                self.table_view.setModel(model)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not load CSV file:\n{e}"
                )

    def go_to_preprocessing_page(self):
        output_cols_text = self.output_columns_edit.text()
        flag, message = self.data_file.check_before_moving_to_preprocessing(output_cols_text)
        if not flag:
            self.error_label.setVisible(True)
            self.error_label.setText(message)
            return
        else:
            self.error_label.setVisible(False)
            self.signal_to_preprocessing_page.emit()

        # self.preprocessing_page_ui()
        # if 'preprocessing_page' not in self.widgets_map:
        #     self.stacked_widget.addWidget(self.preprocessing_page)
        #     self.widgets_map['preprocessing_page'] = self.preprocessing_page
        #     self.stacked_widget.setCurrentWidget(self.preprocessing_page)
        # else:
        #     self.stacked_widget.setCurrentWidget(self.widgets_map.get('preprocessing_page'))
