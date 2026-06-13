# traduction.py
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
from core.debug import Info, Debug
import os
import re

class Traduction:
    langs_path = Info.resource_path('assets/models/lang')
    model = {}

    @staticmethod
    def get_languages():
        langs = []
        for file in os.scandir(Traduction.langs_path):
            if file.is_file() and file.name[-5:] == '.json' and file.name != "en.json":
                file_name = file.name[:-5]
                lang_name = Traduction.get_language_name(file.path)
                if lang_name is None:
                    lang_name = 'Unknown language'
                langs.append((lang_name, file_name))
        langs.sort(key=lambda pair : pair[1])
        langs.insert(0, ('English', 'en'))
        return langs

    @staticmethod
    def get_language_name(lang_path: str):
        try:
            with open(lang_path, encoding='utf-8') as data:
                lines = '\n'.join(data.readlines(2))
                match = re.search(r'"language_name"\s*:\s*"(.*?)"\s*,', lines)
                lang_name = match.group(1)
                return lang_name
        except Exception:
            return None

    @staticmethod
    def set_translate_model(lang: str):
        trad_file = os.path.join(Traduction.langs_path, lang + '.json')
        try:
            with open(trad_file, encoding='utf-8') as data:
                Traduction.model = json.load(data)
        except FileNotFoundError:
            Debug.Error(f"Cannot find language model for {lang}")

    @staticmethod
    def get_trad(msgid, fallback="", **kwargs):
        text = Traduction.model.get(msgid, fallback)
        try:
            return text.format(**kwargs)
        except Exception:
            return text
