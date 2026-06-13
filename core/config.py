# config.py
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

import json
from pathlib import Path
from core.debug import Debug, Info

class Config:
    DEBUG = False
    USING_TTY = True
    SYNC_NODES_AND_GEN = False
    AUTO_SAVE = False
    lang = "en"
    theme = "dark"
    CUSTOM_SHEBANG = "#!/usr/bin/env bash"
    
class ConfigManager:
    @staticmethod
    def serialize_config(config: Config):
        for attr in dir(config):
            if not attr.startswith("__") and not callable(getattr(config, attr)):
                yield (attr, getattr(config, attr))

    @staticmethod
    def load_config():
        try:
            with open(Info.get_config_path(), "r") as f:
                config_dict = json.load(f)
                for key, value in config_dict.items():
                    if hasattr(Config, key):
                        current = getattr(Config, key)
                        if isinstance(value, type(current)):
                            setattr(Config, key, value)
                        else:
                            Debug.Warn(f"Invalid type for {key}, ignoring")
        except FileNotFoundError:
            Debug.Warn("Config file not found. Using default configuration.")
        except Exception as e:
            Debug.Error(f"Failed to load config: {e}")
    @staticmethod
    def save_config():
        config_dict = dict(ConfigManager.serialize_config(Config))
        with open(Info.get_config_path(), "w") as f:
            json.dump(config_dict, f, indent=4)

class MarkdownLoader:
    @staticmethod
    def load_markdown(file):
        try:
            path = Info.resource_path(f"assets/markdown/{file}")
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            Debug.Error(f"Failed to load markdown file: {e}")
            return ""
