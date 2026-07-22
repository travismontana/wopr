from __future__ import annotations

from PySide6.QtCore import Qt, QSettings, QThread
from PySide6.QtGui import QIcon, QActionGroup, QAction
from PySide6.QtWidgets import QMainWindow, QToolBar, QStackedWidget, QLabel

from .pages.calibrate_page import CalibratePage
from .pages.library_page import LibraryPage
from .pages.runs_page import RunsPage
from .pages.sessions_page import SessionsPage
from .pages.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("W.O.P.R. - Worldview Observation and Prediction Resource")
        self.resize(1200, 760)

        # -- Pages
        self.stack = QStackedWidget()
        self.stack.addWidget(CalibratePage())
        self.stack.addWidget(RunsPage())
        self.stack.addWidget(LibraryPage())
        self.stack.addWidget(SessionsPage())
        self.stack.addWidget(SettingsPage())

        self.setCentralWidget(self.stack)

        # -- Toolbar
        bar = QToolBar("Modes")
        bar.setObjectName("mode_toolbar")
        bar.setMovable(False)
        group = QActionGroup(self)
        for i, name in enumerate(("CALIBRATE", "RUN", "LIBRARY", "SESSIONS", "SETTINGS")):
            action = QAction(name, self, checkable=True, checked=(i == 0))
            action.triggered.connect(lambda _=False, idx=i: self.stack.setCurrentIndex(idx))
            group.addAction(action)
            bar.addAction(action)
        self.addToolBar(bar)


        # -- Status bar
        self.label_fps = QLabel("CAM - ")
        self.label_infer = QLabel("INFER - ")
        self.label_state = QLabel("STATE - ")
        for w in (self.label_fps, self.label_infer, self.label_state):
            w.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.statusBar().addPermanentWidget(w)