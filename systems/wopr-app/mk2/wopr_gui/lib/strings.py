from pathlib import Path

import tomllib

_LOCALE_DIR = Path(__file__).parent.parent / "locales"
_strings: dict = {}


def load(lang: str = "en") -> None:
    global _strings
    with open(_LOCALE_DIR / f"{lang}.toml", "rb") as f:
        _strings = tomllib.load(f)


def basedata(key: str, **kwargs) -> str:
    node = _strings
    for part in key.split("."):
        node = node[part]
    return node.format(**kwargs) if kwargs else node
