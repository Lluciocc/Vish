# debug.py
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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
        Logger.LogError(message)

    @staticmethod
    def Warn(message: str):
        Debug._show(message, "warn")
        Logger.LogWarning(message)

    @staticmethod
    def Log(message: str):
        Debug._show(message, "info")
        Logger.LogMessage(message)


class Info:
    CONFIG_FILE = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation), "vish", "config.json")
    CONFIG_PATH = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation), "vish")
    @staticmethod
    def get_os():
        return platform.system()

    @staticmethod
    def get_config_file():
        Info.ensure_dir_exists(Info.CONFIG_FILE)
        return Info.CONFIG_FILE

    @staticmethod
    def get_config_path():
        Info.ensure_dir_exists(Info.CONFIG_PATH)
        return Info.CONFIG_PATH

    @staticmethod
    def ensure_dir_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_files_from_directory(base_directory, relative_path, name_filter):
        if base_directory == "resource_path":
            path = Info.resource_path(relative_path)
        if base_directory == "config_path":
            path = Path(Info.get_config_path()) / relative_path
        if not os.path.exists(path):
            return

        if name_filter == None:
            return os.listdir(path)
        files = []
        for file_name in os.listdir(path):
            if name_filter in file_name:
                files.append(file_name)
        return files

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
