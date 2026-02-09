import random

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
        labelSizeShape = QLabel("Size/Shape: ")
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

        threshold_validator = QDoubleValidator(0.0, 100.00, 4)

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
        output_labelSizeShape = QLabel("Output shape: ")
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
        Dynamically handle any number of categories, computing both abundance-
        and prevalence-based filters. Then combine them (intersection) to get
        a final list of species.
        """

        # 1. Load data
        temporary_abundance_df = self.data_file.get_abundance_input_dataframe()
        temporary_metadata_df = self.data_file.get_metadata_input_dataframe()
        output_column = self.data_file.output_labels[0]  # Only one output column
        unique_categories = temporary_metadata_df[output_column].unique()

        # 2. Parse thresholds
        abundance_threshold = 0.0
        if self.abundanceThresholdInput.text():
            abundance_threshold = float(self.abundanceThresholdInput.text())

        prevalence_threshold = 0.0
        if self.prevalenceThresholdInput.text():
            # Convert from percentage to fraction (e.g., 10 -> 0.1)
            prevalence_threshold = float(self.prevalenceThresholdInput.text()) / 100.0

        # 3. Build a dict of category -> subset DataFrame
        #    This way, if there are N categories, we create N DataFrames.
        category_abundance_dfs = {
            cat: temporary_abundance_df.loc[temporary_metadata_df[output_column] == cat]
            for cat in unique_categories
        }

        # 4. Compute the abundance-based filter for each category
        #    and store sets of species above the threshold.
        category_abundance_species = {}
        for cat, cat_df in category_abundance_dfs.items():
            mean_abundance = cat_df.mean(axis=0)  # average across samples
            # Filter species based on abundance threshold
            abundance_species = mean_abundance[mean_abundance > abundance_threshold].index
            category_abundance_species[cat] = set(abundance_species)

        # 5. Combine all category sets based on 'both' or 'either' checkboxes
        if self.preprocessing_abundance_both_checkbox.isChecked():
            # Intersection across all categories
            abundance_selected_species = set.intersection(*category_abundance_species.values())
        elif self.preprocessing_abundance_either_checkbox.isChecked():
            # Union across all categories
            abundance_selected_species = set.union(*category_abundance_species.values())
        else:
            # If neither is checked, default to intersection or union, or do nothing
            # (This depends on your specific requirements.)
            abundance_selected_species = set.union(*category_abundance_species.values())

        # 6. Compute the prevalence-based filter for each category
        category_prevalence_species = {}
        for cat, cat_df in category_abundance_dfs.items():
            # Convert abundance to 1/0
            masked_df = cat_df.mask(cat_df > 0, 1)
            prevalence = masked_df.mean(axis=0)  # fraction of samples that have the species
            # Filter species by prevalence threshold
            prevalence_species = prevalence[prevalence > prevalence_threshold].index
            category_prevalence_species[cat] = set(prevalence_species)

        # 7. Combine all category sets for prevalence
        if self.preprocessing_prevalence_both_checkbox.isChecked():
            # Intersection across all categories
            prevalence_selected_species = set.intersection(*category_prevalence_species.values())
        elif self.preprocessing_prevalence_either_checkbox.isChecked():
            # Union across all categories
            prevalence_selected_species = set.union(*category_prevalence_species.values())
        else:
            # Default if neither is checked
            prevalence_selected_species = set.union(*category_prevalence_species.values())

        # 8. Final species = intersection of abundance filter & prevalence filter
        final_processed_set_of_species = abundance_selected_species.intersection(prevalence_selected_species)
        final_processed_list = sorted(final_processed_set_of_species)

        # final_processed_list = list(final_processed_set_of_species)
        # random.Random(42).shuffle(final_processed_list)


        # 9. Save the final feature list and create a new DataFrame
        self.data_file.feature_list_after_preprocessing = final_processed_list
        output_abundance_dataframe = self.data_file.set_preprocessed_abundance_dataframe(
            self.data_file.input_abundance_dataframe[final_processed_list]
        )

        # 10. Update UI labels, table, etc.
        self.outputlabelDFShapeValue.setText(
            f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features"
        )
        self.filteredTableView.setModel(PandasModel(output_abundance_dataframe))

