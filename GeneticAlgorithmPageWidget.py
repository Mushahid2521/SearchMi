from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QTableView, QCheckBox, \
    QLineEdit, QGroupBox, QFrame, QProgressBar, QListWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QObject

import DataProcessing
from GeneticAlgorithm import GeneticAlgorithm
from mainwindow import PandasModel


class SearchWorker(QObject):
    signal_to_update_progress = pyqtSignal(int, int, float, list, bool)
    signal_to_pause_search = pyqtSignal()
    signal_to_stop_search = pyqtSignal()

    def __init__(self, ga_data):
        super().__init__()
        self.ga_data = ga_data
        self.search_running = False

    @pyqtSlot()
    def pause_search(self):
        self.search_running = not self.search_running
        self.signal_to_pause_search.emit()

    @pyqtSlot()
    def stop_search(self):
        self.search_running = False
        self.signal_to_stop_search.emit()

    def run_one_iteration(self):
        for i in range(self.ga_data.current_generation, self.ga_data.num_generations):
            if not self.search_running:
                break

            self.ga_data.run_one_iteration()
            generation_no = self.ga_data.current_generation
            cost_value = self.ga_data.tracking_generations[generation_no].get('best_score')

            # Add right panel species list
            best_solution = self.ga_data.tracking_generations[generation_no].get('best_solution')

            should_break = False
            if self.ga_data.stop_strategy:
                if (self.ga_data.improvement_patience - self.ga_data.no_improvement_counter) == 0:
                    should_break = True

            self.signal_to_update_progress.emit(i, generation_no, cost_value, best_solution, should_break)


