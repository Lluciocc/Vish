from theme.theme import Theme, set_dark_theme, set_white_theme, set_purple_theme
from core.debug import Info, Debug
from core.config import Config
from core.logger import Logger
from pathlib import Path
from PySide6.QtWidgets import QApplication
import shutil

BUILTIN_THEMES = ["dark", "white", "purple"]
theme_list: list[str] = list(BUILTIN_THEMES)

def parse_yaml(text: str) -> dict:
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        colon_idx = stripped.index(":")
        key = stripped[:colon_idx].strip()
        value_raw = stripped[colon_idx + 1:].strip()

        if value_raw and value_raw[0] in ('"', "'") and value_raw[-1] == value_raw[0]:
            value: object = value_raw[1:-1]
        elif not value_raw:
            value = None
        else:
            for cast in (int, float):
                try:
                    value = cast(value_raw)
                    break
                except ValueError:
                    pass
            else:
                if value_raw.lower() == "true":
                    value = True
                elif value_raw.lower() == "false":
                    value = False
                else:
                    value = value_raw

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if value is None:
            nested: dict = {}
            parent[key] = nested
            stack.append((indent, nested))
        else:
            parent[key] = value

    return root

_STYLESHEET_TEMPLATE = """
    QWidget {{
        background-color: {PANEL};
        color: {TEXT};
        font-size: 13px;
    }}
    QPushButton {{
        background-color: {PANEL};
        border: 1px solid {BUTTON};
        padding: 6px 10px;
        border-radius: 4px;
    }}
    QPushButton:hover  {{ border-color: {BUTTON_HOVER}; }}
    QPushButton:pressed {{ background-color: {BUTTON_PRESSED}; }}
    QTextEdit {{
        background-color: {BACKGROUND};
        border: 1px solid {BUTTON};
    }}
    QSplitter::handle {{ background-color: {BUTTON}; }}
"""

def _apply_stylesheet() -> None:
    app = QApplication.instance()
    if app is None:
        return
    app.setStyleSheet(_STYLESHEET_TEMPLATE.format(
        PANEL=Theme.PANEL,
        TEXT=Theme.TEXT,
        BUTTON=Theme.BUTTON,
        BUTTON_HOVER=Theme.BUTTON_HOVER,
        BUTTON_PRESSED=Theme.BUTTON_PRESSED,
        BACKGROUND=Theme.BACKGROUND,
    ))

def _populate_theme(data: dict) -> None:
    if "name" in data:
        Theme.selected_theme = data["name"]
    if "description" in data:
        Theme.description = data["description"]

    for key, value in data.get("theme", {}).items():
        attr = "type" if key == "TYPE" else key
        setattr(Theme, attr, value)

def _themes_dir() -> Path:
    return Path(Info.get_config_path()).parent / "themes"

def _resolve_theme_path(filepath: str) -> Path:
    path = Path(filepath)

    if path.exists():
        return path

    if path.suffix != ".yml":
        path = path.with_suffix(".yml")

    return _themes_dir() / path.name

def load_theme(filepath: str) -> type:
    if Config.DEBUG:
        Logger.LogMessage(f"Loading theme from {filepath}")

    if filepath in BUILTIN_THEMES:
        setter = {
            "dark": set_dark_theme,
            "white": set_white_theme,
            "purple": set_purple_theme,
        }.get(filepath)

        if setter:
            setter()
            _apply_stylesheet()

        return Theme

    theme_path = _resolve_theme_path(filepath)

    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            data = parse_yaml(f.read())
    except FileNotFoundError:
        Debug.Error(f"Theme file not found: {theme_path}")
        load_theme("dark")  # Fallback to dark theme
        return Theme
    except Exception as e:
        Debug.Error(f"Failed to load theme from {theme_path}: {e}")
        load_theme("dark")
        return Theme

    _populate_theme(data)
    _apply_stylesheet()

    name = data.get("name", theme_path.stem)
    if name not in theme_list:
        theme_list.append(name)

    return Theme

def load_every_theme() -> None:
    config_dir = _themes_dir()
    if not config_dir.exists():
        return

    for file in config_dir.glob("*.yml"):
        try:
            if file.stem not in theme_list:
                theme_list.append(file.stem)
        except Exception as e:
            Debug.Error(f"Failed to load {file.name}: {e}")

def import_theme(filepath: str) -> type | None:
    try:
        _copy_theme_to_config(filepath)
        theme = load_theme(filepath)
        return theme
    except Exception as e:
        Debug.Error(f"Failed to import {filepath}: {e}")
        return None

def delete_theme(theme_name: str) -> None:
    for file in _themes_dir().glob("*.yml"):
        try:
            if f"name: {theme_name}" in file.read_text(encoding="utf-8"):
                file.unlink()
                if theme_name in theme_list:
                    theme_list.remove(theme_name)
                return
        except Exception as e:
            Debug.Error(f"Failed to delete {file.name}: {e}")

def _copy_theme_to_config(filepath: str) -> None:
    src = Path(filepath)
    if not src.exists():
        return

    config_dir = _themes_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    dest = config_dir / src.name
    if not dest.exists():
        try:
            shutil.copy2(src, dest)
        except Exception as e:
            Debug.Error(f"Failed to copy theme file: {e}")