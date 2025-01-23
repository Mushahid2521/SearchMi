from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QTableView, QCheckBox, \
    QLineEdit, QGroupBox, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

import DataProcessing
from mainwindow import PandasModel


class PreprocessingPageWidget(QWidget):
    signal_to_import_page = pyqtSignal()
    signal_to_search_selection_page = pyqtSignal()

    def __init__(self, data: DataProcessing.DataFile, parent=None):
        """
        :param data: Shared dictionary or object for application data
        :param parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.data_file = data  # Keep a reference to the shared data
        self.init_ui()

    def init_ui(self):
        preprocessing_page_layout = QtWidgets.QVBoxLayout(self)

        title_label = QLabel("Preprocessing Input Data")
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        preprocessing_page_layout.addWidget(title_label)

        sizeShapeLayout = QHBoxLayout()
        sizeShapeLayout.setAlignment(Qt.AlignLeft)
        sizeShapeLayout.setContentsMargins(0, 0, 0, 0)
        sizeShapeLayout.setSpacing(0)
        labelSizeShape = QLabel("Size/Shape:")
        labelSizeShape.setAlignment(Qt.AlignLeft)
        labelSizeShape.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.labelDFShapeValue = QLabel(
            f"{self.data_file.input_dataframe.shape[0]} rows x {self.data_file.input_dataframe.shape[1]} features")
        self.labelDFShapeValue.setAlignment(Qt.AlignLeft)
        # self.labelDFShapeValue.setStyleSheet("border: 1px gray; padding: 4px;")
        self.labelDFShapeValue.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizeShapeLayout.addWidget(labelSizeShape)
        sizeShapeLayout.addWidget(self.labelDFShapeValue)
        preprocessing_page_layout.addLayout(sizeShapeLayout)

        labelDFShape = QLabel("DataFrame:")
        preprocessing_page_layout.addWidget(labelDFShape)

        # Two Table Views, side by side
        tableViewLayout = QHBoxLayout()
        self.tableView1 = QTableView()
        self.tableView2 = QTableView()
        tableViewLayout.addWidget(self.tableView1)
        tableViewLayout.addWidget(self.tableView2)
        tableViewLayout.setStretch(0, 3)
        tableViewLayout.setStretch(1, 1)

        input_abun_model = PandasModel(self.data_file.get_abundance_input_dataframe())
        self.tableView1.setModel(input_abun_model)
        input_meta_model = PandasModel(self.data_file.get_metadata_input_dataframe())
        self.tableView2.setModel(input_meta_model)

        preprocessing_page_layout.addLayout(tableViewLayout)

        # Data Preprocessing
        labelDataPreprocessing = QLabel("Data Preprocessing")
        preprocessing_page_layout.addWidget(labelDataPreprocessing)

        parallelLayout = QHBoxLayout()

        threshold_validator = QDoubleValidator(0.0, 100.00, 2)

        # Prevalence Section
        prevalenceLayout = QVBoxLayout()
        self.preprocessing_prevalence_either_checkbox = QCheckBox("Either")
        self.preprocessing_prevalence_both_checkbox = QCheckBox("Both")

        self.preprocessing_prevalence_both_checkbox.toggled.connect(
            lambda checked: self.preprocessing_prevalence_either_checkbox.setEnabled(not checked)
        )

        self.preprocessing_prevalence_either_checkbox.toggled.connect(
            lambda checked: self.preprocessing_prevalence_both_checkbox.setEnabled(not checked)
        )

        prevalenceOptionsLayout = QHBoxLayout()
        prevalenceCheckBoxLayout = QVBoxLayout()
        prevalenceCheckBoxLayout.addWidget(self.preprocessing_prevalence_either_checkbox)
        prevalenceCheckBoxLayout.addWidget(self.preprocessing_prevalence_both_checkbox)
        prevalenceOptionsLayout.addLayout(prevalenceCheckBoxLayout)
        self.prevalenceThresholdInput = QLineEdit()
        self.prevalenceThresholdInput.setValidator(threshold_validator)
        self.prevalenceThresholdInput.setPlaceholderText("Prevalence Threshold (0-100 %)")
        prevalenceOptionsLayout.addWidget(self.prevalenceThresholdInput)
        prevalenceGroup = QGroupBox("Prevalence")
        prevalenceGroup.setLayout(prevalenceOptionsLayout)
        prevalenceLayout.addWidget(prevalenceGroup)

        # Abundance Section
        abundanceLayout = QVBoxLayout()
        self.preprocessing_abundance_either_checkbox = QCheckBox("Either")
        self.preprocessing_abundance_both_checkbox = QCheckBox("Both")

        self.preprocessing_abundance_both_checkbox.toggled.connect(
            lambda checked: self.preprocessing_abundance_either_checkbox.setEnabled(not checked)
        )

        self.preprocessing_abundance_either_checkbox.toggled.connect(
            lambda checked: self.preprocessing_abundance_both_checkbox.setEnabled(not checked)
        )

        abundanceOptionsLayout = QHBoxLayout()
        abundanceCheckBoxLayout = QVBoxLayout()
        abundanceCheckBoxLayout.addWidget(self.preprocessing_abundance_either_checkbox)
        abundanceCheckBoxLayout.addWidget(self.preprocessing_abundance_both_checkbox)
        abundanceOptionsLayout.addLayout(abundanceCheckBoxLayout)
        self.abundanceThresholdInput = QLineEdit()
        self.abundanceThresholdInput.setPlaceholderText("Abundance Threshold (0-100 %)")
        self.abundanceThresholdInput.setValidator(threshold_validator)
        abundanceOptionsLayout.addWidget(self.abundanceThresholdInput)
        abundanceGroup = QGroupBox("Abundance")
        abundanceGroup.setLayout(abundanceOptionsLayout)
        abundanceLayout.addStretch()
        abundanceLayout.addWidget(abundanceGroup)

        # Vertical Line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        prevalenceWidget = QWidget()
        prevalenceWidget.setLayout(prevalenceLayout)
        abundanceWidget = QWidget()
        abundanceWidget.setLayout(abundanceLayout)

        parallelLayout.addWidget(prevalenceWidget)
        parallelLayout.addWidget(line)
        parallelLayout.addWidget(abundanceWidget)
        preprocessing_page_layout.addLayout(parallelLayout)

        self.preprocess_button = QtWidgets.QPushButton("Preprocess")
        preprocessing_page_layout.addWidget(self.preprocess_button)

        # Preprocessing output dataframe
        # Output shape
        output_sizeShapeLayout = QHBoxLayout()
        output_sizeShapeLayout.setContentsMargins(0, 0, 0, 0)
        output_sizeShapeLayout.setSpacing(0)
        output_labelSizeShape = QLabel("Output shape:")
        output_labelSizeShape.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        output_sizeShapeLayout.addWidget(output_labelSizeShape)

        self.outputlabelDFShapeValue = QLabel()
        # self.outputlabelDFShapeValue.setAlignment(Qt.AlignLeft)
        self.outputlabelDFShapeValue.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.outputlabelDFShapeValue.setStyleSheet("border: 1px gray; padding: 4px;")
        output_sizeShapeLayout.setAlignment(Qt.AlignLeft)
        output_sizeShapeLayout.addWidget(self.outputlabelDFShapeValue)

        preprocessing_page_layout.addLayout(output_sizeShapeLayout)

        labelFilteredShape = QLabel("Filtered DataFrame:")
        preprocessing_page_layout.addWidget(labelFilteredShape)

        # Table View for filtered DataFrame
        self.filteredTableView = QTableView()
        preprocessing_page_layout.addWidget(self.filteredTableView)
        self.preprocess_button.clicked.connect(self.preprocess_with_thresholds)

        button_layout = QHBoxLayout()
        self.back_button = QtWidgets.QPushButton("Back")
        self.toSearchbutton = QtWidgets.QPushButton("Next")

        self.toSearchbutton.clicked.connect(self.go_to_search_algorithm_ui)
        self.back_button.clicked.connect(self.go_to_data_import_ui)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.toSearchbutton)

        preprocessing_page_layout.addLayout(button_layout)
        preprocessing_page_layout.addStretch()

    def refresh_ui(self):
        self.labelDFShapeValue = QLabel(
            f"{self.data_file.input_dataframe.shape[0]} rows x {self.data_file.input_dataframe.shape[1]} features")

        input_abun_model = PandasModel(self.data_file.get_abundance_input_dataframe())
        self.tableView1.setModel(input_abun_model)
        input_meta_model = PandasModel(self.data_file.get_metadata_input_dataframe())
        self.tableView2.setModel(input_meta_model)

        self.preprocessing_prevalence_both_checkbox.setChecked(False)
        self.preprocessing_prevalence_either_checkbox.setChecked(False)
        self.prevalenceThresholdInput.setText("")
        self.preprocessing_abundance_either_checkbox.setChecked(False)
        self.preprocessing_abundance_both_checkbox.setChecked(False)
        self.abundanceThresholdInput.setText("")

        self.outputlabelDFShapeValue.setText("")
        self.filteredTableView.setModel(PandasModel())

        # Reset the data changed
        self.data_file.reset_the_processed_feature_list()

    def go_to_data_import_ui(self):
        self.signal_to_import_page.emit()

    def go_to_search_algorithm_ui(self):
        self.signal_to_search_selection_page.emit()

    def preprocess_with_thresholds(self):
        """
        Do the preprocessing based on the input threshold
        :return:
        """
        # prevalence threshold
        temporary_abundance_df = self.data_file.get_abundance_input_dataframe()
        temporary_metadata_df = self.data_file.get_metadata_input_dataframe()
        output_column = self.data_file.output_labels[0]  # only accounts for one output column
        unique_categories = temporary_metadata_df[output_column].unique()
        category_1_abundance_df = temporary_abundance_df.loc[
            temporary_metadata_df[output_column] == unique_categories[0]]
        category_2_abundance_df = temporary_abundance_df.loc[
            temporary_metadata_df[output_column] == unique_categories[1]]

        abundance_selected_species = set(temporary_abundance_df.columns.tolist())
        prevalence_selected_species = abundance_selected_species.copy()

        abundance_threshold = 0
        prevalence_threshold = 0

        if self.abundanceThresholdInput.text():
            abundance_threshold = float(self.abundanceThresholdInput.text())
        if self.prevalenceThresholdInput.text():
            prevalence_threshold = float(
                self.prevalenceThresholdInput.text()) / 100  # Converting it into 0-1 from 0-100

        mean_abundance_category_1_df = category_1_abundance_df.mean(axis=0).sort_values(ascending=False)
        abundance_species_category_1_df = mean_abundance_category_1_df[
            mean_abundance_category_1_df > abundance_threshold].index.to_list()
        mean_abundance_category_2_df = category_2_abundance_df.mean(axis=0).sort_values(ascending=False)
        abundance_species_category_2_df = mean_abundance_category_2_df[
            mean_abundance_category_2_df > abundance_threshold].index.to_list()

        if self.preprocessing_abundance_both_checkbox.isChecked():
            abundance_selected_species = set(abundance_species_category_1_df).intersection(
                set(abundance_species_category_2_df))
        elif self.preprocessing_abundance_either_checkbox.isChecked():
            abundance_selected_species = set(abundance_species_category_1_df).union(
                set(abundance_species_category_2_df))

        # Prevalence threshold
        category_1_abundance_df = category_1_abundance_df.mask(category_1_abundance_df > 0, 1)
        category_2_abundance_df = category_2_abundance_df.mask(category_2_abundance_df > 0, 1)
        category_1_prevalence_df = category_1_abundance_df.mean(axis=0)
        category_2_prevalence_df = category_2_abundance_df.mean(axis=0)
        prevalence_species_category_1_df = category_1_prevalence_df[
            category_1_prevalence_df > prevalence_threshold].index.to_list()
        prevalence_species_category_2_df = category_2_prevalence_df[
            category_2_prevalence_df > prevalence_threshold].index.to_list()

        if self.preprocessing_prevalence_both_checkbox.isChecked():
            prevalence_selected_species = set(prevalence_species_category_1_df).intersection(
                set(prevalence_species_category_2_df))
        elif self.preprocessing_prevalence_either_checkbox.isChecked():
            prevalence_selected_species = set(prevalence_species_category_1_df).union(
                set(prevalence_species_category_2_df))

        final_processed_set_of_species = list(abundance_selected_species.intersection(prevalence_selected_species))
        self.data_file.feature_list_after_preprocessing = sorted(final_processed_set_of_species)
        output_abundance_dataframe = self.data_file.set_preprocessed_abundance_dataframe(
            self.data_file.input_abundance_dataframe[
                final_processed_set_of_species])

        self.outputlabelDFShapeValue.setText(
            f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")

        # self.sa_shape_value_label.setText(
        #     f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")

        self.filteredTableView.setModel(PandasModel(output_abundance_dataframe))
