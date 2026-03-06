import os
from pathlib import Path
import platform
import sys
from ui.info import MessageWidget
from PySide6.QtCore import QStandardPaths

class Debug:
    _parent = None

    @staticmethod
    def init(parent):
        Debug._parent = parent

    @staticmethod
    def _show(message: str, level: str):
        if not Debug._parent:
            print(f"[{level.upper()}] {message}")
            return

        toast = MessageWidget(Debug._parent, message, level)
        toast.show_animated()

    @staticmethod
    def Error(message: str):
        Debug._show(message, "error")

    @staticmethod
    def Warn(message: str):
        Debug._show(message, "warn")

    @staticmethod
    def Log(message: str):
        Debug._show(message, "info")

class Info:
    CONFIG_PATH = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation), "vish", "config.json")
    @staticmethod
    def get_os():
        return platform.system()
    
    @staticmethod
    def get_config_path():
        Info.ensure_config_dir_exists()
        return Info.CONFIG_PATH
    
    @staticmethod
    def ensure_config_dir_exists():
        config_dir = os.path.dirname(Info.CONFIG_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)