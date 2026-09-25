"""WOPR Core Library - Tactical Wargaming Adjudication Tracker"""

from wopr.config import (
    ConfigError,
    get_bool,
    get_dict,
    get_float,
    get_int,
    get_list,
    get_section,
    get_setting,
    get_str,
    init_config,
    reload_config,
)
from wopr.logging import get_logger, setup_logging
from wopr.storage import (
    StorageError,
    ensure_path,
    get_game_directory,
    imagefilename,
    list_game_images,
    thumbnailfilename,
)

__version__ = "0.1.3-beta"
__all__ = [
    # Config
    "init_config",
    "get_setting",
    "get_str",
    "get_int",
    "get_float",
    "get_bool",
    "get_list",
    "get_dict",
    "get_section",
    "reload_config",
    "ConfigError",
    # Storage
    "imagefilename",
    "thumbnailfilename",
    "ensure_path",
    "get_game_directory",
    "list_game_images",
    "StorageError",
    # Logging
    "setup_logging",
    "get_logger",
]
