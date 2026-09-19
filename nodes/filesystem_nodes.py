# filesystem_nodes.py
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

from core.bash_values import (
    arithmetic_operand,
    command_substitution,
    condition,
    number,
    shell_word,
    user_interpolation,
)
from core.port_types import PortType
from nodes.base_node import BaseNode
from nodes.registry import register_node


class ArgumentNode(BaseNode):
    def _argument(self, key, port_index, context, default=""):
        port = self.inputs[port_index] if port_index is not None else None
        if port is not None and port.connected_edges:
            source = port.connected_edges[0].source.node
            value = source.emit_bash_value(context)
            if value is not None:
                return shell_word(value)
        value = self.properties.get(key, default)
        expand_tilde = port is not None and port.port_type == PortType.PATH
        return shell_word(user_interpolation(value, expand_tilde=expand_tilde))

    def _numeric_argument(self, key, port_index, context, default=0):
        port = self.inputs[port_index]
        if port.connected_edges:
            source = port.connected_edges[0].source.node
            value = source.emit_bash_value(context)
            if value is not None:
                return arithmetic_operand(value, default=default)
        return str(number(self.properties.get(key, default), default=default))

    def _add_exec_ports(self):
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")


@register_node(
    "directory_exists",
    category="File System",
    label="Directory Exists",
    description="Checks whether a directory exists",
    collapsable=True,
)
class DirectoryExistsNode(ArgumentNode):
    def __init__(self):
        super().__init__("directory_exists", "Directory Exists")
        self.add_input("Path", PortType.PATH, "Directory path")
        self.add_output("Result", PortType.CONDITION, "Existence check result")
        self.properties["path"] = ""

    def emit_condition(self, context):
        return condition(f"[ -d {self._argument('path', 0, context)} ]")


@register_node(
    "create_directory",
    category="File System",
    label="Create Directory",
    description="Creates a directory and missing parent directories",
)
class CreateDirectoryNode(ArgumentNode):
    def __init__(self):
        super().__init__("create_directory", "Create Directory")
        self._add_exec_ports()
        self.add_input("Path", PortType.PATH, "Directory path")
        self.properties["path"] = ""

    def emit_bash(self, context):
        return f"mkdir -p -- {self._argument('path', 1, context)}"


@register_node(
    "copy_file",
    category="File System",
    label="Copy File",
    description="Copies a file to another path",
)
class CopyFileNode(ArgumentNode):
    def __init__(self):
        super().__init__("copy_file", "Copy File")
        self._add_exec_ports()
        self.add_input("Source", PortType.PATH, "Source file path")
        self.add_input("Destination", PortType.PATH, "Destination path")
        self.properties["source"] = ""
        self.properties["destination"] = ""

    def emit_bash(self, context):
        source = self._argument("source", 1, context)
        destination = self._argument("destination", 2, context)
        return f"cp -- {source} {destination}"


@register_node(
    "copy_directory",
    category="File System",
    label="Copy Directory",
    description="Copies a directory and all of its contents to another path",
)
class CopyDirectoryNode(CopyFileNode):
    def __init__(self):
        ArgumentNode.__init__(self, "copy_directory", "Copy Directory")
        self._add_exec_ports()
        self.add_input("Source", PortType.PATH, "Source directory path")
        self.add_input("Destination", PortType.PATH, "Destination path")
        self.properties["source"] = ""
        self.properties["destination"] = ""

    def emit_bash(self, context):
        source = self._argument("source", 1, context)
        destination = self._argument("destination", 2, context)
        return f"cp -R -- {source} {destination}"


@register_node(
    "move_file",
    category="File System",
    label="Move File",
    description="Moves or renames a file",
)
class MoveFileNode(CopyFileNode):
    def __init__(self):
        ArgumentNode.__init__(self, "move_file", "Move File")
        self._add_exec_ports()
        self.add_input("Source", PortType.PATH, "Source file path")
        self.add_input("Destination", PortType.PATH, "Destination path")
        self.properties["source"] = ""
        self.properties["destination"] = ""

    def emit_bash(self, context):
        source = self._argument("source", 1, context)
        destination = self._argument("destination", 2, context)
        return f"mv -- {source} {destination}"


