# operation_nodes.py
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
from __future__ import annotations
import re
import shlex
from enum import Enum, auto


class BashValueKind(Enum):
    LITERAL = auto()
    USER_INTERPOLATION = auto()
    VARIABLE = auto()
    COMMAND_SUBSTITUTION = auto()
    ARITHMETIC = auto()
    NUMBER = auto()
    CONDITION = auto()


class BashValue(str):
    kind: BashValueKind
    def __new__(cls, value, kind: BashValueKind):
        instance = super().__new__(cls, str(value))
        instance.kind = kind
        return instance


_SIMPLE_PARAMETER = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*")
_BRACED_PARAMETER = re.compile(
    r"\$\{(?:#[A-Za-z_][A-Za-z0-9_]*|"
    r"[A-Za-z_][A-Za-z0-9_]*(?:(?:##|#|%%|%)[^{}$`\"';()]*)?)\}"
)
_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)\Z")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_GLOB_CHARACTER = re.compile(r"[*?[]")
_SAFE_GLOB_SUFFIX = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-*?[]!"
)


def literal(value) -> BashValue:
    return BashValue(value, BashValueKind.LITERAL)


def user_interpolation(value, *, expand_tilde=False) -> BashValue:
    text = str(value)
    if expand_tilde and (text == "~" or text.startswith("~/")):
        text = "$HOME" + text[1:]
    return BashValue(text, BashValueKind.USER_INTERPOLATION)


def variable(name: str) -> BashValue:
    return BashValue(f"${name}", BashValueKind.VARIABLE)


def command_substitution(command: str) -> BashValue:
    return BashValue(f"$({command})", BashValueKind.COMMAND_SUBSTITUTION)


def arithmetic(expression: str) -> BashValue:
    return BashValue(f"$(({expression}))", BashValueKind.ARITHMETIC)


def number(value, default="0") -> BashValue:
    text = str(value)
    if not _NUMBER.fullmatch(text):
        text = str(default)
    return BashValue(text, BashValueKind.NUMBER)


def condition(expression: str) -> BashValue:
    return BashValue(expression, BashValueKind.CONDITION)


def identifier(value, default: str) -> str:
    text = str(value)
    return text if _IDENTIFIER.fullmatch(text) else default


def quote_literal(value) -> str:
    text = str(value)
    escaped = "".join(
        "\\" + character if character in {"\\", '"', "`", "$"} else character
        for character in text
    )
    return f'"{escaped}"'


def _parameter_at(text: str, index: int):
    for pattern in (_BRACED_PARAMETER, _SIMPLE_PARAMETER):
        match = pattern.match(text, index)
        if match:
            return match
    return None


def quote_user_interpolation(value) -> str:
    text = str(value)
    pieces: list[str] = []
    found_parameter = False
    index = 0
    while index < len(text):
        if text[index] == "$" and (index == 0 or text[index - 1] != "\\"):
            match = _parameter_at(text, index)
            if match:
                pieces.append(match.group(0))
                index = match.end()
                found_parameter = True
                continue

        character = text[index]
        if character in {"\\", '"', "`", "$"}:
            pieces.append("\\" + character)
        else:
            pieces.append(character)
        index += 1

    if not found_parameter:
        return quote_literal(text)
    return '"' + "".join(pieces) + '"'


def shell_word(value) -> str:
    if not isinstance(value, BashValue):
        return quote_literal(value)
    if value.kind == BashValueKind.LITERAL:
        return quote_literal(value)
    if value.kind == BashValueKind.USER_INTERPOLATION:
        return quote_user_interpolation(value)
    if value.kind == BashValueKind.CONDITION:
        return quote_literal(value)
    if value.kind in {
        BashValueKind.VARIABLE,
        BashValueKind.COMMAND_SUBSTITUTION,
    }:
        return f'"{value}"'
    return str(value)


def shell_assignment(value) -> str:
    return shell_word(value)


def arithmetic_operand(value, default="0") -> str:
    if isinstance(value, BashValue):
        if value.kind in {
            BashValueKind.NUMBER,
            BashValueKind.VARIABLE,
            BashValueKind.COMMAND_SUBSTITUTION,BashValueKind.ARITHMETIC,
        }:
            return str(value)
        if value.kind == BashValueKind.LITERAL and _NUMBER.fullmatch(str(value)):
            return str(value)
    elif _NUMBER.fullmatch(str(value)):
        return str(value)
    return str(default)


def _quote_glob_word(value: str) -> str:
    match = _GLOB_CHARACTER.search(value)
    if not match:
        return quote_user_interpolation(value)

    slash = value.rfind("/", 0, match.start() + 1)
    if slash >= 0:
        prefix = value[:slash]
        suffix = value[slash:]
    else:
        prefix = ""
        suffix = value

    quoted_prefix = quote_user_interpolation(prefix) if prefix else ""
    quoted_suffix = "".join(
        character if character in _SAFE_GLOB_SUFFIX else "\\" + character
        for character in suffix
    )
    return quoted_prefix + quoted_suffix


def quote_user_list(value) -> str:
    text = str(value)
    try:
        words = shlex.split(text)
    except ValueError:
        return quote_literal(text)
    if not words:
        return quote_literal("")
    return " ".join(_quote_glob_word(word) for word in words)


def shell_list(value) -> str:
    if isinstance(value, BashValue) and value.kind == BashValueKind.USER_INTERPOLATION:
        return quote_user_list(value)
    return shell_word(value)
