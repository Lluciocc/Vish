# bash_values.py
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Semantic Bash values and their final rendering boundaries."""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from enum import Enum, auto


class BashValueKind(Enum):
    LITERAL = auto()
    VARIABLE = auto()
    EXPRESSION = auto()
    PATH_EXPRESSION = auto()
    GLOB_EXPRESSION = auto()
    COMMAND_SUBSTITUTION = auto()
    ARITHMETIC = auto()
    NUMBER = auto()
    CONDITION = auto()
    RAW_COMMAND = auto()


@dataclass(frozen=True)
class BashValue:
    """An unrendered semantic value.

    ``text`` never contains surrounding shell quotes. Keeping this object from
    inheriting from ``str`` makes accidental rendering loss visible instead of
    silently turning an expression into literal text.
    """

    kind: BashValueKind
    text: str


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
    return BashValue(BashValueKind.LITERAL, str(value))


def variable(name: str) -> BashValue:
    return BashValue(BashValueKind.VARIABLE, identifier(name, "VAR"))


def expression(value: str) -> BashValue:
    return BashValue(BashValueKind.EXPRESSION, str(value))


def command_substitution(command: str) -> BashValue:
    return BashValue(BashValueKind.COMMAND_SUBSTITUTION, command)


def arithmetic(expression_text: str) -> BashValue:
    return BashValue(BashValueKind.ARITHMETIC, expression_text)


def number(value, default="0") -> BashValue:
    text = str(value)
    if not _NUMBER.fullmatch(text):
        text = str(default)
    return BashValue(BashValueKind.NUMBER, text)


def condition(expression_text: str) -> BashValue:
    return BashValue(BashValueKind.CONDITION, expression_text)


def raw_command(command: str) -> BashValue:
    return BashValue(BashValueKind.RAW_COMMAND, command)


def identifier(value, default: str) -> str:
    text = str(value)
    return text if _IDENTIFIER.fullmatch(text) else default


def _parameter_at(text: str, index: int):
    for pattern in (_BRACED_PARAMETER, _SIMPLE_PARAMETER):
        match = pattern.match(text, index)
        if match:
            return match
    return None


def _contains_parameter(text: str) -> bool:
    index = 0
    while index < len(text):
        if (
            text[index] == "$"
            and (index == 0 or text[index - 1] != "\\")
            and _parameter_at(text, index)
        ):
            return True
        index += 1
    return False


def _strip_legacy_outer_quotes(text: str) -> str:
    """Normalize expression fields saved with shell quotes in older projects."""

    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    return text


def user_interpolation(value, *, expand_tilde=False) -> BashValue:
    """Parse an expression-enabled property without rendering it.

    Only parameter references are promoted to expressions. User-authored
    command substitutions and backticks remain literal data.
    """

    text = _strip_legacy_outer_quotes(str(value))
    if expand_tilde and (text == "~" or text.startswith("~/")):
        text = "$HOME" + text[1:]
    if _contains_parameter(text):
        return expression(text)
    return literal(text)


def path_expression(value, *, expand_tilde=True) -> BashValue:
    text = str(value)
    # Older project files may contain one shell word with quotes already
    # attached (for example ``"$HOME/Downloads"/*``).  Normalize that legacy
    # representation back to its semantic text before classifying it.
    try:
        parsed = shlex.split(text)
    except ValueError:
        parsed = []
    if len(parsed) == 1:
        text = parsed[0]
    if expand_tilde and (text == "~" or text.startswith("~/")):
        text = "$HOME" + text[1:]
    kind = (
        BashValueKind.GLOB_EXPRESSION
        if _GLOB_CHARACTER.search(text)
        else BashValueKind.PATH_EXPRESSION
    )
    return BashValue(kind, text)


def _double_quote_literal(text: str) -> str:
    escaped = "".join(
        "\\" + character if character in {"\\", '"', "`", "$"} else character
        for character in text
    )
    return f'"{escaped}"'


def quote_literal(value) -> str:
    """Render data that must never undergo shell expansion."""

    text = str(value)
    if "$" in text or "`" in text:
        return shlex.quote(text)
    return _double_quote_literal(text)


def _render_interpolation(text: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "$" and (index == 0 or text[index - 1] != "\\"):
            match = _parameter_at(text, index)
            if match:
                pieces.append(match.group(0))
                index = match.end()
                continue

        character = text[index]
        if character in {"\\", '"', "`", "$"}:
            pieces.append("\\" + character)
        else:
            pieces.append(character)
        index += 1
    return '"' + "".join(pieces) + '"'


def _render_glob(text: str) -> str:
    match = _GLOB_CHARACTER.search(text)
    if not match:
        return _render_interpolation(text)

    slash = text.rfind("/", 0, match.start() + 1)
    if slash >= 0:
        prefix = text[:slash]
        suffix = text[slash:]
    else:
        prefix = ""
        suffix = text

    quoted_prefix = _render_interpolation(prefix) if prefix else ""
    rendered_suffix: list[str] = []
    index = 0
    while index < len(suffix):
        if suffix[index] == "$":
            parameter = _parameter_at(suffix, index)
            if parameter:
                rendered_suffix.append(_render_interpolation(parameter.group(0)))
                index = parameter.end()
                continue
        character = suffix[index]
        rendered_suffix.append(
            character if character in _SAFE_GLOB_SUFFIX else "\\" + character
        )
        index += 1
    return quoted_prefix + "".join(rendered_suffix)


def render_word(value: BashValue) -> str:
    """Render one semantic value as one shell argument."""

    if not isinstance(value, BashValue):
        raise TypeError("render_word() requires a BashValue")
    if value.kind == BashValueKind.LITERAL:
        return quote_literal(value.text)
    if value.kind == BashValueKind.VARIABLE:
        return f'"${value.text}"'
    if value.kind in {BashValueKind.EXPRESSION, BashValueKind.PATH_EXPRESSION}:
        return _render_interpolation(value.text)
    if value.kind == BashValueKind.GLOB_EXPRESSION:
        return _render_glob(value.text)
    if value.kind == BashValueKind.COMMAND_SUBSTITUTION:
        return f'"$({value.text})"'
    if value.kind == BashValueKind.ARITHMETIC:
        return f"$(({value.text}))"
    if value.kind == BashValueKind.NUMBER:
        return value.text
    if value.kind == BashValueKind.RAW_COMMAND:
        return quote_literal(value.text)
    raise ValueError(f"{value.kind.name} cannot be rendered as a shell word")


def render_assignment(value: BashValue) -> str:
    return render_word(value)


def render_arithmetic(value: BashValue, default="0") -> str:
    if value.kind == BashValueKind.NUMBER:
        return value.text
    if value.kind == BashValueKind.VARIABLE:
        return f"${value.text}"
    if value.kind == BashValueKind.COMMAND_SUBSTITUTION:
        return f"$({value.text})"
    if value.kind == BashValueKind.ARITHMETIC:
        return f"$(({value.text}))"
    if value.kind == BashValueKind.LITERAL and _NUMBER.fullmatch(value.text):
        return value.text
    return str(default)


def render_condition(value: BashValue) -> str:
    if value.kind != BashValueKind.CONDITION:
        raise TypeError("render_condition() requires a condition")
    return value.text


def render_raw_command(value: BashValue) -> str:
    """Render a value at an explicitly raw command node boundary."""

    if value.kind in {BashValueKind.LITERAL, BashValueKind.RAW_COMMAND}:
        return value.text
    if value.kind == BashValueKind.VARIABLE:
        return f"${value.text}"
    if value.kind == BashValueKind.COMMAND_SUBSTITUTION:
        return f"$({value.text})"
    if value.kind == BashValueKind.ARITHMETIC:
        return f"$(({value.text}))"
    return value.text


def user_loop_list(value) -> tuple[BashValue, ...]:
    """Parse a loop-list property into semantic path/glob values."""

    text = str(value)
    try:
        words = shlex.split(text)
    except ValueError:
        return (literal(text),)
    if not words:
        return (literal(""),)
    return tuple(path_expression(word) for word in words)


def render_loop_list(value: BashValue | tuple[BashValue, ...]) -> str:
    values = value if isinstance(value, tuple) else (value,)
    return " ".join(render_word(item) for item in values)
