import sys
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QLineEdit, QGroupBox, QWidget, QTableView, \
    QFrame, QSizePolicy, QFormLayout, QComboBox, QPushButton, QProgressBar, QListWidget, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt

from DataProcessing import DataFile
from PyQt5.QtGui import QDoubleValidator

from GeneticAlgorithm import GeneticAlgorithm

"""
TODO: 
1. Solve the scroll issue in the metadata table view 
"""


class PandasModel(QtCore.QAbstractTableModel):
    """
    A basic model to interface a Pandas DataFrame with a QTableView.
    """

    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return str(self._df.iat[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(self._df.index[section])
        return None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔎SearchMi")
        # Set a "regular" window size
        self.resize(800, 600)

        # Data files and interactions with the GA
        self.data_file = DataFile()
        self.ga_run_instance = None
        self.sa_run_instance = None

        # Create a stacked widget to hold multiple pages
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.widgets_map = {}

        # Create the two pages
        self.import_data_page = QtWidgets.QWidget()
        self.preprocessing_page = QtWidgets.QWidget()
        self.search_algorithm_design_page = QtWidgets.QWidget()
        self.ga_search_running_page = QtWidgets.QWidget()
        self.sa_search_running_page = QtWidgets.QWidget()

        # Initialize import data UI
        self.import_page_ui()
        self.widgets_map['import_page'] = self.import_data_page
        self.stacked_widget.addWidget(self.import_data_page)
        self.stacked_widget.setCurrentWidget(self.widgets_map.get('import_page'))

        # Initialize pre-processing page UI
        # self.preprocessing_page_ui()
        # Search algorithm page UI
        # self.search_algorithm_page_ui()
        # GA Search running page UI
        # self.ga_searching_interface_page_ui()
        # SA Search running page UI
        # self.sa_search_running_page_ui()

        # Add pages to the stacked widget

        # self.stacked_widget.addWidget(self.preprocessing_page)
        # self.stacked_widget.addWidget(self.search_algorithm_design_page)
        # self.stacked_widget.addWidget(self.ga_search_running_page)
        # self.stacked_widget.addWidget(self.sa_search_running_page)

        # DataFrame placeholder
        self.df = pd.DataFrame()

    def import_page_ui(self):
        """
        Set up the UI for the first page: CSV import, data preview, etc.
        """
        layout = QtWidgets.QVBoxLayout()

        title_label = QLabel("Data Import")
        # Optionally style title (e.g., larger font, alignment, etc.)
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 1) Button to import CSV
        import_btn = QtWidgets.QPushButton("Import CSV")
        path_label = QtWidgets.QLabel("Location: path")
        table_view = QtWidgets.QTableView()
        output_columns_label = QtWidgets.QLabel("Metadata Columns (comma-separated):")
        output_columns_edit = QtWidgets.QLineEdit()
        output_columns_edit.setPlaceholderText(
            "e.g. Column1,Column2,Column3"
        )
        error_label = QtWidgets.QLabel("")
        error_label.setStyleSheet("color: red;")  # Make text red
        error_label.setVisible(False)  # Hide it by default
        next_btn = QtWidgets.QPushButton("Next")

        layout.addWidget(import_btn)
        layout.addWidget(path_label)
        layout.addWidget(table_view)
        layout.addWidget(output_columns_label)
        layout.addWidget(output_columns_edit)
        layout.addWidget(error_label)
        layout.addWidget(next_btn)

        def import_csv():
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Select CSV or Excel file",
                "",
                "CSV/Excel files (*.csv *.xlsx *.xls)"
            )
            if filename:
                path_label.setText(f"Location: {filename}")
                try:
                    self.data_file.read_file(file_path=filename)
                    model = PandasModel(self.data_file.get_input_dataframe())
                    table_view.setModel(model)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error",
                        f"Could not load CSV file:\n{e}"
                    )

        def go_to_preprocessing_page():
            output_cols_text = output_columns_edit.text()
            output_cols = [col.strip() for col in output_cols_text.split(',')]

            if not set(output_cols).issubset(self.data_file.input_dataframe.columns):
                error_label.setText("Columns are not in the dataframe!")
                error_label.setVisible(True)
                return

            self.data_file.set_output_labels(output_cols)
            flag, message = self.data_file.check_consistency_of_input_data()
            if not flag:
                error_label.setText(message)
                error_label.setVisible(True)
                self.data_file.reset_output_labels()
                return

            error_label.setVisible(False)
            self.preprocessing_page_ui()
            if 'preprocessing_page' not in self.widgets_map:
                self.stacked_widget.addWidget(self.preprocessing_page)
                self.widgets_map['preprocessing_page'] = self.preprocessing_page
                self.stacked_widget.setCurrentWidget(self.preprocessing_page)
            else:
                self.stacked_widget.setCurrentWidget(self.widgets_map.get('preprocessing_page'))

        import_btn.clicked.connect(import_csv)
        next_btn.clicked.connect(go_to_preprocessing_page)

        self.import_data_page.setLayout(layout)

    def preprocessing_page_ui(self):
        """
        Set up the UI for the second page.
        """
        preprocessing_page_layout = QtWidgets.QVBoxLayout()

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
        # labelSizeShape.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        labelDFShapeValue = QLabel(
            f"{self.data_file.input_dataframe.shape[0]} rows x {self.data_file.input_dataframe.shape[1]} features")
        labelDFShapeValue.setAlignment(Qt.AlignLeft)
        # labelDFShapeValue.setStyleSheet("border: 1px gray; padding: 4px;")
        labelDFShapeValue.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizeShapeLayout.addWidget(labelSizeShape)
        sizeShapeLayout.addWidget(labelDFShapeValue)
        preprocessing_page_layout.addLayout(sizeShapeLayout)

        labelDFShape = QLabel("DataFrame:")
        preprocessing_page_layout.addWidget(labelDFShape)

        # Two Table Views, side by side
        tableViewLayout = QHBoxLayout()
        tableView1 = QTableView()
        tableView2 = QTableView()
        tableViewLayout.addWidget(tableView1)
        tableViewLayout.addWidget(tableView2)
        tableViewLayout.setStretch(0, 3)
        tableViewLayout.setStretch(1, 1)

        input_abun_model = PandasModel(self.data_file.get_abundance_input_dataframe())
        tableView1.setModel(input_abun_model)
        input_meta_model = PandasModel(self.data_file.get_metadata_input_dataframe())
        tableView2.setModel(input_meta_model)

        preprocessing_page_layout.addLayout(tableViewLayout)

        # Data Preprocessing
        labelDataPreprocessing = QLabel("Data Preprocessing")
        preprocessing_page_layout.addWidget(labelDataPreprocessing)

        parallelLayout = QHBoxLayout()

        threshold_validator = QDoubleValidator(0.0, 100.00, 2)

        # Prevalence Section
        prevalenceLayout = QVBoxLayout()
        preprocessing_prevalence_either_checkbox = QCheckBox("Either")
        preprocessing_prevalence_both_checkbox = QCheckBox("Both")

        preprocessing_prevalence_both_checkbox.toggled.connect(
            lambda checked: preprocessing_prevalence_either_checkbox.setEnabled(not checked)
        )

        preprocessing_prevalence_either_checkbox.toggled.connect(
            lambda checked: preprocessing_prevalence_both_checkbox.setEnabled(not checked)
        )

        prevalenceOptionsLayout = QHBoxLayout()
        prevalenceCheckBoxLayout = QVBoxLayout()
        prevalenceCheckBoxLayout.addWidget(preprocessing_prevalence_either_checkbox)
        prevalenceCheckBoxLayout.addWidget(preprocessing_prevalence_both_checkbox)
        prevalenceOptionsLayout.addLayout(prevalenceCheckBoxLayout)
        prevalenceThresholdInput = QLineEdit()
        prevalenceThresholdInput.setValidator(threshold_validator)
        prevalenceThresholdInput.setPlaceholderText("Prevalence Threshold (0-100 %)")
        prevalenceOptionsLayout.addWidget(prevalenceThresholdInput)
        prevalenceGroup = QGroupBox("Prevalence")
        prevalenceGroup.setLayout(prevalenceOptionsLayout)
        prevalenceLayout.addWidget(prevalenceGroup)

        # Abundance Section
        abundanceLayout = QVBoxLayout()
        preprocessing_abundance_either_checkbox = QCheckBox("Either")
        preprocessing_abundance_both_checkbox = QCheckBox("Both")

        preprocessing_abundance_both_checkbox.toggled.connect(
            lambda checked: preprocessing_abundance_either_checkbox.setEnabled(not checked)
        )

        preprocessing_abundance_either_checkbox.toggled.connect(
            lambda checked: preprocessing_abundance_both_checkbox.setEnabled(not checked)
        )

        abundanceOptionsLayout = QHBoxLayout()
        abundanceCheckBoxLayout = QVBoxLayout()
        abundanceCheckBoxLayout.addWidget(preprocessing_abundance_either_checkbox)
        abundanceCheckBoxLayout.addWidget(preprocessing_abundance_both_checkbox)
        abundanceOptionsLayout.addLayout(abundanceCheckBoxLayout)
        abundanceThresholdInput = QLineEdit()
        abundanceThresholdInput.setPlaceholderText("Abundance Threshold (0-100 %)")
        abundanceThresholdInput.setValidator(threshold_validator)
        abundanceOptionsLayout.addWidget(abundanceThresholdInput)
        abundanceGroup = QGroupBox("Abundance")
        abundanceGroup.setLayout(abundanceOptionsLayout)
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

        preprocess_button = QtWidgets.QPushButton("Preprocess")
        preprocessing_page_layout.addWidget(preprocess_button)
        #
        # # Preprocessing output dataframe
        # # Output shape
        # output_sizeShapeLayout = QHBoxLayout()
        # # output_sizeShapeLayout.setContentsMargins(0, 0, 0, 0)
        # # output_sizeShapeLayout.setSpacing(0)
        # output_labelSizeShape = QLabel("Output shape:")
        # # output_labelSizeShape.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # output_sizeShapeLayout.addWidget(output_labelSizeShape)
        #
        # output_labelDFShapeValue = QLabel()
        # output_labelDFShapeValue.setAlignment(Qt.AlignLeft)
        # output_labelDFShapeValue.setStyleSheet("border: 1px gray; padding: 4px;")
        # output_sizeShapeLayout.addWidget(output_labelDFShapeValue)
        #
        # preprocessing_page_layout.addLayout(output_sizeShapeLayout)
        #
        # labelFilteredShape = QLabel("Filtered DataFrame:")
        # preprocessing_page_layout.addWidget(labelFilteredShape)
        #
        # # Table View for filtered DataFrame
        # filteredTableView = QTableView()
        # preprocessing_page_layout.addWidget(filteredTableView)
        #
        # def preprocess_with_thresholds():
        #     """
        #     Do the preprocessing based on the input threshold
        #     :return:
        #     """
        #     # prevalence threshold
        #     temporary_abundance_df = self.data_file.get_abundance_input_dataframe()
        #     temporary_metadata_df = self.data_file.get_metadata_input_dataframe()
        #     output_column = self.data_file.output_labels[0]  # only accounts for one output column
        #     unique_categories = temporary_metadata_df[output_column].unique()
        #     category_1_abundance_df = temporary_abundance_df.loc[
        #         temporary_metadata_df[output_column] == unique_categories[0]]
        #     category_2_abundance_df = temporary_abundance_df.loc[
        #         temporary_metadata_df[output_column] == unique_categories[1]]
        #
        #     abundance_selected_species = set(temporary_abundance_df.columns.tolist())
        #     prevalence_selected_species = abundance_selected_species.copy()
        #
        #     abundance_threshold = 0
        #     prevalence_threshold = 0
        #
        #     if abundanceThresholdInput.text():
        #         abundance_threshold = float(abundanceThresholdInput.text())
        #     if prevalenceThresholdInput.text():
        #         prevalence_threshold = float(
        #             prevalenceThresholdInput.text()) / 100  # Converting it into 0-1 from 0-100
        #
        #     mean_abundance_category_1_df = category_1_abundance_df.mean(axis=0).sort_values(ascending=False)
        #     abundance_species_category_1_df = mean_abundance_category_1_df[
        #         mean_abundance_category_1_df > abundance_threshold].index.to_list()
        #     mean_abundance_category_2_df = category_2_abundance_df.mean(axis=0).sort_values(ascending=False)
        #     abundance_species_category_2_df = mean_abundance_category_2_df[
        #         mean_abundance_category_2_df > abundance_threshold].index.to_list()
        #
        #     if preprocessing_abundance_both_checkbox.isChecked():
        #         abundance_selected_species = set(abundance_species_category_1_df).intersection(
        #             set(abundance_species_category_2_df))
        #     elif preprocessing_abundance_either_checkbox.isChecked():
        #         abundance_selected_species = set(abundance_species_category_1_df).union(
        #             set(abundance_species_category_2_df))
        #
        #     # Prevalence threshold
        #     category_1_abundance_df = category_1_abundance_df.mask(category_1_abundance_df > 0, 1)
        #     category_2_abundance_df = category_2_abundance_df.mask(category_2_abundance_df > 0, 1)
        #     category_1_prevalence_df = category_1_abundance_df.mean(axis=0)
        #     category_2_prevalence_df = category_2_abundance_df.mean(axis=0)
        #     prevalence_species_category_1_df = category_1_prevalence_df[
        #         category_1_prevalence_df > prevalence_threshold].index.to_list()
        #     prevalence_species_category_2_df = category_2_prevalence_df[
        #         category_2_prevalence_df > prevalence_threshold].index.to_list()
        #
        #     if preprocessing_prevalence_both_checkbox.isChecked():
        #         prevalence_selected_species = set(prevalence_species_category_1_df).intersection(
        #             set(prevalence_species_category_2_df))
        #     elif preprocessing_prevalence_either_checkbox.isChecked():
        #         prevalence_selected_species = set(prevalence_species_category_1_df).union(
        #             set(prevalence_species_category_2_df))
        #
        #     final_processed_set_of_species = list(abundance_selected_species.intersection(prevalence_selected_species))
        #     self.data_file.feature_list_after_preprocessing = sorted(final_processed_set_of_species)
        #     output_abundance_dataframe = self.data_file.set_preprocessed_abundance_dataframe(
        #         self.data_file.input_abundance_dataframe[
        #             final_processed_set_of_species])
        #
        #     output_labelDFShapeValue.setText(
        #         f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")
        #
        #     # self.sa_shape_value_label.setText(
        #     #     f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")
        #
        #     filteredTableView.setModel(PandasModel(output_abundance_dataframe))
        #
        # preprocess_button.clicked.connect(preprocess_with_thresholds)
        #
        # def go_to_search_algorithm_ui():
        #     self.search_algorithm_page_ui()
        #     # self.stacked_widget.addWidget(self.search_algorithm_design_page)
        #     self.stacked_widget.setCurrentWidget(self.search_algorithm_design_page)
        #
        # def go_to_data_import_ui():
        #     self.stacked_widget.setCurrentWidget(self.import_data_page)
        #
        # button_layout = QHBoxLayout()
        # back_button = QtWidgets.QPushButton("Back")
        # toSearchbutton = QtWidgets.QPushButton("Next")
        #
        # toSearchbutton.clicked.connect(go_to_search_algorithm_ui)
        # back_button.clicked.connect(go_to_data_import_ui)
        # button_layout.addWidget(back_button)
        # button_layout.addWidget(toSearchbutton)
        #
        # preprocessing_page_layout.addLayout(button_layout)

        self.preprocessing_page.setLayout(preprocessing_page_layout)

    def search_algorithm_page_ui(self):
        """
        Returns a QWidget containing the layout described:
        """
        search_algorithm_layout = QVBoxLayout()

        # --- Title at the top ---
        title_label = QLabel("Search Algorithms")
        # Optionally style title (e.g., larger font, alignment, etc.)
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        search_algorithm_layout.addWidget(title_label)

        # --- Data shape section ---
        data_shape_layout = QHBoxLayout()
        data_shape_label = QLabel("Data shape:")
        sa_shape_value_label = QLabel(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[0]} features")
        data_shape_layout.addWidget(data_shape_label)
        data_shape_layout.addWidget(sa_shape_value_label)
        data_shape_layout.addStretch()
        search_algorithm_layout.addLayout(data_shape_layout)

        # --- Algorithm selection checkboxes ---
        algo_selection_layout = QHBoxLayout()
        genetic_checkbox = QCheckBox("Genetic Search")
        sa_checkbox = QCheckBox("Simulated Annealing")

        algo_selection_layout.addWidget(genetic_checkbox)
        algo_selection_layout.addWidget(sa_checkbox)
        algo_selection_layout.addStretch()
        search_algorithm_layout.addLayout(algo_selection_layout)

        # --- Parameter sections (group boxes) ---
        # Create group and layout
        genetic_params_group = QGroupBox("Genetic Algorithm Parameters")
        genetic_params_layout = QFormLayout()

        # Create line edits with default values
        genetic_pop_size = QLineEdit("100")
        genetic_num_parents = QLineEdit("10")
        genetic_seed = QLineEdit("42")

        # Add the population size row as is
        genetic_params_layout.addRow("Population size:", genetic_pop_size)

        # Create checkboxes and corresponding QLineEdits for options
        custom_checkbox = QCheckBox("Custom")
        custom_generation_edit = QLineEdit("50")
        custom_generation_edit.setEnabled(False)  # disabled initially

        continue_checkbox = QCheckBox("Continue till no improvement for generations")
        improvement_edit = QLineEdit("10")
        improvement_edit.setEnabled(False)  # disabled initially

        # Set "Continue till no improvement for" as checked by default
        continue_checkbox.setChecked(True)
        improvement_edit.setEnabled(True)

        # Connect toggled signals to enable/disable corresponding QLineEdits
        custom_checkbox.toggled.connect(custom_generation_edit.setEnabled)
        continue_checkbox.toggled.connect(improvement_edit.setEnabled)

        # Ensure that when one checkbox is enabled, the other becomes disabled
        def on_custom_toggled(checked):
            # If Custom is checked, disable Continue option, else enable it.
            continue_checkbox.setDisabled(checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        def on_continue_toggled(checked):
            # If Continue is checked, disable Custom option, else enable it.
            custom_checkbox.setDisabled(checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        custom_checkbox.toggled.connect(on_custom_toggled)
        continue_checkbox.toggled.connect(on_continue_toggled)

        # Layout for the "Custom" option row
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(custom_checkbox)
        custom_layout.addWidget(custom_generation_edit)
        genetic_params_layout.addRow("Number of generations:", custom_layout)

        # Layout for the "Continue till no improvement for" option
        continue_layout = QHBoxLayout()
        continue_layout.addWidget(continue_checkbox)
        continue_layout.addWidget(improvement_edit)
        genetic_params_layout.addRow("", continue_layout)

        # Add remaining rows
        genetic_params_layout.addRow("Number of parents:", genetic_num_parents)
        genetic_params_layout.addRow("Seed:", genetic_seed)

        genetic_params_group.setLayout(genetic_params_layout)

        # ------- Simulated Annealing parameters ------- #
        sa_params_group = QGroupBox("Simulated Annealing Parameters")
        sa_params_layout = QFormLayout()

        sa_num_iterations = QLineEdit("1000")
        sa_temperature = QLineEdit("100.0")
        sa_cooling_rate = QLineEdit("0.95")
        sa_seed = QLineEdit("42")

        sa_params_layout.addRow("Number of Iterations:", sa_num_iterations)
        sa_params_layout.addRow("Temperature:", sa_temperature)
        sa_params_layout.addRow("Cooling Rate:", sa_cooling_rate)
        sa_params_layout.addRow("Seed:", sa_seed)
        sa_params_group.setLayout(sa_params_layout)

        # By default, hide both parameter groups (shown when checkbox is checked)
        genetic_params_group.setVisible(False)
        sa_params_group.setVisible(False)

        search_algorithm_layout.addWidget(genetic_params_group)
        search_algorithm_layout.addWidget(sa_params_group)

        # --- Objective function / statistics selection ---
        obj_func_group = QGroupBox("Objective Function / Statistics")
        obj_func_layout = QVBoxLayout()

        # 2) Test selection (ComboBox)
        test_label = QLabel("Select test:")
        obj_func_combo = QComboBox()
        obj_func_combo.addItems(["Mann-Whitney Test", "T-test"])  # Add more as needed

        obj_func_layout.addWidget(test_label)
        obj_func_layout.addWidget(obj_func_combo)

        # 3) Hypothesis selection (Radio Buttons)
        hypothesis_groupbox = QGroupBox("Hypothesis")
        hypothesis_layout = QHBoxLayout()

        two_sided_radio = QRadioButton("Two sided")
        one_sided_radio = QRadioButton("One sided")

        # Add them to a ButtonGroup so only one can be selected
        hypothesis_btn_group = QButtonGroup()
        hypothesis_btn_group.addButton(two_sided_radio)
        hypothesis_btn_group.addButton(one_sided_radio)

        # Default to "Two sided"
        two_sided_radio.setChecked(True)

        hypothesis_layout.addWidget(two_sided_radio)
        hypothesis_layout.addWidget(one_sided_radio)
        hypothesis_groupbox.setLayout(hypothesis_layout)
        obj_func_layout.addWidget(hypothesis_groupbox)

        # 4) Positive/Negative Signature (Radio Buttons), initially hidden
        signature_group = QGroupBox("Signature type")
        signature_layout = QHBoxLayout()

        positive_radio = QRadioButton("Positive signatures")
        negative_radio = QRadioButton("Negative signatures")

        # Put them in a button group to be mutually exclusive
        self.signature_btn_group = QButtonGroup()
        self.signature_btn_group.addButton(positive_radio)
        self.signature_btn_group.addButton(negative_radio)

        # One of them can be default
        positive_radio.setChecked(True)

        signature_layout.addWidget(positive_radio)
        signature_layout.addWidget(negative_radio)
        signature_group.setLayout(signature_layout)

        # Start hidden unless "One sided" is chosen
        signature_group.setVisible(False)
        obj_func_layout.addWidget(signature_group)

        # 5) Control Group selection, initially hidden
        control_group_box = QGroupBox("Control Group")
        control_group_layout = QHBoxLayout()

        groupA_radio = QRadioButton(self.data_file.output_label_groups[0])
        groupB_radio = QRadioButton(self.data_file.output_label_groups[1])

        # Put them in a button group
        control_group_btn_group = QButtonGroup()
        control_group_btn_group.addButton(groupA_radio)
        control_group_btn_group.addButton(groupB_radio)

        # Choose one of them by default
        groupA_radio.setChecked(True)

        control_group_layout.addWidget(groupA_radio)
        control_group_layout.addWidget(groupB_radio)
        control_group_box.setLayout(control_group_layout)

        # Start hidden unless "One sided" is chosen
        control_group_box.setVisible(False)
        obj_func_layout.addWidget(control_group_box)

        # 6) Connect signals to show/hide "Signature" and "Control Group"
        def on_hypothesis_changed():
            if one_sided_radio.isChecked():
                signature_group.setVisible(True)
                control_group_box.setVisible(True)
            else:
                signature_group.setVisible(False)
                control_group_box.setVisible(False)

        two_sided_radio.toggled.connect(on_hypothesis_changed)
        one_sided_radio.toggled.connect(on_hypothesis_changed)
        on_hypothesis_changed()  # Ensure correct initial state

        # Finalize the Objective Function group layout
        obj_func_group.setLayout(obj_func_layout)

        # Finally, add 'obj_func_group' to the parent layout
        search_algorithm_layout.addWidget(obj_func_group)

        # --- Logic to enable/disable parameter sections based on selection ---
        def on_genetic_toggled(checked):
            if checked:
                # Uncheck the other checkbox
                sa_checkbox.setChecked(False)
                # Show genetic parameters, hide SA parameters
                genetic_params_group.setVisible(True)
                sa_params_group.setVisible(False)
            else:
                genetic_params_group.setVisible(False)

        def on_sa_toggled(checked):
            if checked:
                # Uncheck the other checkbox
                genetic_checkbox.setChecked(False)
                # Show SA parameters, hide Genetic parameters
                sa_params_group.setVisible(True)
                genetic_params_group.setVisible(False)
            else:
                sa_params_group.setVisible(False)

        genetic_checkbox.toggled.connect(on_genetic_toggled)
        sa_checkbox.toggled.connect(on_sa_toggled)
        genetic_checkbox.setChecked(True)

        # # Adjust stretching or spacing if needed
        # search_algorithm_layout.addStretch()

        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        search_button = QPushButton("Search")

        def go_to_preprocessing_page():
            self.stacked_widget.setCurrentIndex(1)

        def choosing_search_algorithm_page():
            if genetic_checkbox.isChecked():
                hypothesis_selection = 'two-sided'
                positive_category = str(groupA_radio.text())
                if two_sided_radio.isChecked():
                    hypothesis_selection = 'two-sided'
                elif one_sided_radio.isChecked():
                    hypothesis_selection = 'one-sided'
                    signature_type = 'positive'
                    if negative_radio.isChecked():
                        signature_type = 'negative'
                    if groupA_radio.isChecked():
                        positive_category = str(groupA_radio.text())

                self.ga_searching_interface_page_ui(name_algo="Genetic Algorithm",
                                                    pop_size=int(genetic_pop_size.text()),
                                                    num_generations=3,  # TODO change this
                                                    stop_strategy=False,
                                                    num_parents=int(genetic_num_parents.text()),
                                                    objective_function=str(obj_func_combo.textActivated),
                                                    hypothesis_selection=hypothesis_selection,
                                                    positive_category=positive_category,
                                                    signature_type=signature_type,
                                                    output_label_categories=self.data_file.output_label_groups,
                                                    random_seed=int(genetic_seed.text())
                                                    )
                self.stacked_widget.addWidget(self.ga_search_running_page)
                self.stacked_widget.setCurrentWidget(self.ga_search_running_page)

            elif sa_checkbox.isChecked():
                self.sa_search_running_page_ui()
                self.stacked_widget.addWidget(self.sa_search_running_page)
                self.stacked_widget.setCurrentWidget(self.sa_search_running_page)

        # Add them side by side
        button_layout.addWidget(back_button)
        button_layout.addWidget(search_button)
        back_button.clicked.connect(go_to_preprocessing_page)
        search_button.clicked.connect(choosing_search_algorithm_page)

        # Ensure everything above stays at top, buttons at bottom
        search_algorithm_layout.addStretch()
        search_algorithm_layout.addLayout(button_layout)

        self.search_algorithm_design_page.setLayout(search_algorithm_layout)

    def sa_search_running_page_ui(self):
        pass

    def ga_searching_interface_page_ui(self, name_algo: str,
                                       pop_size: int,
                                       num_generations: int,
                                       stop_strategy: bool,
                                       num_parents: int,
                                       objective_function: str,
                                       hypothesis_selection: str,
                                       positive_category: str,
                                       signature_type: str,
                                       output_label_categories: list,
                                       random_seed: int
                                       ):

        # Create the GA run instance
        if self.ga_run_instance is None:
            self.ga_run_instance = GeneticAlgorithm(
                search_abundance=self.data_file.preprocessed_abundance_dataframe,
                metadata=self.data_file.input_metadata_dataframe,
                hypothesis_selection=hypothesis_selection,
                output_label_categories=output_label_categories,
                # search_disease="",
                soi_list=self.data_file.feature_list_after_preprocessing,
                pop_size=pop_size,
                num_generations=num_generations,
                num_parents=num_parents,
                objective_function=objective_function,
                positive_label=positive_category,
                signature_type=signature_type,
                random_seed=random_seed
            )

        if stop_strategy:
            num_generations = 300

        # Main vertical layout
        main_layout = QVBoxLayout()

        # Title label
        title_label = QLabel(name_algo)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Row for Input Data Shape
        shape_layout = QHBoxLayout()
        input_shape_label = QLabel("Data Shape:")
        input_shape_value = QLabel(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[1]} features")  # Example shape text
        shape_layout.addWidget(input_shape_label)
        shape_layout.addWidget(input_shape_value)
        shape_layout.addStretch()  # Add stretch to push contents to left
        main_layout.addLayout(shape_layout)

        # Row for Generations
        gen_layout = QHBoxLayout()
        generations_label = QLabel("Generations:")
        current_gen_label = QLabel(f"0/{num_generations}")  # Example current generations text
        gen_layout.addWidget(generations_label)
        gen_layout.addWidget(current_gen_label)
        gen_layout.addStretch()
        main_layout.addLayout(gen_layout)

        # Progress Bar for generation progress
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(num_generations)  # Example maximum generation count
        progress_bar.setValue(0)  # Example current progress
        main_layout.addWidget(progress_bar)

        info_text_label = QLabel("")
        main_layout.addWidget(info_text_label)

        # Two parallel sections for results and species
        parallel_layout = QHBoxLayout()

        # Left section layout (Vertical with header and list)
        left_panel_layout = QVBoxLayout()
        cost_function_label = QLabel("Cost function")
        cost_function_label.setAlignment(Qt.AlignLeft)
        left_panel_layout.addWidget(cost_function_label)

        results_list = QListWidget()
        # Example dynamic population loop - replace with your dynamic logic

        results_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_panel_layout.addWidget(results_list)

        parallel_layout.addLayout(left_panel_layout)

        # Right section layout (Vertical with header and list)
        right_panel_layout = QVBoxLayout()
        species_label = QLabel("Species combination")
        species_label.setAlignment(Qt.AlignLeft)
        right_panel_layout.addWidget(species_label)

        species_list = QListWidget()
        species_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel_layout.addWidget(species_list)

        # Function to handle click on items in the left panel and update species_list on the right
        def updateSpeciesList(item):
            # Clear the current species list
            species_list.clear()
            index = results_list.row(item)

            this_solution = self.ga_run_instance.tracking_generations[index].get('best_solution')
            for spp in this_solution:
                species_list.addItem(spp)
            species_list.scrollToTop()

        # Connect the left panel's item click signal to the update function
        results_list.itemClicked.connect(updateSpeciesList)

        parallel_layout.addLayout(right_panel_layout)

        for i in range(1, num_generations):
            self.ga_run_instance.run_one_iteration()
            generation_no = self.ga_run_instance.current_generation
            cost_value = self.ga_run_instance.tracking_generations[generation_no].get('best_score')
            results_list.addItem(0, f"Generation: {generation_no} | P-value: {cost_value}")
            results_list.scrollToTop()

            # Add right panel species list
            best_solution = self.ga_run_instance.tracking_generations[generation_no].get('best_solution')
            for sp in best_solution:
                species_list.addItem(sp)
            species_list.scrollToTop()

            progress_bar.setValue(i)

        main_layout.addLayout(parallel_layout)

        # Row for Pause and Stop buttons
        button_layout = QHBoxLayout()

        pause_button = QPushButton("Pause")
        pause_button.setStyleSheet("background-color: blue; color: white; padding: 6px;")
        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet("background-color: red; color: white; padding: 6px;")

        button_layout.addWidget(pause_button)
        button_layout.addWidget(stop_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Set some margins and spacing if desired
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.ga_search_running_page.setLayout(main_layout)

    # def preprocess_with_thresholds(self):
    #     """
    #     Do the preprocessing based on the input threshold
    #     :return:
    #     """
    #     # prevalence threshold
    #     temporary_abundance_df = self.data_file.get_abundance_input_dataframe()
    #     temporary_metadata_df = self.data_file.get_metadata_input_dataframe()
    #     output_column = self.data_file.output_labels[0]  # only accounts for one output column
    #     unique_categories = temporary_metadata_df[output_column].unique()
    #     category_1_abundance_df = temporary_abundance_df.loc[
    #         temporary_metadata_df[output_column] == unique_categories[0]]
    #     category_2_abundance_df = temporary_abundance_df.loc[
    #         temporary_metadata_df[output_column] == unique_categories[1]]
    # 
    #     abundance_selected_species = set(temporary_abundance_df.columns.tolist())
    #     prevalence_selected_species = abundance_selected_species.copy()
    # 
    #     abundance_threshold = 0
    #     prevalence_threshold = 0
    # 
    #     if abundanceThresholdInput.text():
    #         abundance_threshold = float(abundanceThresholdInput.text())
    #     if prevalenceThresholdInput.text():
    #         prevalence_threshold = float(
    #             prevalenceThresholdInput.text()) / 100  # Converting it into 0-1 from 0-100
    # 
    #     mean_abundance_category_1_df = category_1_abundance_df.mean(axis=0).sort_values(ascending=False)
    #     abundance_species_category_1_df = mean_abundance_category_1_df[
    #         mean_abundance_category_1_df > abundance_threshold].index.to_list()
    #     mean_abundance_category_2_df = category_2_abundance_df.mean(axis=0).sort_values(ascending=False)
    #     abundance_species_category_2_df = mean_abundance_category_2_df[
    #         mean_abundance_category_2_df > abundance_threshold].index.to_list()
    # 
    #     if preprocessing_abundance_both_checkbox.isChecked():
    #         abundance_selected_species = set(abundance_species_category_1_df).intersection(
    #             set(abundance_species_category_2_df))
    #     elif preprocessing_abundance_either_checkbox.isChecked():
    #         abundance_selected_species = set(abundance_species_category_1_df).union(
    #             set(abundance_species_category_2_df))
    # 
    #     # Prevalence threshold
    #     category_1_abundance_df = category_1_abundance_df.mask(category_1_abundance_df > 0, 1)
    #     category_2_abundance_df = category_2_abundance_df.mask(category_2_abundance_df > 0, 1)
    #     category_1_prevalence_df = category_1_abundance_df.mean(axis=0)
    #     category_2_prevalence_df = category_2_abundance_df.mean(axis=0)
    #     prevalence_species_category_1_df = category_1_prevalence_df[
    #         category_1_prevalence_df > prevalence_threshold].index.to_list()
    #     prevalence_species_category_2_df = category_2_prevalence_df[
    #         category_2_prevalence_df > prevalence_threshold].index.to_list()
    # 
    #     if preprocessing_prevalence_both_checkbox.isChecked():
    #         prevalence_selected_species = set(prevalence_species_category_1_df).intersection(
    #             set(prevalence_species_category_2_df))
    #     elif preprocessing_prevalence_either_checkbox.isChecked():
    #         prevalence_selected_species = set(prevalence_species_category_1_df).union(
    #             set(prevalence_species_category_2_df))
    # 
    #     final_processed_set_of_species = list(abundance_selected_species.intersection(prevalence_selected_species))
    #     self.data_file.feature_list_after_preprocessing = sorted(final_processed_set_of_species)
    #     output_abundance_dataframe = self.data_file.set_preprocessed_abundance_dataframe(
    #         self.data_file.input_abundance_dataframe[
    #             final_processed_set_of_species])
    # 
    #     output_labelDFShapeValue.setText(
    #         f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")
    # 
    #     # self.sa_shape_value_label.setText(
    #     #     f"{output_abundance_dataframe.shape[0]} rows x {output_abundance_dataframe.shape[1]} features")
    # 
    #     filteredTableView.setModel(PandasModel(output_abundance_dataframe))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
