from __future__ import annotations

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow

def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(43, 45, 48))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(214, 216, 218))
    palette.setColor(QPalette.ColorRole.Base, QColor(27, 29, 31))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 37, 39))
    #palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    #palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(214, 216, 218))
    palette.setColor(QPalette.ColorRole.Button, QColor(58, 61, 65))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(214, 216, 218))
    #palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 176, 0))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(27, 20, 0))
    return palette

def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())