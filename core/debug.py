from core.logger import Logger
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QGuiApplication
from ui.info import MessageWidget
import getpass
import os
import platform
import sys

class Debug:
    _parent = None
    init_error = False

    @staticmethod
    def init(parent):
        Debug._parent = parent

    @staticmethod
    def _show(message: str, level: str):
        if not Debug._parent:
            from core.config import Config 
            if Config.DEBUG:
                Logger.LogError("Debug not initialized with parent widget, using console for output.")
                Debug.init_error = True
            return

        toast = MessageWidget(Debug._parent, message, level)
        toast.show_animated()

    @staticmethod
    def Error(message: str):
        Debug._show(message, "error")

        from core.config import Config # importing here to avoid circular import
        if Config.DEBUG or Debug.init_error:
            Logger.LogError(message)

    @staticmethod
    def Warn(message: str):
        Debug._show(message, "warn")

        from core.config import Config
        if Config.DEBUG or Debug.init_error:
            Logger.LogWarning(message)

    @staticmethod
    def Log(message: str):
        Debug._show(message, "info")
        from core.config import Config
        if Config.DEBUG or Debug.init_error:
            Logger.LogMessage(message)

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

    @staticmethod
    def get_user():
         return getpass.getuser()

    @staticmethod
    def get_device_type():
        screen = QGuiApplication.primaryScreen()
        dpi = screen.physicalDotsPerInch()

        physical_width = screen.size().width() / dpi
        physical_height = screen.size().height() / dpi
        physical_diagonal = (physical_width ** 2 + physical_height ** 2) ** 0.5

        if physical_diagonal <= 7.5:
            device_type = "phone"
        else:
            device_type = "desktop"
        return device_type