@register_node(
    "delete_file",
    category="File System",
    label="Delete File",
    description="Deletes a file",
)
class DeleteFileNode(ArgumentNode):
    def __init__(self):
        super().__init__("delete_file", "Delete File")
        self._add_exec_ports()
        self.add_input("Path", PortType.PATH, "File path")
        self.properties["path"] = ""

    def emit_bash(self, context):
        return f"rm -f -- {self._argument('path', 1, context)}"


@register_node(
    "delete_directory",
    category="File System",
    label="Delete Directory",
    description="Deletes a directory and all of its contents",
)
class DeleteDirectoryNode(DeleteFileNode):
    def __init__(self):
        ArgumentNode.__init__(self, "delete_directory", "Delete Directory")
        self._add_exec_ports()
        self.add_input("Path", PortType.PATH, "Directory path")
        self.properties["path"] = ""

    def emit_bash(self, context):
        return f"rm -rf -- {self._argument('path', 1, context)}"


@register_node(
    "read_file",
    category="File System",
    label="Read File",
    description="Reads the contents of a file",
    collapsable=True,
)
class ReadFileNode(ArgumentNode):
    def __init__(self):
        super().__init__("read_file", "Read File")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Content", PortType.STRING, "File contents")
        self.properties["path"] = ""

    def emit_bash_value(self, context):
        return command_substitution(f"cat -- {self._argument('path', 0, context)}")


class FileContentWriterNode(ArgumentNode):
    redirect = ">"

    def _setup(self):
        self._add_exec_ports()
        self.add_input("Path", PortType.PATH, "File path")
        self.add_input("Content", PortType.STRING, "Content to write")
        self.properties["path"] = ""
        self.properties["content"] = ""

    def emit_bash(self, context):
        path = self._argument("path", 1, context)
        content = self._argument("content", 2, context)
        return f"printf '%s' {content} {self.redirect} {path}"


@register_node(
    "write_file",
    category="File System",
    label="Write File",
    description="Writes content to a file, replacing its contents",
)
class WriteFileNode(FileContentWriterNode):
    def __init__(self):
        super().__init__("write_file", "Write File")
        self._setup()


@register_node(
    "append_to_file",
    category="File System",
    label="Append to File",
    description="Appends content to a file",
)
class AppendToFileNode(FileContentWriterNode):
    redirect = ">>"

    def __init__(self):
        super().__init__("append_to_file", "Append to File")
        self._setup()


@register_node(
    "list_directory",
    category="File System",
    label="List Directory",
    description="Lists a directory's entries",
    collapsable=True,
)
class ListDirectoryNode(ArgumentNode):
    def __init__(self):
        super().__init__("list_directory", "List Directory")
        self.add_input("Path", PortType.PATH, "Directory path")
        self.add_output("Entries", PortType.STRING, "Directory entries")
        self.properties["path"] = "."

    def emit_bash_value(self, context):
        return command_substitution(
            f"ls -A -- {self._argument('path', 0, context, '.')}"
        )


@register_node(
    "file_size",
    category="File System",
    label="File Size",
    description="Returns a file's size in bytes",
    collapsable=True,
)
class FileSizeNode(ArgumentNode):
    def __init__(self):
        super().__init__("file_size", "File Size")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Bytes", PortType.INT, "Size in bytes")
        self.properties["path"] = ""

    def emit_bash_value(self, context):
        return command_substitution(
            f"stat -c '%s' -- {self._argument('path', 0, context)}"
        )


