# import sys
#
# from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
# from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QApplication
#
#
# class Worker(QObject):
#     progress_signal = pyqtSignal(str)
#     paused_signal = pyqtSignal(bool)  # True when paused, False when resumed
#     stopped_signal = pyqtSignal()
#
#     def __init__(self):
#         super().__init__()
#         self._stop_requested = False
#         self._pause_requested = False
#
#     @pyqtSlot()
#     def stop(self):
#         self._stop_requested = True
#         # Optionally emit a signal right here if you want immediate notification
#         # self.stopped_signal.emit()
#
#     @pyqtSlot()
#     def toggle_pause(self):
#         self._pause_requested = not self._pause_requested
#         # Emit paused_signal to let the main thread know the new state
#         self.paused_signal.emit(self._pause_requested)
#
#     def do_work(self):
#         while not self._stop_requested:
#             if self._pause_requested:
#                 # If paused, just sleep a bit in a loop
#                 QThread.msleep(100)
#                 continue
#
#             # Do some "work"
#             self.progress_signal.emit("Working...")
#             QThread.msleep(500)
#
#         # Once we exit the loop, we are stopped
#         self.stopped_signal.emit()
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         ...
#         self.worker = Worker()
#         self.thread = QThread()
#         self.worker.moveToThread(self.thread)
#
#         # Start the worker when the thread starts
#         self.thread.started.connect(self.worker.do_work)
#         self.thread.start()
#
#         # Connect signals from the worker to slots in MainWindow
#         self.worker.progress_signal.connect(self.on_progress)
#         self.worker.paused_signal.connect(self.on_worker_paused)
#         self.worker.stopped_signal.connect(self.on_worker_stopped)
#
#         # Buttons
#         self.btn_pause = QPushButton("Pause")
#         self.btn_pause.clicked.connect(self.worker.toggle_pause)  # triggers pause/resume
#         self.btn_stop = QPushButton("Stop")
#         self.btn_stop.clicked.connect(self.worker.stop)
#
#         self.status_label = QLabel("Ready...")
#
#     def on_progress(self, text):
#         self.status_label.setText(text)
#
#     def on_worker_paused(self, is_paused):
#         if is_paused:
#             self.status_label.setText("Worker is PAUSED")
#             self.btn_pause.setText("Resume")
#         else:
#             self.status_label.setText("Worker is RUNNING")
#             self.btn_pause.setText("Pause")
#
#     def on_worker_stopped(self):
#         self.status_label.setText("Worker has STOPPED")
#         self.btn_pause.setEnabled(False)
#         self.btn_stop.setEnabled(False)
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
