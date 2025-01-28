from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QProgressBar, \
    QListWidget
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QObject, QTimer

import DataProcessing
from GeneticAlgorithm import GeneticAlgorithm


class SearchWorker(QObject):
    signal_to_update_progress = pyqtSignal(int, int, float, list, bool)
    signal_to_pause_search = pyqtSignal()
    signal_to_stop_search = pyqtSignal(str)

    def __init__(self, ga_data):
        super().__init__()
        self.ga_data = ga_data
        self.search_running = False
        self.timer = None  # Initialize timer as None

    @pyqtSlot()
    def init_timer(self):
        """Initialize QTimer within the worker thread."""
        self.timer = QTimer()
        self.timer.setInterval(0)  # Execute as soon as possible
        self.timer.timeout.connect(self.process_iteration)

    @pyqtSlot()
    def start_search(self):
        """Start the search by initializing and starting the timer."""
        if not self.timer:
            self.init_timer()
        self.search_running = True
        self.timer.start()

    @pyqtSlot()
    def pause_search(self):
        """Toggle the search running state and manage the timer accordingly."""
        self.search_running = not self.search_running
        self.signal_to_pause_search.emit()
        if self.search_running:
            # self.info_message = "INFO: Paused"
            self.timer.start()
        else:
            self.info_message = "INFO: Paused!"
            self.timer.stop()

    @pyqtSlot()
    def stop_search(self):
        """Stop the search by stopping the timer and emitting a stop signal."""
        self.search_running = False
        self.info_message = "INFO: Stopping search after finishing this generation!"
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.signal_to_stop_search.emit("stop_pressed")

    def process_iteration(self):
        """Process a single iteration of the genetic algorithm."""
        if not self.search_running:
            return  # Do nothing if paused

        # Run one iteration
        self.ga_data.run_one_iteration()
        generation_no = self.ga_data.current_generation
        cost_value = self.ga_data.tracking_generations[generation_no].get('best_score')
        best_solution = self.ga_data.tracking_generations[generation_no].get('best_solution')

        should_break = False
        if self.ga_data.stop_strategy:
            if (self.ga_data.improvement_patience - self.ga_data.no_improvement_counter) == 0:
                should_break = True

        current_gen = self.ga_data.current_generation

        # Emit progress signal
        self.signal_to_update_progress.emit(
            current_gen,
            generation_no,
            cost_value,
            best_solution,
            should_break
        )

        if current_gen >= self.ga_data.num_generations:
            self.timer.stop()
            self.signal_to_stop_search.emit("finished")
            return

        if should_break:
            self.timer.stop()
            self.signal_to_stop_search.emit("no_improvement")


