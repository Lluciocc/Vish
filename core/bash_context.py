# bash_context.py
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

from typing import List, Dict

class BashContext:
    def __init__(self):
        self.variables: Dict[str, str] = {}
        self.indent_level = 0
        self.lines: List[str] = []
        self.function_lines = []
        self.emitted_nodes = set()
        self._current_buffer = "main"
    
    def add_line(self, line: str):
        indent = "    " * self.indent_level
        if self._current_buffer == "function":
            self.function_lines.append(f"{indent}{line}")
        else:
            self.lines.append(f"{indent}{line}")

    def add_function_line(self, line: str):
        self.function_lines.append(line)

    def build(self) -> str:
        return "\n".join(self.function_lines + [""] + self.lines)
    
    def indent(self):
        self.indent_level += 1
    
    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)
    
    def get_script(self) -> str:
        return "\n".join(self.function_lines + [""] + self.lines)
