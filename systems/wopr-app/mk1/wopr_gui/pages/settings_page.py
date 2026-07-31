from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QInputDialog,
)
from PySide6.QtCore import Qt

from ..lib.config import AppSettings
from ..lib.camera import list_attached_cameras


def _config_dir_row(current_path: Path, on_change) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)

    field = QLineEdit(str(current_path))
    field.setReadOnly(True)  # path picked via dialog, not typed free-hand

    browse_btn = QPushButton("Browse…")

    def choose_dir():
        chosen = QFileDialog.getExistingDirectory(
            row, "Select config directory", str(current_path)
        )
        if chosen:
            field.setText(chosen)
            on_change(Path(chosen))

    browse_btn.clicked.connect(choose_dir)

    layout.addWidget(field)
    layout.addWidget(browse_btn)
    return row


def _db_file_row(current_path: Path, on_change) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)

    field = QLineEdit(str(current_path))
    field.setReadOnly(True)  # path picked via dialog, not typed free-hand

    browse_btn = QPushButton("Browse…")

    def choose_file():
        chosen, _ = QFileDialog.getOpenFileName(
            row, "Select database file", str(current_path), "Database Files (*.db)"
        )
        if chosen:
            field.setText(chosen)
            on_change(Path(chosen))

    browse_btn.clicked.connect(choose_file)

    layout.addWidget(field)
    layout.addWidget(browse_btn)
    return row


def _camera_select_row(current_index: int, camera_dict: dict, on_change) -> QWidget:
    # needs to have a drop down list of attached cameras, and a button to refresh the list
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    field = QLineEdit(str(current_index))
    field.setReadOnly(True)  # index picked via dialog, not typed free-hand

    browse_btn = QPushButton("Select…")

    def choose_camera():
        cameras = list_attached_cameras()
        if not cameras:
            field.setText("No cameras found")
            return
        # display string -> index, so the picked label can be mapped back
        display_to_index = {
            f"{idx}: {info['name']} ({info['path']})": idx
            for idx, info in cameras.items()
        }
        items = list(display_to_index.keys())

        try:
            current_position = list(cameras.keys()).index(current_index)
        except ValueError:
            current_position = 0

        chosen, ok = QInputDialog.getItem(
            row,
            "Select camera",
            "Available cameras:",
            items,
            current=current_position,
            editable=False,
        )
        if ok and chosen:
            index = display_to_index[chosen]
            field.setText(str(index))
            on_change(index)
            AppSettings().camera_index = index

    layout.addWidget(field)
    browse_btn.clicked.connect(choose_camera)
    layout.addWidget(browse_btn)
    return row


def _first_run() -> QWidget:
    # placeholder for first-run setup logic, e.g., creating config directory, initializing database, etc.
    row = QWidget()
    return row


def _settings_group(title: str, rows: list[tuple[str, QWidget]]) -> QGroupBox:
    """One bordered, titled section of the settings page. Adding a new
    group later is just another call to this with its own row list."""
    group = QGroupBox(title)
    form = QFormLayout(group)
    for label, widget in rows:
        form.addRow(label, widget)
    return group


def SettingsPage() -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)

    title = QLabel("SETTINGS")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 32px; font-weight: bold;")
    layout.addWidget(title)

    # Deferred -- config_directory/config_file aren't wired into the UI
    # yet. Revisit once that group's fields are settled.
    # config_dir_row = _config_dir_row(
    #    current_path=Path(AppSettings().config_directory),
    #    on_change=lambda p: print(f"config dir -> {p}"),  # placeholder for save()
    # )
    # config_file_row = _db_file_row(
    #    current_path=Path(AppSettings().config_file),
    #    on_change=lambda p: print(f"config file -> {p}"),  # placeholder for save()
    # )

    # db_dir_row will set the directory for the database.
    # and db_file_row will set the specific database file within that directory.
    db_dir_row = _config_dir_row(
        current_path=Path(AppSettings().db_directory),
        on_change=lambda p: print(f"db dir -> {p}"),  # placeholder for save()
    )
    db_file_row = _db_file_row(
        current_path=Path(AppSettings().db_file),
        on_change=lambda p: print(f"db file -> {p}"),  # placeholder for save()
    )
    db_group = _settings_group(
        "Database",
        [
            ("Database directory:", db_dir_row),
            ("Database file:", db_file_row),
        ],
    )
    layout.addWidget(db_group)

    # Future groups (Camera, Tuning, Game, User, ...) each drop in here as
    # another _settings_group(...) call + layout.addWidget(...).

    if AppSettings().dirty_bit:
        _first_run()

    camera_group = _settings_group("Camera", [])

    if not AppSettings().camera_dict or len(AppSettings().camera_dict) == 0:
        # Show "No cameras saved" message if camera_dict is empty or None
        no_cameras_label = QLabel("No cameras saved.")
        camera_group.layout().addRow(QLabel(""), no_cameras_label)
        cameras = list_attached_cameras()
    else:
        cameras = AppSettings().camera_dict
    if cameras:
        camera_select_row = _camera_select_row(
            current_index=AppSettings().camera_index,
            camera_dict=cameras,
            on_change=lambda idx: print(
                f"camera index -> {idx}"
            ),  # placeholder for save()
        )
        camera_group.layout().addRow("Camera index:", camera_select_row)

    layout.addWidget(camera_group)
    layout.addStretch()

    return page
