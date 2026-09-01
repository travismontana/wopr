from __future__ import annotations

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow

def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(43, 45, 48))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 176, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(27, 29, 31))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 37, 39))
    # palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    # palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(14, 216, 218))
    palette.setColor(QPalette.ColorRole.Button, QColor(58, 61, 65))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(214, 216, 218))
    # palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 176, 0))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(27, 20, 0))
    return palette


def wopr_palette() -> QPalette:
    p = QPalette()
    print("Setting WOPR palette...")
    # --- base chrome ---
    p.setColor(QPalette.ColorRole.Window, QColor("#2b2d30"))  # --chrome
    p.setColor(QPalette.ColorRole.WindowText, QColor("#d6d8da"))  # --text
    p.setColor(QPalette.ColorRole.Base, QColor("#1b1d1f"))  # --panel-deep
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#232527"))  # --panel

    # --- text in editable / list-y widgets ---
    p.setColor(QPalette.ColorRole.Text, QColor("#d6d8da"))  # --text
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8a8f96"))  # --text-dim

    # --- buttons ---
    p.setColor(QPalette.ColorRole.Button, QColor("#3a3d41"))  # --chrome-hi
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#ffb000"))  # --text

    # --- links (unused in source CSS, left as Qt default-ish) ---
    p.setColor(QPalette.ColorRole.Link, QColor("#2a82da"))

    # --- the one accent QPalette can give: pick ONE ---
    # Source CSS actually uses two different "selected" accents:
    #   --sel   #3d5a80 (blue)  -> table/card row selection
    #   --phosphor #ffb000 (amber) -> active mode-tab
    # QPalette.Highlight is a single global slot, so this is blue by
    # default (matches table/card selection, the more common case).
    # Flip to amber below if the tab look matters more than table rows.
    p.setColor(QPalette.ColorRole.Highlight, QColor("#3d5a80"))  # --sel
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#d6d8da"))
    # amber alternative:
    # p.setColor(QPalette.ColorRole.Highlight, QColor("#ffb000"))
    # p.setColor(QPalette.ColorRole.HighlightedText, QColor("#1b1400"))

    # --- bevel/border shading Fusion uses for frames & button edges ---
    p.setColor(QPalette.ColorRole.Mid, QColor("#44474c"))  # --line
    p.setColor(QPalette.ColorRole.Dark, QColor("#000000"))
    p.setColor(QPalette.ColorRole.Midlight, QColor("#3a3d41"))  #

    # --- disabled state carries --text-dim automatically this way ---
    dim = QColor("#8a8f96")
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        p.setColor(QPalette.ColorGroup.Disabled, role, dim)
    return p


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(wopr_palette())
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
