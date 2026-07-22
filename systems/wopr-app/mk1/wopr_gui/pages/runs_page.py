from __future__ import annotations

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

def RunsPage() -> QWidget:
    """The runs page
    Games
    Sessions
    Players
    """
    page = QWidget()
    label = QLabel("RUN")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 32px; font-weight: bold;")
    layout = QVBoxLayout(page)
    layout.addWidget(label)
    return page