@register_node(
    "file_extension",
    category="Paths",
    label="File Extension",
    description="Returns a filename extension without the dot",
    collapsable=True,
)
class FileExtensionNode(ArgumentNode):
    def __init__(self):
        super().__init__("file_extension", "File Extension")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Extension", PortType.STRING, "Filename extension")
        self.properties["path"] = ""

    def emit_bash_value(self, context):
        path = self._argument("path", 0, context)
        return command_substitution(
            "VISH_NAME=$(basename -- "
            f"{path}); if [[ $VISH_NAME == *.* && $VISH_NAME != .* ]]; then "
            "printf '%s' \"${VISH_NAME##*.}\"; fi"
        )


@register_node(
    "filename",
    category="Paths",
    label="Filename",
    description="Returns the final component of a path",
    collapsable=True,
)
class FilenameNode(ArgumentNode):
    def __init__(self):
        super().__init__("filename", "Filename")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Filename", PortType.STRING, "Filename")
        self.properties["path"] = ""

    def emit_bash_value(self, context):
        return command_substitution(f"basename -- {self._argument('path', 0, context)}")


@register_node(
    "parent_directory",
    category="Paths",
    label="Parent Directory",
    description="Returns the parent directory of a path",
    collapsable=True,
)
class ParentDirectoryNode(ArgumentNode):
    def __init__(self):
        super().__init__("parent_directory", "Parent Directory")
        self.add_input("Path", PortType.PATH, "Path")
        self.add_output("Parent", PortType.PATH, "Parent directory")
        self.properties["path"] = ""

    def emit_bash_value(self, context):
        return command_substitution(f"dirname -- {self._argument('path', 0, context)}")


@register_node(
    "join_path",
    category="Paths",
    label="Join Path",
    description="Joins two path components",
)
class JoinPathNode(ArgumentNode):
    def __init__(self):
        super().__init__("join_path", "Join Path")
        self.add_input("Base", PortType.PATH, "Base path")
        self.add_input("Child", PortType.PATH, "Child path")
        self.add_output("Path", PortType.PATH, "Joined path")
        self.properties["base"] = ""
        self.properties["child"] = ""

    def emit_bash_value(self, context):
        base = self._argument("base", 0, context)
        child = self._argument("child", 1, context)
        return command_substitution(
            f"VISH_BASE={base}; VISH_CHILD={child}; "
            "if [[ -z $VISH_BASE ]]; then printf '%s' \"$VISH_CHILD\"; "
            "elif [[ -z $VISH_CHILD ]]; then printf '%s' \"$VISH_BASE\"; "
            'else printf \'%s/%s\' "${VISH_BASE%/}" "${VISH_CHILD#/}"; fi'
        )


class TemporaryPathNode(ArgumentNode):
    option = ""

    def _setup(self):
        self.add_input("Template", PortType.STRING, "Optional mktemp template")
        self.add_output("Path", PortType.PATH, "Temporary path")
        self.properties["template"] = ""

    def emit_bash_value(self, context):
        template_port = self.inputs[0]
        template = self.properties.get("template", "")
        option = f" {self.option}" if self.option else ""
        if not template_port.connected_edges and not template:
            return command_substitution(f"mktemp{option}")
        return command_substitution(
            f"mktemp{option} -- {self._argument('template', 0, context)}"
        )


@register_node(
    "create_temporary_file",
    category="File System",
    label="Create Temporary File",
    description="Creates a temporary file and returns its path",
    collapsable=True,
)
class CreateTemporaryFileNode(TemporaryPathNode):
    def __init__(self):
        super().__init__("create_temporary_file", "Create Temporary File")
        self._setup()


@register_node(
    "create_temporary_directory",
    category="File System",
    label="Create Temporary Directory",
    description="Creates a temporary directory and returns its path",
    collapsable=True,
)
class CreateTemporaryDirectoryNode(TemporaryPathNode):
    option = "-d"

    def __init__(self):
        super().__init__("create_temporary_directory", "Create Temporary Directory")
        self._setup()