class GeneticAlgorithmPageWidget(QWidget):
    signal_to_search_selection_page = pyqtSignal()

    def __init__(self, data: DataProcessing.DataFile, ga_data: GeneticAlgorithm, parent=None):
        super().__init__(parent)
        self.search_running_thread = None
        self.search_worker = None
        self.data_file = data
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

        self.results_list.itemClicked.connect(self.updateSpeciesList)

        parallel_layout.addLayout(right_panel_layout)

        main_layout.addLayout(parallel_layout)

        # Row for Pause and Stop buttons
        button_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.back_button = QPushButton("Back")

        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        self.back_button.clicked.connect(self.back_to_search_selection_page)

        main_layout.addLayout(button_layout)

        # Threading code
        self.initiate_threading()

        # Update the random seed
        self.ga_data.set_random_seed()

    def initiate_threading(self):
        """Initialize the worker and thread, and connect signals."""
        self.search_worker = SearchWorker(ga_data=self.ga_data)
        self.search_running_thread = QThread()
        self.search_worker.moveToThread(self.search_running_thread)

        # Connect thread's started signal to worker's start_search
        self.search_running_thread.started.connect(self.search_worker.start_search)

        # Connect worker signals to UI slots
        self.search_worker.signal_to_update_progress.connect(self.update_search_progress)
        self.search_worker.signal_to_pause_search.connect(self.pause_the_search)
        self.search_worker.signal_to_stop_search.connect(self.stop_the_search)

        # Connect UI buttons to worker slots
        self.pause_button.clicked.connect(self.search_worker.pause_search)
        self.stop_button.clicked.connect(self.search_worker.stop_search)

    def refresh_ui(self):
        """Reset the UI and re-initialize threading if necessary."""
        # Stop and clean up existing thread and worker if running
        if self.search_running_thread and self.search_running_thread.isRunning():
            self.search_worker.stop_search()
            self.search_running_thread.quit()
            self.search_running_thread.wait()

        # Re-initiate threading
        self.initiate_threading()

        self.start_search_button.setEnabled(True)
        self.input_shape_value.setText(
            f"{self.data_file.preprocessed_abundance_dataframe.shape[0]} rows x "
            f"{self.data_file.preprocessed_abundance_dataframe.shape[1]} features")
        self.current_gen_label.setText(f"0/{self.ga_data.num_generations}")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.ga_data.num_generations)
        self.progress_bar.setValue(0)
        self.info_text_label.setText("")
        self.results_list.clear()
        self.species_list.clear()

    def back_to_search_selection_page(self):
        """Handle navigation back to the search selection page."""
        if self.search_running_thread and self.search_running_thread.isRunning():
            self.search_worker.stop_search()
            self.search_running_thread.quit()
            self.search_running_thread.wait()
        self.search_running_thread = None
        self.ga_data.reinit_ga_data()
        self.signal_to_search_selection_page.emit()

    def stop_the_search(self, flag):
        """Handle the stop signal from the worker."""
        if flag == "stop_pressed":
            self.info_text_label.setText(
                "INFO: Search stopped")
            self.current_gen_label.setText(f"{self.ga_data.current_generation}/-")
        else:
            self.info_text_label.setText(
                "INFO: " + "Finished | " + f"No improvement in last {self.ga_data.no_improvement_counter} generations")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.start_search_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.progress_bar.setValue(self.ga_data.num_generations)

    def pause_the_search(self):
        """Handle the pause signal from the worker."""
        if self.search_worker.search_running:
            self.info_text_label.setText("")
            self.pause_button.setText("Pause")
        else:
            self.info_text_label.setText("INFO: Search paused!")
            self.pause_button.setText("Resume")

    def initiate_search(self):
        """Start the search by starting the worker thread."""
        self.start_search_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        if not self.search_running_thread.isRunning():
            self.search_running_thread.start()

    def updateSpeciesList(self, item):
        # Clear the current species list
        self.species_list.clear()
        index = self.results_list.row(item)
        reverse_index = abs(max(self.ga_data.tracking_generations.keys()) - index)
        this_solution = self.ga_data.tracking_generations[reverse_index].get('best_solution')
        for spp in this_solution:
            self.species_list.addItem(spp)
        self.species_list.scrollToTop()

    def update_search_progress(self, i, generation_no, cost_value, best_solution, should_break):
        """Update the UI with the latest search progress."""
        self.results_list.scrollToTop()
        self.results_list.insertItem(0,
                                     f"Generation: {generation_no} | P-value: {cost_value} | Total: {len(best_solution)}")

        self.species_list.clear()
        for sp in best_solution:
            self.species_list.addItem(sp)
        self.species_list.scrollToTop()

        self.current_gen_label.setText(f"{generation_no}/{self.ga_data.num_generations}")
        self.progress_bar.setValue(i + 1)

        # Update the Info label
        if should_break:
            self.info_text_label.setText(
                f"INFO: Stopped due to no improvement for {self.ga_data.no_improvement_counter} generations")
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.back_button.setEnabled(True)
            self.current_gen_label.setText(f"{generation_no}/-")
            self.progress_bar.setValue(self.ga_data.num_generations)
            self.search_worker.stop_search()

        elif (
                self.ga_data.improvement_patience - self.ga_data.no_improvement_counter) < self.ga_data.improvement_patience:
            self.info_text_label.setText(
                f"INFO: No improvement for last {self.ga_data.no_improvement_counter} generations")
