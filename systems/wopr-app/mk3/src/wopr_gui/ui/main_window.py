from wopr_gui import strings as S
from wopr_gui import defaults as D

from PySide6.QtWidgets import (
    QMainWindow
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        win_title = S.APP_TITLE
        self.setWindowTitle(win_title)
        self.resize(D.WINDOW_SIZE_WIDTH, D.WINDOW_SIZE_HEIGHT)
