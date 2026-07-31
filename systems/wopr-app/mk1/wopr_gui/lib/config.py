from dataclasses import dataclass, asdict
from pathlib import Path
import json

base_values = {
    "core": {
        "config_directory": str(Path.home() / ".config" / "wopr"),
        "config_file": "wopr.config",
        "db_directory": str(Path.home() / ".local" / "share" / "wopr"),
        "db_file": "wopr.db",
    }
}

@dataclass
class _AppSettingsData:
    config_directory: Path = Path(base_values["core"]["config_directory"])
    db_directory: Path = Path(base_values["core"]["db_directory"])
    config_file: str = base_values["core"]["config_file"]
    db_file: str = base_values["core"]["db_file"]
    dirty_bit: bool = True
    camera_index: int = 0
    camera_dict: dict = None
    
    @property
    def config_path(self) -> Path:
        return self.config_directory / self.config_file
    @property
    def db_path(self) -> Path:
        return self.db_directory / self.db_file

class AppSettings:
    def __new__(cls):
        return ConfigManager().settings

class ConfigManager:
    _instance = None
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._loaded = False
        return cls._instance
    
    # Can I / Should I set config_path to default to the values in AppSettings? I think so, but I want to be sure that the default is a Path object, not a string.
    def __init__(self, config_path: Path = _AppSettingsData().config_path):
        if self._loaded:
            return
        self.config_path = config_path
        self.settings = self.load_settings()
        self._loaded = True

    def load_settings(self) -> _AppSettingsData:
        if not self.config_path.exists():
            return _AppSettingsData()
        with open(self.config_path, "r") as f:
            data = json.load(f)
            return _AppSettingsData(
                config_directory=Path(data["config_directory"]),
                db_directory=Path(data["db_directory"]),
                config_file=data["config_file"],
                db_file=data["db_file"],
                dirty_bit=False,  # settings have been loaded, so dirty bit is false
                camera_index=data.get("camera_index", 0),
                camera_dict=data.get("camera_dict", None),
            )

    def save_settings(self):
        with open(self.config_path, "w") as f:
            json.dump(asdict(self.settings), f, indent=4)