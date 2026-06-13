# port_types.py
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

from enum import Enum
from dataclasses import dataclass
from typing import Any

class PortType(Enum):
    EXEC = "exec"
    STRING = "string"
    INT = "int"
    BOOL = "bool"
    CONDITION = "condition"
    PATH = "path"
    VARIABLE = "variable"
    ANY = "any"

class PortDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"

@dataclass
class PortStyle:
    color: str
    size: int
    thickness: float = 3
    
EXEC_STYLE = PortStyle("#FFFFFF", 12, thickness=4.5)
STRING_STYLE = PortStyle("#FF6B9D", 10)
INT_STYLE = PortStyle("#4ECDC4", 10)
BOOL_STYLE = PortStyle("#95E1D3", 10)
PATH_STYLE = PortStyle("#F38181", 10)
VARIABLE_STYLE = PortStyle("#FFA07A", 10)
CONDITION_STYLE = PortStyle("#F7D046", 10)
ANY_STYLE = PortStyle("#CCCCCC", 10)

PORT_STYLES = {
    PortType.EXEC: EXEC_STYLE,
    PortType.STRING: STRING_STYLE,
    PortType.INT: INT_STYLE,
    PortType.BOOL: BOOL_STYLE,
    PortType.CONDITION: CONDITION_STYLE,
    PortType.PATH: PATH_STYLE,
    PortType.VARIABLE: VARIABLE_STYLE,
    PortType.ANY: ANY_STYLE,
}