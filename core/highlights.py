from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class BashHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []
        keyword = QTextCharFormat()
        keyword.setForeground(QColor("#C792EA"))
        keyword.setFontWeight(QFont.Bold)

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
            "case", "esac", "in", "function",
            "select", "until", "break", "continue",
            "return", "exit"
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
            "pacman", "zypper", "systemctl"
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

    def highlightBlock(self, text: str):
        for regex, fmt in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt
                )
