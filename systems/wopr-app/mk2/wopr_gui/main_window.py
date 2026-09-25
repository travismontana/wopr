from PySide6.QtWidgets import QMainWindow

from .lib import strings
from .lib.strings import basedata

strings.load("en")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(basedata("window.title"))
        self.resize(basedata("window.width"), basedata("window.height"))
