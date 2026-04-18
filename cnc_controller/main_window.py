from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from .ui import Ui_Widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-code Viewer and CNC Control")
        
        self.setFixedSize(1400, 790)
        self.ui_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.ui_widget)
        self.ui = Ui_Widget()
        self.ui.setupUi(self.ui_widget)
