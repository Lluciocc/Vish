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

from dataclasses import dataclass
from enum import Enum

from themes.theme_manager import Theme


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


EXEC_STYLE = PortStyle(Theme.get_color("PORT_TYPES-EXEC"), 12, thickness=4.5)
STRING_STYLE = PortStyle(Theme.get_color("PORT_TYPES-STRING"), 10)
INT_STYLE = PortStyle(Theme.get_color("PORT_TYPES-INT"), 10)
BOOL_STYLE = PortStyle(Theme.get_color("PORT_TYPES-BOOL"), 10)
PATH_STYLE = PortStyle(Theme.get_color("PORT_TYPES-PATH"), 10)
VARIABLE_STYLE = PortStyle(Theme.get_color("PORT_TYPES-VARIABLE"), 10)
CONDITION_STYLE = PortStyle(Theme.get_color("PORT_TYPES-CONDITION"), 10)
ANY_STYLE = PortStyle(Theme.get_color("PORT_TYPES-ANY"), 10)

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
