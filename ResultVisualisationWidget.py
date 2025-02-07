from PyQt5.QtWidgets import QWidget

import DataProcessing
from GeneticAlgorithm import GeneticAlgorithm


class GeneticAlgorithmPageWidget(QWidget):
    def __init__(self, data: DataProcessing.DataFile, ga_data: GeneticAlgorithm, parent=None):
        super().__init__(parent)
