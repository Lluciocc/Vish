# utils_node.py
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
    arithmetic,
    literal,
    number,
    path_expression,
    render_arithmetic,
    render_word,
)
from core.port_types import PortType
from nodes.base_node import BaseNode
from nodes.registry import register_node


@register_node(
    "to_string",
    category="Conversion",
    label="To String",
    collapsable=True,
)
class ToString(BaseNode):
    def __init__(self):
        super().__init__("to_string", "To String")
        self.add_input("Input", PortType.INT, "Value to convert to string")
        self.add_output("Output", PortType.VARIABLE, "String representation")

    def emit_bash(self, context):
        return render_word(self.emit_bash_value(context))

    def emit_bash_value(self, context):
        input_port = self.inputs[0]

        if input_port.connected_edges:
            value = input_port.connected_edges[0].source.node.emit_bash_value(context)
            if value is not None:
                if not isinstance(value, BashValue):
                    source = input_port.connected_edges[0].source.node
                    raise TypeError(f"{source.title} returned a rendered Bash value")
                return value

        return literal(input_port.value or "")


@register_node(
    "to_int",
    category="Conversion",
    label="To Int",
    collapsable=True,
)
class ToInt(BaseNode):
    def __init__(self):
        super().__init__("to_int", "To Int")
        self.add_input("Input", PortType.VARIABLE, "Value to convert to integer")
        self.add_output("Output", PortType.INT, "Integer representation")

    def emit_bash(self, context):
        return render_arithmetic(self.emit_bash_value(context))

    def emit_bash_value(self, context):
        input_port = self.inputs[0]

        if input_port.connected_edges:
            value = input_port.connected_edges[0].source.node.emit_bash_value(context)
            if value is None:
                value = number(0)
            elif not isinstance(value, BashValue):
                source = input_port.connected_edges[0].source.node
                raise TypeError(f"{source.title} returned a rendered Bash value")
        else:
            value = number(input_port.value or "0")

        return arithmetic(f" {render_arithmetic(value)} ")


@register_node(
    "path_constant",
    category="Constants",
    label="Path Constant",
    description="Represents a path constant value",
    collapsable=True,
)
class PathConstant(BaseNode):
    def __init__(self):
        super().__init__("path_constant", "Path Constant")
        self.add_output("Value", PortType.PATH, "Path value")
        self.properties["value"] = "~"

    def emit_bash_value(self, context: BashContext) -> str:
        return path_expression(self.properties.get("value", "~"), expand_tilde=True)


@register_node(
    "sleep",
    category="Utilities",
    label="Sleep",
    description="Pauses execution for a specified duration",
)
class SleepNode(BaseNode):
    def __init__(self):
        super().__init__("sleep", "Sleep")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Duration", PortType.INT, "Duration to sleep in seconds")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["duration"] = 1

    def emit_bash(self, context: BashContext) -> str:
        duration = number(self.properties.get("duration", 1), default="1")

        duration_port = self.inputs[1]
        if duration_port.connected_edges:
            source_node = duration_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                duration = emitted

        return f"sleep {render_arithmetic(duration, default='1')}"


@register_node(
    "download_file",
    category="Utilities",
    label="Download File",
    description="Downloads a file from a specified URL",
)
class DownloadFileNode(BaseNode):
    def __init__(self):
        super().__init__("download_file", "Download File")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["url"] = ""
        self.properties["output_path"] = ""

    def emit_bash(self, context: BashContext) -> str:
        url = self.properties.get("url", "")
        output_path = self.properties.get("output_path", "")

        output = render_word(path_expression(output_path, expand_tilde=True))
        return f"curl -o {output} -- {render_word(literal(url))}"


@register_node(
    "git_clone",
    category="Utilities",
    label="Git Clone",
    description="Clones a Git repository to a specified destination",
)
class GitCloneNode(BaseNode):
    def __init__(self):
        super().__init__("git_clone", "Git Clone")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["repo_url"] = ""
        self.properties["destination_path"] = ""

    def emit_bash(self, context: BashContext) -> str:
        repo_url = self.properties.get("repo_url", "")
        destination_path = self.properties.get("destination_path", "")

        destination = render_word(path_expression(destination_path, expand_tilde=True))
        return f"git clone -- {render_word(literal(repo_url))} {destination}"


@register_node(
    "open_website",
    category="Utilities",
    label="Open Website",
    description="Opens a specified URL in the default web browser",
)
class OpenWebsiteNode(BaseNode):
    def __init__(self):
        super().__init__("open_website", "Open Website")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["url"] = ""

    def emit_bash(self, context: BashContext) -> str:
        url = self.properties.get("url", "")

        return f"xdg-open -- {render_word(literal(url))}"
