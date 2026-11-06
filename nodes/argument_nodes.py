# argument_nodes.py
#
# Copyright 2026 michaelmadell
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

from core.bash_values import command_substitution, condition, expression, quote_literal
from core.port_types import PortType
from nodes.base_node import BaseNode
from nodes.registry import register_node


def _index_property(node, key="index", default=1):
    try:
        value = int(str(node.properties.get(key, default)).strip())
    except ValueError:
        value = default
    return max(value, 1)


def _positional(index: int):
    return expression(f"${{{index}}}")


@register_node(
    "get_argument",
    category="Arguments",
    label="Get Argument",
    description="Gets a positional script argument ($1, $2, ...) by index",
    collapsable=True,
)
class GetArgumentNode(BaseNode):
    def __init__(self):
        super().__init__("get_argument", "Get Argument")
        self.add_output("Value", PortType.STRING, "Value of the argument")
        self.properties["index"] = 1

    def emit_bash_value(self, context):
        return _positional(_index_property(self))


@register_node(
    "argument_count",
    category="Arguments",
    label="Argument Count",
    description="Gets the number of arguments passed to the script ($#)",
    collapsable=True,
)
class ArgumentCountNode(BaseNode):
    def __init__(self):
        super().__init__("argument_count", "Argument Count")
        self.add_output("Count", PortType.INT, "Number of arguments")

    def emit_bash_value(self, context):
        return expression("${#}")


@register_node(
    "all_arguments",
    category="Arguments",
    label="All Arguments",
    description="Gets every argument passed to the script ($@)",
    collapsable=True,
)
class AllArgumentsNode(BaseNode):
    def __init__(self):
        super().__init__("all_arguments", "All Arguments")
        self.add_output("Arguments", PortType.STRING, "All arguments")

    def emit_bash_value(self, context):
        return expression("${@}")


@register_node(
    "script_name",
    category="Arguments",
    label="Script Name",
    description="Gets the name the script was invoked with ($0)",
    collapsable=True,
)
class ScriptNameNode(BaseNode):
    def __init__(self):
        super().__init__("script_name", "Script Name")
        self.add_output("Name", PortType.STRING, "Script name")

    def emit_bash_value(self, context):
        return expression("${0}")


@register_node(
    "has_flag",
    category="Arguments",
    label="Has Flag",
    description="Checks whether a flag (e.g. --verbose) was passed anywhere in the arguments",
    collapsable=True,
)
class HasFlagNode(BaseNode):
    def __init__(self):
        super().__init__("has_flag", "Has Flag")
        self.add_output("Found", PortType.CONDITION, "Whether the flag was passed")
        self.properties["flag"] = "--flag"
        self.properties["alias"] = ""

    def emit_bash(self, context):
        return self.emit_condition(context)

    def emit_condition(self, context):
        flag = quote_literal(self.properties.get("flag", ""))
        alias = str(self.properties.get("alias", "")).strip()

        match = f'"$VISH_ARG" == {flag}'
        if alias:
            match += f' || "$VISH_ARG" == {quote_literal(alias)}'

        return condition(
            "(VISH_FOUND=1; for VISH_ARG in \"$@\"; do "
            f"[[ {match} ]] && {{ VISH_FOUND=0; break; }}; "
            'done; exit "$VISH_FOUND")'
        )


@register_node(
    "get_flag_value",
    category="Arguments",
    label="Get Flag Value",
    description="Gets the value passed to a flag, as --flag=value or --flag value",
    collapsable=True,
)
class GetFlagValueNode(BaseNode):
    def __init__(self):
        super().__init__("get_flag_value", "Get Flag Value")
        self.add_output("Value", PortType.STRING, "Value passed to the flag")
        self.properties["flag"] = "--flag"
        self.properties["default"] = ""

    def emit_bash_value(self, context):
        flag = quote_literal(self.properties.get("flag", ""))
        default = quote_literal(self.properties.get("default", ""))

        return command_substitution(
            f"VISH_VALUE={default}; VISH_ARGS=(\"$@\"); "
            'for ((VISH_I=0; VISH_I<${#VISH_ARGS[@]}; VISH_I++)); do '
            'VISH_A="${VISH_ARGS[$VISH_I]}"; '
            f'case "$VISH_A" in {flag}=*) VISH_VALUE="${{VISH_A#*=}}";; '
            f'{flag}) VISH_VALUE="${{VISH_ARGS[$((VISH_I+1))]}}";; esac; '
            'done; printf \'%s\' "$VISH_VALUE"'
        )
