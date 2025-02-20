from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QTableView, QCheckBox, \
    QLineEdit, QGroupBox, QFrame, QFormLayout, QComboBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, pyqtSignal

import DataProcessing
from GeneticAlgorithm import GeneticAlgorithm
from SimulatedAnnealing import SimulatedAnnealing
from mainwindow import PandasModel


class SearchSelectionPageWidget(QWidget):
    signal_to_preprocessing_page = pyqtSignal()
    signal_to_ga_page = pyqtSignal()
    signal_to_sa_page = pyqtSignal()

    def __init__(self, data: DataProcessing.DataFile, ga_data: GeneticAlgorithm, sa_data: SimulatedAnnealing,
                 parent=None):
        """
        :param data: Shared dictionary or object for application data
        :param parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.data_file = data  # Keep a reference to the shared data
        self.genetic_algorithm_data = ga_data
        self.simulated_annealing_data = sa_data
        self.init_ui()

    def init_ui(self):
        search_algorithm_layout = QVBoxLayout(self)

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
        self.sa_shape_value_label = QLabel(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[1]} features")
        data_shape_layout.addWidget(data_shape_label)
        data_shape_layout.addWidget(self.sa_shape_value_label)
        data_shape_layout.addStretch()
        search_algorithm_layout.addLayout(data_shape_layout)

        # --- Algorithm selection checkboxes ---
        algo_selection_layout = QHBoxLayout()
        self.genetic_checkbox = QCheckBox("Genetic Search")
        self.sa_checkbox = QCheckBox("Simulated Annealing")

        algo_selection_layout.addWidget(self.genetic_checkbox)
        algo_selection_layout.addWidget(self.sa_checkbox)
        algo_selection_layout.addStretch()
        search_algorithm_layout.addLayout(algo_selection_layout)

        # --- Parameter sections (group boxes) ---
        # Create group and layout
        genetic_params_group = QGroupBox("Genetic Algorithm Parameters")
        genetic_params_layout = QFormLayout()

        # Create line edits with default values
        # Rule of thumb to population size being K x C
        pop_begin = self.data_file.preprocessed_abundance_dataframe.shape[1] * 4
        self.genetic_pop_size = QLineEdit(str(pop_begin))
        parents_begin = int(pop_begin * 0.70)
        self.genetic_num_parents = QLineEdit(str(parents_begin))
        self.genetic_seed = QLineEdit("42")

        # Add the population size row as is
        genetic_params_layout.addRow("Population size:", self.genetic_pop_size)

        # Create checkboxes and corresponding QLineEdits for options
        self.custom_checkbox = QCheckBox("Custom")
        self.custom_generation_edit = QLineEdit("50")
        self.custom_generation_edit.setEnabled(False)  # disabled initially

        self.continue_checkbox = QCheckBox("Continue till no improvement for generations")
        self.improvement_edit = QLineEdit("10")
        self.improvement_edit.setEnabled(False)  # disabled initially

        # Set "Continue till no improvement for" as checked by default
        self.continue_checkbox.setChecked(True)
        self.improvement_edit.setEnabled(True)

        # Connect toggled signals to enable/disable corresponding QLineEdits
        self.custom_checkbox.toggled.connect(self.custom_generation_edit.setEnabled)
        self.continue_checkbox.toggled.connect(self.improvement_edit.setEnabled)

        # Ensure that when one checkbox is enabled, the other becomes disabled
        def on_custom_toggled(checked):
            # If Custom is checked, disable Continue option, else enable it.
            # self.continue_checkbox.setDisabled(checked)
            self.continue_checkbox.setChecked(not checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        def on_continue_toggled(checked):
            # If Continue is checked, disable Custom option, else enable it.
            # self.custom_checkbox.setDisabled(checked)
            self.custom_checkbox.setChecked(not checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        self.custom_checkbox.toggled.connect(on_custom_toggled)
        self.continue_checkbox.toggled.connect(on_continue_toggled)

        # Layout for the "Custom" option row
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.custom_checkbox)
        custom_layout.addWidget(self.custom_generation_edit)
        genetic_params_layout.addRow("Number of generations:", custom_layout)

        # Layout for the "Continue till no improvement for" option
        continue_layout = QHBoxLayout()
        continue_layout.addWidget(self.continue_checkbox)
        continue_layout.addWidget(self.improvement_edit)
        genetic_params_layout.addRow("", continue_layout)

        # Add remaining rows
        genetic_params_layout.addRow("Number of parents:", self.genetic_num_parents)
        genetic_params_layout.addRow("Seed:", self.genetic_seed)

        genetic_params_group.setLayout(genetic_params_layout)

        # ------- Simulated Annealing parameters ------- #
        sa_params_group = QGroupBox("Simulated Annealing Parameters")
        sa_params_layout = QFormLayout()

        self.sa_num_iterations = QLineEdit("1000")
        self.sa_temperature = QLineEdit("100.0")
        self.sa_cooling_rate = QLineEdit("0.95")
        self.sa_seed = QLineEdit("42")

        # sa_params_layout.addRow("Number of Iterations:", self.sa_num_iterations)
        sa_params_layout.addRow("Temperature:", self.sa_temperature)
        sa_params_layout.addRow("Cooling Rate:", self.sa_cooling_rate)

        # Create checkboxes and corresponding QLineEdits for options
        self.custom_checkbox_sa = QCheckBox("Custom")
        self.custom_generation_edit_sa = QLineEdit("1000")
        self.custom_generation_edit_sa.setEnabled(False)  # disabled initially

        self.continue_checkbox_sa = QCheckBox("Continue till no improvement for generations")
        self.improvement_edit_sa = QLineEdit("100")
        self.improvement_edit_sa.setEnabled(False)  # disabled initially

        # Set "Continue till no improvement for" as checked by default
        self.continue_checkbox_sa.setChecked(True)
        self.improvement_edit_sa.setEnabled(True)

        # Connect toggled signals to enable/disable corresponding QLineEdits
        self.custom_checkbox_sa.toggled.connect(self.custom_generation_edit_sa.setEnabled)
        self.continue_checkbox_sa.toggled.connect(self.improvement_edit_sa.setEnabled)

        # Ensure that when one checkbox is enabled, the other becomes disabled
        def on_custom_toggled_sa(checked):
            # If Custom is checked, disable Continue option, else enable it.
            # self.continue_checkbox_sa.setDisabled(checked)
            self.continue_checkbox_sa.setChecked(not checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        def on_continue_toggled_sa(checked):
            # If Continue is checked, disable Custom option, else enable it.
            # self.custom_checkbox_sa.setDisabled(checked)
            self.custom_checkbox_sa.setChecked(not checked)
            if not checked:
                # Reset focus or state if needed when unchecked
                pass

        self.custom_checkbox_sa.toggled.connect(on_custom_toggled_sa)
        self.continue_checkbox_sa.toggled.connect(on_continue_toggled_sa)

        # Layout for the "Custom" option row
        custom_layout_sa = QHBoxLayout()
        custom_layout_sa.addWidget(self.custom_checkbox_sa)
        custom_layout_sa.addWidget(self.custom_generation_edit_sa)
        sa_params_layout.addRow("Number of iterations:", custom_layout_sa)

        # Layout for the "Continue till no improvement for" option
        continue_layout_sa = QHBoxLayout()
        continue_layout_sa.addWidget(self.continue_checkbox_sa)
        continue_layout_sa.addWidget(self.improvement_edit_sa)
        sa_params_layout.addRow("", continue_layout_sa)

        sa_params_layout.addRow("Seed:", self.sa_seed)
        sa_params_group.setLayout(sa_params_layout)

        # By default, hide both parameter groups (shown when checkbox is checked)
        genetic_params_group.setVisible(False)
        sa_params_group.setVisible(False)

        search_algorithm_layout.addWidget(genetic_params_group)
        search_algorithm_layout.addWidget(sa_params_group)

        # Look for the group numbers
        if len(self.data_file.output_label_groups) == 2:
            self.populate_two_group_stats(search_algorithm_layout)
        elif len(self.data_file.output_label_groups) == 3:
            self.populate_three_group_stats(search_algorithm_layout)

        # --- Logic to enable/disable parameter sections based on selection ---
        def on_genetic_toggled(checked):
            if checked:
                # Uncheck the other checkbox
                self.sa_checkbox.setChecked(False)
                # Show genetic parameters, hide SA parameters
                genetic_params_group.setVisible(True)
                sa_params_group.setVisible(False)
            else:
                genetic_params_group.setVisible(False)

        def on_sa_toggled(checked):
            if checked:
                # Uncheck the other checkbox
                self.genetic_checkbox.setChecked(False)
                # Show SA parameters, hide Genetic parameters
                sa_params_group.setVisible(True)
                genetic_params_group.setVisible(False)
            else:
                sa_params_group.setVisible(False)

        self.genetic_checkbox.toggled.connect(on_genetic_toggled)
        self.sa_checkbox.toggled.connect(on_sa_toggled)
        self.genetic_checkbox.setChecked(True)

        # # Adjust stretching or spacing if needed
        # search_algorithm_layout.addStretch()

        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.search_button = QPushButton("Search")

        # Add them side by side
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.search_button)
        self.back_button.clicked.connect(self.go_to_preprocessing_page)
        self.search_button.clicked.connect(self.choosing_search_algorithm_page)

        # Ensure everything above stays at top, buttons at bottom
        search_algorithm_layout.addStretch()
        search_algorithm_layout.addLayout(button_layout)

        # self.search_algorithm_design_page.setLayout(search_algorithm_layout)

    def populate_three_group_stats(self, search_algorithm_layout):
        # --- Objective function / statistics selection ---
        obj_func_group = QGroupBox("Objective Function / Statistics")
        obj_func_layout = QVBoxLayout()

        # 2) Test selection (ComboBox)
        test_label = QLabel("Select test:")
        self.obj_func_combo = QComboBox()
        self.obj_func_combo.addItems(["One Way-ANOVA", "Kruskal-Wallis H-test"])  # Add more as needed # "Welch's ANOVA"

        obj_func_layout.addWidget(test_label)
        obj_func_layout.addWidget(self.obj_func_combo)

        obj_func_group.setLayout(obj_func_layout)
        search_algorithm_layout.addWidget(obj_func_group)

    def populate_two_group_stats(self, search_algorithm_layout):
        # --- Objective function / statistics selection ---
        obj_func_group = QGroupBox("Objective Function / Statistics")
        obj_func_layout = QVBoxLayout()

        # 2) Test selection (ComboBox)
        test_label = QLabel("Select test:")
        self.obj_func_combo = QComboBox()
        self.obj_func_combo.addItems(["Mann-Whitney U-test", "Welch's T-test"])  # Add more as needed

        obj_func_layout.addWidget(test_label)
        obj_func_layout.addWidget(self.obj_func_combo)

        # 3) Hypothesis selection (Radio Buttons)
        hypothesis_groupbox = QGroupBox("Hypothesis")
        hypothesis_layout = QHBoxLayout()

        self.two_sided_radio = QRadioButton("Two sided")
        self.one_sided_radio = QRadioButton("One sided")

        # Add them to a ButtonGroup so only one can be selected
        hypothesis_btn_group = QButtonGroup()
        hypothesis_btn_group.addButton(self.two_sided_radio)
        hypothesis_btn_group.addButton(self.one_sided_radio)

        # Default to "Two sided"
        self.two_sided_radio.setChecked(True)

        hypothesis_layout.addWidget(self.two_sided_radio)
        hypothesis_layout.addWidget(self.one_sided_radio)
        hypothesis_groupbox.setLayout(hypothesis_layout)
        obj_func_layout.addWidget(hypothesis_groupbox)

        # 4) Positive/Negative Signature (Radio Buttons), initially hidden
        signature_group = QGroupBox("Signature type")
        signature_layout = QHBoxLayout()

        self.positive_radio = QRadioButton("Positive signatures")
        self.negative_radio = QRadioButton("Negative signatures")

        # Put them in a button group to be mutually exclusive
        signature_btn_group = QButtonGroup()
        signature_btn_group.addButton(self.positive_radio)
        signature_btn_group.addButton(self.negative_radio)

        # One of them can be default
        self.positive_radio.setChecked(True)

        signature_layout.addWidget(self.positive_radio)
        signature_layout.addWidget(self.negative_radio)
        signature_group.setLayout(signature_layout)

        # Start hidden unless "One sided" is chosen
        signature_group.setVisible(False)
        obj_func_layout.addWidget(signature_group)

        # 5) Control Group selection, initially hidden
        control_group_box = QGroupBox("Control Group")
        control_group_layout = QHBoxLayout()

        self.groupA_radio = QRadioButton(self.data_file.output_label_groups[0])
        self.groupB_radio = QRadioButton(self.data_file.output_label_groups[1])

        # Put them in a button group
        control_group_btn_group = QButtonGroup()
        control_group_btn_group.addButton(self.groupA_radio)
        control_group_btn_group.addButton(self.groupB_radio)

        # Choose one of them by default
        self.groupA_radio.setChecked(True)

        control_group_layout.addWidget(self.groupA_radio)
        control_group_layout.addWidget(self.groupB_radio)
        control_group_box.setLayout(control_group_layout)

        # Start hidden unless "One sided" is chosen
        control_group_box.setVisible(False)
        obj_func_layout.addWidget(control_group_box)

        # 6) Connect signals to show/hide "Signature" and "Control Group"
        def on_hypothesis_changed():
            if self.one_sided_radio.isChecked():
                signature_group.setVisible(True)
                control_group_box.setVisible(True)
            else:
                signature_group.setVisible(False)
                control_group_box.setVisible(False)

        self.two_sided_radio.toggled.connect(on_hypothesis_changed)
        self.one_sided_radio.toggled.connect(on_hypothesis_changed)
        on_hypothesis_changed()  # Ensure correct initial state

        # Finalize the Objective Function group layout
        obj_func_group.setLayout(obj_func_layout)

        # Finally, add 'obj_func_group' to the parent layout
        search_algorithm_layout.addWidget(obj_func_group)

    def refresh_ui(self):
        pop_begin = self.data_file.preprocessed_abundance_dataframe.shape[1] * 4
        self.genetic_pop_size.setText(str(pop_begin))
        parents_begin = int(pop_begin * 0.70)
        self.genetic_num_parents.setText(str(parents_begin))

        self.sa_shape_value_label.setText(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[1]} features")

    def go_to_preprocessing_page(self):
        self.signal_to_preprocessing_page.emit()

    def choosing_search_algorithm_page(self):
        if self.genetic_checkbox.isChecked():
            hypothesis_selection = 'two-sided'
            positive_category = "" # str(self.groupA_radio.text())
            signature_type = 'positive'
            stop_strategy = False
            improvement_patience = 10

            if self.continue_checkbox.isChecked():
                stop_strategy = True
                improvement_patience = int(self.improvement_edit.text())
                number_of_generations = 300
            else:
                number_of_generations = int(self.custom_generation_edit.text())

            if len(self.data_file.output_label_groups) == 2:
                if self.two_sided_radio.isChecked():
                    hypothesis_selection = 'two-sided'
                elif self.one_sided_radio.isChecked():
                    hypothesis_selection = 'one-sided'
                    signature_type = 'positive'
                    if self.negative_radio.isChecked():
                        signature_type = 'negative'
                    if self.groupA_radio.isChecked():
                        positive_category = str(self.groupA_radio.text())

            self.genetic_algorithm_data.search_abundance = self.data_file.preprocessed_abundance_dataframe.copy()
            self.genetic_algorithm_data.search_abundance[self.genetic_algorithm_data.search_abundance > 0] = 1
            self.genetic_algorithm_data.metadata = self.data_file.input_metadata_dataframe
            self.genetic_algorithm_data.output_column = self.data_file.output_labels[0]
            self.genetic_algorithm_data.soi_list = self.data_file.feature_list_after_preprocessing
            self.genetic_algorithm_data.positive_label = positive_category
            self.genetic_algorithm_data.output_label_categories = self.data_file.output_label_groups
            self.genetic_algorithm_data.hypothesis_selection = hypothesis_selection
            self.genetic_algorithm_data.signature_type = signature_type
            self.genetic_algorithm_data.pop_size = int(self.genetic_pop_size.text())
            self.genetic_algorithm_data.num_generations = number_of_generations  # TODO change this
            self.genetic_algorithm_data.num_parents = int(self.genetic_num_parents.text())
            self.genetic_algorithm_data.objective_function = str(self.obj_func_combo.currentText())
            self.genetic_algorithm_data.stop_strategy = stop_strategy
            self.genetic_algorithm_data.improvement_patience = improvement_patience
            self.genetic_algorithm_data.random_seed = int(self.genetic_seed.text())

            self.signal_to_ga_page.emit()

        elif self.sa_checkbox.isChecked():
            hypothesis_selection = 'two-sided'
            positive_category = "" # str(self.groupA_radio.text())
            signature_type = 'positive'
            stop_strategy = False
            improvement_patience = 100

            if self.continue_checkbox_sa.isChecked():
                stop_strategy = True
                improvement_patience = int(self.improvement_edit_sa.text())
                number_of_iterations = 1000
            else:
                number_of_iterations = int(self.custom_generation_edit_sa.text())

            if len(self.data_file.output_label_groups) == 2:
                if self.two_sided_radio.isChecked():
                    hypothesis_selection = 'two-sided'
                elif self.one_sided_radio.isChecked():
                    hypothesis_selection = 'one-sided'
                    signature_type = 'positive'
                    if self.negative_radio.isChecked():
                        signature_type = 'negative'
                    if self.groupA_radio.isChecked():
                        positive_category = str(self.groupA_radio.text())

            self.simulated_annealing_data.search_abundance = self.data_file.preprocessed_abundance_dataframe.copy()
            self.simulated_annealing_data.search_abundance[self.simulated_annealing_data.search_abundance > 0] = 1
            self.simulated_annealing_data.metadata = self.data_file.input_metadata_dataframe
            self.simulated_annealing_data.output_column = self.data_file.output_labels[0]
            self.simulated_annealing_data.soi_list = self.data_file.feature_list_after_preprocessing
            self.simulated_annealing_data.positive_label = positive_category
            self.simulated_annealing_data.output_label_categories = self.data_file.output_label_groups
            self.simulated_annealing_data.hypothesis_selection = hypothesis_selection
            self.simulated_annealing_data.objective_function = str(self.obj_func_combo.currentText())
            self.simulated_annealing_data.signature_type = signature_type
            self.simulated_annealing_data.no_iterations = number_of_iterations
            self.simulated_annealing_data.temp = float(self.sa_temperature.text())
            self.simulated_annealing_data.cooling_rate = float(self.sa_cooling_rate.text())
            self.simulated_annealing_data.stop_strategy = stop_strategy
            self.simulated_annealing_data.improvement_patience = improvement_patience
            self.simulated_annealing_data.random_seed = int(self.sa_seed.text())

            self.signal_to_sa_page.emit()
