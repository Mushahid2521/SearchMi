import sys
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QTableView,
    QVBoxLayout, QWidget
)


class PandasModel(QAbstractTableModel):
    """A model to interface a pandas DataFrame with a QTableView."""
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self._df.iat[row, col])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._df.columns[section]
        else:
            return str(self._df.index[section])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pandas DataFrame Viewer")

        # Create a central widget to hold our table
        self.table_view = QTableView()
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initially, no data loaded
        self.model = PandasModel(pd.DataFrame())
        self.table_view.setModel(self.model)

        # Create menu bar and actions
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        import_action = QAction("Import CSV", self)
        import_action.triggered.connect(self.import_csv)
        file_menu.addAction(import_action)

    def import_csv(self):
        """Open a file dialog to import a CSV and display it in the table."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            try:
                df = pd.read_csv(file_name)
                self.model = PandasModel(df)
                self.table_view.setModel(self.model)
            except Exception as e:
                # In a real app, you might show a dialog with the error
                print("Error loading file:", e)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

