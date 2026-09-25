from enum import StrEnum
from importlib.metadata import metadata

_meta = metadata("wopr_gui")

APP_NAME = _meta["Name"]
APP_VERSION = _meta["Version"]
APP_SUMMARY = _meta["Summary"]

APP_TITLE = f"{APP_NAME} - {APP_VERSION} - {APP_SUMMARY}"
