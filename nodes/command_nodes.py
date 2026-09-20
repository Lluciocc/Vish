# command_nodes.py
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
    command_substitution,
    number,
    raw_command,
    render_arithmetic,
    render_raw_command,
    render_word,
    user_interpolation,
)
from core.port_types import PortType
from nodes.base_node import BaseNode
from nodes.registry import register_node


@register_node(
    "run_command",
    category="Commands",
    label="Run a command",
    description="Executes a shell command",
)
class RunCommandNode(BaseNode):
    def __init__(self):
        super().__init__("run_command", "Run Command")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Command", PortType.STRING, "Command to run")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.add_output("Output", PortType.STRING, "Command output")
        self.properties["command"] = "ls"

    def emit_bash(self, context: BashContext) -> str:
        command = raw_command(self.properties.get("command", ""))

        cmd_port = self.inputs[1]
        if cmd_port.connected_edges:
            source_node = cmd_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                command = emitted

        return render_raw_command(command)

    def emit_bash_value(self, context: BashContext):
        return command_substitution(self.emit_bash(context))


@register_node(
    "pipe",
    category="Commands",
    label="Pipe",
    description="Pipes output from Command 1 into Command 2",
)
class PipeNode(BaseNode):
    def __init__(self):
        super().__init__("pipe", "Pipe")
        self.add_input("Exec", PortType.EXEC, "Execution Input")
        self.add_input("Command 1", PortType.ANY, "Left command")
        self.add_input("Command 2", PortType.ANY, "Right command")
        self.add_output("Exec", PortType.EXEC, "Execution Output")
        self.add_output("Output", PortType.STRING, "Output of piped command")
        self.properties["Command 1"] = "ls"
        self.properties["Command 2"] = "grep test"

    def emit_bash(self, context: BashContext) -> str:
        cmd1 = raw_command(self.properties.get("Command 1", "ls"))
        cmd2 = raw_command(self.properties.get("Command 2", ""))

        cmd1_port = self.inputs[1]
        if cmd1_port.connected_edges:
            source_node = cmd1_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                cmd1 = emitted

        cmd2_port = self.inputs[2]
        if cmd2_port.connected_edges:
            source_node = cmd2_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                cmd2 = emitted

        return f"{render_raw_command(cmd1)} | {render_raw_command(cmd2)}"

    def emit_bash_value(self, context: BashContext):
        return command_substitution(self.emit_bash(context))


@register_node(
    "echo",
    category="Commands",
    label="Print a text",
    description="Prints a text to the console",
)
class EchoNode(BaseNode):
    def __init__(self):
        super().__init__("echo", "Echo")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Text", PortType.ANY, "Things to print")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["text"] = "Hello"

    def emit_bash(self, context: BashContext) -> str:
        text = user_interpolation(self.properties.get("text", ""))

        text_port = self.inputs[1]

        if text_port.connected_edges:
            source_node = text_port.connected_edges[0].source.node

            value = source_node.emit_bash_value(context)
            if value is not None:
                if not isinstance(value, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                text = value

        return f"echo {render_word(text)}"


@register_node(
    "exit",
    category="Commands",
    label="Exit script",
    description="Exits the script with a status code",
)
class ExitNode(BaseNode):
    def __init__(self):
        super().__init__("exit", "Exit")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Code", PortType.INT, "Exit code")
        self.properties["code"] = 0

    def emit_bash(self, context: BashContext) -> str:
        code = number(self.properties.get("code", 0))

        code_port = self.inputs[1]
        if code_port.connected_edges:
            source_node = code_port.connected_edges[0].source.node
            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                if not isinstance(emitted, BashValue):
                    raise TypeError(
                        f"{source_node.title} returned a rendered Bash value"
                    )
                code = emitted

        return f"exit {render_arithmetic(code)}"
