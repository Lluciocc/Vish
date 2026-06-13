# highlights.py
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

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class BashHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []
        self.known_functions = set()
        keyword = QTextCharFormat()
        keyword.setForeground(QColor("#C792EA"))

        function_def = QTextCharFormat()
        function_def.setForeground(QColor("#D000FF"))

        function_call = QTextCharFormat()
        function_call.setForeground(QColor("#D000FF"))

        command = QTextCharFormat()
        command.setForeground(QColor("#82AAFF"))

        string = QTextCharFormat()
        string.setForeground(QColor("#C3E88D"))

        comment = QTextCharFormat()
        comment.setForeground(QColor("#616161"))
        comment.setFontItalic(True)

        variable = QTextCharFormat()
        variable.setForeground(QColor("#F78C6C"))

        number = QTextCharFormat()
        number.setForeground(QColor("#FFCB6B"))
        keywords = [
            "if", "then", "else", "elif", "fi",
            "for", "while", "do", "done",
            "case", "esac", "in",
            "select", "until", "break",
            "continue", "return", "exit"
        ]
        for kw in keywords:
            self.rules.append((
                QRegularExpression(rf"\b{kw}\b"),
                keyword
            ))

        commands = [
            "echo", "cd", "pwd", "read", "printf",
            "mkdir", "rm", "cp", "mv", "touch",
            "chmod", "chown", "grep", "sed", "awk",
            "curl", "wget", "sudo", "apt", "dnf",
            "pacman", "zypper", "systemctl", "ls",
            "cat", "head", "tail", "diff", "find",
            "xargs", "tar", "zip", "unzip",
            "ssh", "scp", "git", "make", "gcc",
            "gdb", "docker", "kubectl",
            "npm", "yarn", "node", "python", "java",
            "javac", "perl", "ruby", "php",
            "mysql", "psql", "top", "htop",
            "kill", "ping", "traceroute",
            "ifconfig", "netstat", "ssh-keygen",
            "alias", "unalias", "export", "source",
            "history", "clear", "man", "help", "which",
            "env", "printenv", "date", "time", "uptime", 
            "df", "du", "mount", "umount", "service", "set",
            "unset", "jobs", "fg", "bg", "wait", "trap", "test", 
            "expr", "bc", "cut", "sort", "uniq", "wc", "tee", "diff",
            "cmp", "stat", "file", "basename", "dirname", "readlink",
            "ln", "sleep", "shift", "getopts", "printf", "let", "eval",
            "exec", "disown", "shopt", "complete", "compgen", "mapfile", 

        ]
        for cmd in commands:
            self.rules.append((
                QRegularExpression(rf"\b{cmd}\b"),
                command
            ))

        self.rules.append((
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
            string
        ))
        self.rules.append((
            QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"),
            string
        ))

        self.rules.append((
            QRegularExpression(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?"),
            variable
        ))

        self.rules.append((
            QRegularExpression(r"\b\d+\b"),
            number
        ))

        self.rules.append((
            QRegularExpression(r"#.*"),
            comment
        ))

        self.function_def_regex = QRegularExpression(
            r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{"
        )
        self.function_def_format = function_def
        self.function_call_format = function_call

    
    def highlightBlock(self, text: str):
        match = self.function_def_regex.match(text)
        if match.hasMatch():
            name = match.captured(1)
            self.known_functions.add(name)

            self.setFormat(
                match.capturedStart(1),
                match.capturedLength(1),
                self.function_def_format
            )

        for regex, fmt in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(
                    m.capturedStart(),
                    m.capturedLength(),
                    fmt
                )

        for fn in self.known_functions:
            call_regex = QRegularExpression(rf"\b{fn}\b")
            it = call_regex.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(
                    m.capturedStart(),
                    m.capturedLength(),
                    self.function_call_format
                )
