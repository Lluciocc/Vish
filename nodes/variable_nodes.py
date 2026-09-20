# variable_nodes.py
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

from core.bash_context import BashContext
from core.bash_values import (
    BashValue,
    condition,
    identifier,
    literal,
    render_assignment,
    render_word,
    user_interpolation,
    variable,
)
from core.port_types import PortType
from nodes.base_node import BaseNode
from nodes.registry import register_node


@register_node(
    "set_variable",
    category="Variables",
    label="Set Variable",
    description="Sets a variable to a specific value",
)
class SetVariableNode(BaseNode):
    def __init__(self):
        super().__init__("set_variable", "Set Variable")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Value", PortType.ANY, "Value")
        self.add_output("Exec", PortType.EXEC, "Control flow output")

        self.properties["variable"] = "VAR"
        self.properties["value"] = ""

    def emit_bash(self, context: BashContext) -> str:
        var_name = identifier(self.properties.get("variable", "VAR"), "VAR")
        value = user_interpolation(self.properties.get("value", ""))

        value_port = self.inputs[1]
        if value_port.connected_edges:
            source_node = value_port.connected_edges[0].source.node

            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                value = emitted

        value_expr = render_assignment(value)
        context.variables[var_name] = value
        return f"{var_name}={value_expr}"


@register_node(
    "get_variable",
    category="Variables",
    label="Get Variable",
    description="Gets the value of a variable",
    collapsable=True,
)
class GetVariableNode(BaseNode):
    def __init__(self):
        super().__init__("get_variable", "Get Variable")
        self.add_output("Value", PortType.VARIABLE, "Variable value")
        self.properties["variable"] = "VAR"

    def emit_bash(self, context: BashContext) -> str:
        var_name = identifier(self.properties.get("variable", "VAR"), "VAR")
        return render_word(variable(var_name))

    def emit_bash_value(self, context):
        var_name = identifier(self.properties.get("variable", "VAR"), "VAR")
        return variable(var_name)


@register_node(
    "file_exists",
    category="Variables",
    label="File Exists",
    description="Checks if a file exists",
    collapsable=True,
)
class FileExistsNode(BaseNode):
    def __init__(self):
        super().__init__("file_exists", "File Exists")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Result", PortType.CONDITION, "Existence check result")
        self.properties["path"] = ""

    def emit_bash(self, context: BashContext) -> str:
        return self.emit_condition(context)

    def emit_condition(self, context: BashContext) -> str:
        path = user_interpolation(self.properties.get("path", ""), expand_tilde=True)

        path_port = self.inputs[0]
        if path_port.connected_edges:
            source_node = path_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                path = emitted

        return condition(f"[[ -f {render_word(path)} ]]")


@register_node(
    "string_constant",
    category="Constants",
    label="String Constant",
    description="Represents a string constant value",
    collapsable=True,
)
class StringConstantNode(BaseNode):
    def __init__(self):
        super().__init__("string_constant", "String Constant")
        self.add_output("Value", PortType.STRING, "String value")
        self.properties["value"] = ""

    def emit_bash_value(self, context: BashContext) -> BashValue:
        return literal(self.properties.get("value", ""))