class GeneticAlgorithmPageWidget(QWidget):
    signal_to_search_selection_page = pyqtSignal()

    signal_to_start_search = pyqtSignal()
    signal_to_pause_search = pyqtSignal()
    signal_to_stop_search = pyqtSignal()
    signal_to_update_progress = pyqtSignal(int, int, float, list, bool)

    def __init__(self, data: DataProcessing.DataFile, ga_data: GeneticAlgorithm, parent=None):
        """
        :param data: Shared dictionary or object for application data
        :param parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.search_running_thread = QThread()

        self.data_file = data  # Keep a reference to the shared data
        self.ga_data = ga_data
        self.init_ui()

    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel('Genetic Algorithm')
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Row for Input Data Shape
        shape_layout = QHBoxLayout()
        input_shape_label = QLabel("Data Shape:")
        self.input_shape_value = QLabel(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[1]} features")  # Example shape text
        shape_layout.addWidget(input_shape_label)
        shape_layout.addWidget(self.input_shape_value)
        shape_layout.addStretch()  # Add stretch to push contents to left
        main_layout.addLayout(shape_layout)

        self.start_search_button = QPushButton('🔎Search')
        self.start_search_button.clicked.connect(self.initiate_search)
        main_layout.addWidget(self.start_search_button)

        # Row for Generations
        gen_layout = QHBoxLayout()
        generations_label = QLabel("Generations:")
        self.current_gen_label = QLabel(f"0/{self.ga_data.num_generations}")  # Example current generations text
        gen_layout.addWidget(generations_label)
        gen_layout.addWidget(self.current_gen_label)
        gen_layout.addStretch()
        main_layout.addLayout(gen_layout)

        # Progress Bar for generation progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.ga_data.num_generations)  # Example maximum generation count
        self.progress_bar.setValue(0)  # Example current progress
        main_layout.addWidget(self.progress_bar)

        self.info_text_label = QLabel("")
        main_layout.addWidget(self.info_text_label)

        # Two parallel sections for results and species
        parallel_layout = QHBoxLayout()

        # Left section layout (Vertical with header and list)
        left_panel_layout = QVBoxLayout()
        cost_function_label = QLabel("Cost function")
        cost_function_label.setAlignment(Qt.AlignLeft)
        left_panel_layout.addWidget(cost_function_label)

        self.results_list = QListWidget()
        self.results_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_panel_layout.addWidget(self.results_list)

        parallel_layout.addLayout(left_panel_layout)

        # Right section layout (Vertical with header and list)
        right_panel_layout = QVBoxLayout()
        species_label = QLabel("Species combination")
        species_label.setAlignment(Qt.AlignLeft)
        right_panel_layout.addWidget(species_label)

        self.species_list = QListWidget()
        self.species_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel_layout.addWidget(self.species_list)

        # Function to handle click on items in the left panel and update self.species_list on the right

        # Connect the left panel's item click signal to the update function
        self.results_list.itemClicked.connect(self.updateSpeciesList)

        parallel_layout.addLayout(right_panel_layout)

        # for i in range(1, num_generations):
        #     self.ga_run_instance.run_one_iteration()
        #     generation_no = self.ga_run_instance.current_generation
        #     cost_value = self.ga_run_instance.tracking_generations[generation_no].get('best_score')
        #     self.results_list.addItem(0, f"Generation: {generation_no} | P-value: {cost_value}")
        #     self.results_list.scrollToTop()
        #
        #     # Add right panel species list
        #     best_solution = self.ga_run_instance.tracking_generations[generation_no].get('best_solution')
        #     for sp in best_solution:
        #         self.species_list.addItem(sp)
        #     self.species_list.scrollToTop()
        #
        #     self.progress_bar.setValue(i)

        main_layout.addLayout(parallel_layout)

        # Row for Pause and Stop buttons
        button_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(False)
        # self.pause_button.setStyleSheet("background-color: blue; color: white; padding: 6px;")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        # self.stop_button.setStyleSheet("background-color: red; color: white; padding: 6px;")
        self.back_button = QPushButton("Back")

        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        self.back_button.clicked.connect(self.back_to_search_selection_page)

        main_layout.addLayout(button_layout)

        # Threading code
        self.search_worker = SearchWorker(ga_data=self.ga_data)
        self.search_worker.moveToThread(self.search_running_thread)
        self.search_running_thread.started.connect(self.search_worker.run_one_iteration)
        self.search_worker.signal_to_update_progress.connect(self.update_search_progress)
        self.search_worker.signal_to_pause_search.connect(self.pause_the_search)
        self.search_worker.signal_to_stop_search.connect(self.stop_the_search)

        self.pause_button.clicked.connect(self.search_worker.pause_search)
        self.stop_button.clicked.connect(self.search_worker.stop_search)

        # Update the random seed
        self.ga_data.set_random_seed()

    def refresh_ui(self):
        self.search_running_thread = QThread()
        self.search_running_thread.started.connect(self.start_the_search_thread)

        self.start_search_button.setEnabled(True)
        self._search_running = True
        self.input_shape_value.setText(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x {self.data_file.preprocessed_abundance_dataframe.shape[1]} features")
        self.current_gen_label.setText(f"0/{self.ga_data.num_generations}")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.ga_data.num_generations)  # Example maximum generation count
        self.progress_bar.setValue(0)  # Example current progress
        self.info_text_label.setText("")
        self.results_list.clear()
        self.species_list.clear()

    def back_to_search_selection_page(self):
        self.search_running_thread.quit()
        self.search_running_thread.wait()
        self.search_running_thread = None
        self.ga_data.reinit_ga_data()
        self.signal_to_search_selection_page.emit()

    def stop_the_search(self):
        self.info_text_label.setText(
            f"INFO: Stopping search after finishing this generation!")
        self.pause_button.setEnabled(False)
        self.start_search_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.progress_bar.setValue(self.ga_data.num_generations)

    def pause_the_search(self):
        if self.search_worker.search_running == True:
            self.info_text_label.setText(
                f"INFO: Pausing after this generation is completed!")
            self.pause_button.setText("Resume")
        else:
            self.info_text_label.setText("")
            self.pause_button.setText("Pause")

    def initiate_search(self):
        self.start_search_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        if not self.search_running_thread.isRunning():
            self.search_worker.search_running = True
            self.search_running_thread.start()

    def start_the_search_thread(self):
        self._search_running = True
        self.keep_searching()

    def updateSpeciesList(self, item):
        # Clear the current species list
        # TODO, Fix this click item thing
        self.species_list.clear()
        index = self.results_list.row(item)
        reverse_index = max(self.ga_data.tracking_generations.keys()) - index
        this_solution = self.ga_data.tracking_generations[reverse_index].get('best_solution')
        for spp in this_solution:
            self.species_list.addItem(spp)
        self.species_list.scrollToTop()

    def update_search_progress(self, i, generation_no, cost_value, best_solution, should_break):
        self.results_list.scrollToTop()
        self.results_list.insertItem(0,
                                     f"Generation: {generation_no} | P-value: {cost_value} | Total: {len(best_solution)}")

        self.species_list.clear()
        for sp in best_solution:
            self.species_list.addItem(sp)

        self.species_list.scrollToTop()
        # QApplication.processEvents()

        self.current_gen_label.setText(f"{i + 1}/{self.ga_data.num_generations}")
        self.progress_bar.setValue(i + 1)

        # Update the Info label
        if self.ga_data.stop_strategy:
            if should_break:
                self.info_text_label.setText(
                    f"INFO: Stopped due to no improvement for {self.ga_data.no_improvement_counter} generations")
                self.pause_button.setEnabled(False)
                self.stop_button.setEnabled(False)
                self.back_button.setEnabled(True)

                self.current_gen_label.setText(f"{i + 1}/-")
                self.progress_bar.setValue(self.ga_data.num_generations)
                self.search_worker.stop_search()

            if (self.ga_data.improvement_patience - self.ga_data.no_improvement_counter) < int(
                    self.ga_data.improvement_patience):
                self.info_text_label.setText(
                    f"INFO: No improvement for last {self.ga_data.no_improvement_counter} generations")

        if i + 1 == self.ga_data.num_generations:
            pass
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.back_button.setEnabled(True)
            self.search_worker.stop_search()

    def keep_searching(self):
        for i in range(self.ga_data.current_generation, self.ga_data.num_generations):
            if not self._search_running:
                break

            self.ga_data.run_one_iteration()
            generation_no = self.ga_data.current_generation
            cost_value = self.ga_data.tracking_generations[generation_no].get('best_score')

            # Add right panel species list
            best_solution = self.ga_data.tracking_generations[generation_no].get('best_solution')

            should_break = False
            if self.ga_data.stop_strategy:
                if (self.ga_data.improvement_patience - self.ga_data.no_improvement_counter) == 0:
                    should_break = True

            self.signal_to_update_progress.emit(i, generation_no, cost_value, best_solution, should_break)

            # QApplication.processEvents()
