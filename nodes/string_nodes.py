# string_nodes.py
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

from core.port_types import PortType
from nodes.filesystem_nodes import ArgumentNode
from nodes.registry import register_node


class BinaryStringNode(ArgumentNode):
    def _setup(self, first="text", second="value"):
        self.add_input(first.title(), PortType.STRING, first.title())
        self.add_input(second.title(), PortType.STRING, second.title())
        self.properties[first] = ""
        self.properties[second] = ""


@register_node(
    "concatenate_strings",
    category="Strings",
    label="Concatenate Strings",
    description="Concatenates two strings",
)
class ConcatenateStringsNode(BinaryStringNode):
    def __init__(self):
        super().__init__("concatenate_strings", "Concatenate Strings")
        self._setup("first", "second")
        self.add_output("Result", PortType.STRING, "Concatenated text")

    def emit_bash_value(self, context):
        first = self._argument("first", 0, context)
        second = self._argument("second", 1, context)
        return f"$(printf '%s%s' {first} {second})"


@register_node(
    "string_length",
    category="Strings",
    label="String Length",
    description="Returns the number of characters in text",
)
class StringLengthNode(ArgumentNode):
    def __init__(self):
        super().__init__("string_length", "String Length")
        self.add_input("Text", PortType.STRING, "Text")
        self.add_output("Length", PortType.INT, "Character count")
        self.properties["text"] = ""

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        return f"$(VISH_TEXT={text}; printf '%s' \"${{#VISH_TEXT}}\")"


class StringPredicateNode(BinaryStringNode):
    operator = "=="
    prefix = ""
    suffix = ""

    def _condition(self, context):
        text = self._argument("text", 0, context)
        value = self._argument("value", 1, context)
        return f"[[ {text} {self.operator} {self.prefix}{value}{self.suffix} ]]"

    def emit_condition(self, context):
        return self._condition(context)


@register_node(
    "contains",
    category="Strings",
    label="Contains",
    description="Checks whether text contains a value",
)
class ContainsNode(StringPredicateNode):
    prefix = "*"
    suffix = "*"

    def __init__(self):
        super().__init__("contains", "Contains")
        self._setup("text", "value")
        self.add_output("Result", PortType.CONDITION, "Whether text contains value")


@register_node(
    "starts_with",
    category="Strings",
    label="Starts With",
    description="Checks whether text starts with a value",
)
class StartsWithNode(StringPredicateNode):
    suffix = "*"

    def __init__(self):
        super().__init__("starts_with", "Starts With")
        self._setup("text", "value")
        self.add_output("Result", PortType.CONDITION, "Whether text starts with value")


@register_node(
    "ends_with",
    category="Strings",
    label="Ends With",
    description="Checks whether text ends with a value",
)
class EndsWithNode(StringPredicateNode):
    prefix = "*"

    def __init__(self):
        super().__init__("ends_with", "Ends With")
        self._setup("text", "value")
        self.add_output("Result", PortType.CONDITION, "Whether text ends with value")


@register_node(
    "replace_text",
    category="Strings",
    label="Replace Text",
    description="Replaces every occurrence of text",
)
class ReplaceTextNode(ArgumentNode):
    def __init__(self):
        super().__init__("replace_text", "Replace Text")
        self.add_input("Text", PortType.STRING, "Original text")
        self.add_input("Search", PortType.STRING, "Text to replace")
        self.add_input("Replacement", PortType.STRING, "Replacement text")
        self.add_output("Result", PortType.STRING, "Modified text")
        self.properties["text"] = ""
        self.properties["search"] = ""
        self.properties["replacement"] = ""

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        search = self._argument("search", 1, context)
        replacement = self._argument("replacement", 2, context)
        return (
            f"$(VISH_TEXT={text}; VISH_SEARCH={search}; "
            f"VISH_REPLACEMENT={replacement}; "
            "if [[ -z $VISH_SEARCH ]]; then printf '%s' \"$VISH_TEXT\"; "
            "else printf '%s' "
            "\"${VISH_TEXT//$VISH_SEARCH/$VISH_REPLACEMENT}\"; fi)"
        )


@register_node(
    "substring",
    category="Strings",
    label="Substring",
    description="Extracts part of a string",
)
class SubstringNode(ArgumentNode):
    def __init__(self):
        super().__init__("substring", "Substring")
        self.add_input("Text", PortType.STRING, "Original text")
        self.add_input("Start", PortType.INT, "Zero-based start index")
        self.add_input("Length", PortType.INT, "Number of characters")
        self.add_output("Result", PortType.STRING, "Extracted text")
        self.properties["text"] = ""
        self.properties["start"] = 0
        self.properties["length"] = 1

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        start = self._argument("start", 1, context, 0)
        length = self._argument("length", 2, context, 1)
        return (
            f"$(VISH_TEXT={text}; VISH_START={start}; VISH_LENGTH={length}; "
            "printf '%s' \"${VISH_TEXT:VISH_START:VISH_LENGTH}\")"
        )


class UnaryStringNode(ArgumentNode):
    def _setup(self, output_type=PortType.STRING):
        self.add_input("Text", PortType.STRING, "Text")
        self.add_output("Result", output_type, "Result")
        self.properties["text"] = ""


@register_node(
    "trim",
    category="Strings",
    label="Trim",
    description="Removes leading and trailing whitespace",
)
class TrimNode(UnaryStringNode):
    def __init__(self):
        super().__init__("trim", "Trim")
        self._setup()

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        return (
            f"$(printf '%s' {text} | "
            "sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        )


@register_node(
    "uppercase",
    category="Strings",
    label="Uppercase",
    description="Converts text to uppercase",
)
class UppercaseNode(UnaryStringNode):
    def __init__(self):
        super().__init__("uppercase", "Uppercase")
        self._setup()

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        return f"$(VISH_TEXT={text}; printf '%s' \"${{VISH_TEXT^^}}\")"


@register_node(
    "lowercase",
    category="Strings",
    label="Lowercase",
    description="Converts text to lowercase",
)
class LowercaseNode(UnaryStringNode):
    def __init__(self):
        super().__init__("lowercase", "Lowercase")
        self._setup()

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        return f"$(VISH_TEXT={text}; printf '%s' \"${{VISH_TEXT,,}}\")"


@register_node(
    "split",
    category="Strings",
    label="Split",
    description="Splits text into newline-separated parts",
)
class SplitNode(BinaryStringNode):
    def __init__(self):
        super().__init__("split", "Split")
        self._setup("text", "delimiter")
        self.add_output("Parts", PortType.STRING, "Newline-separated parts")

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        delimiter = self._argument("delimiter", 1, context)
        return (
            f"$(VISH_TEXT={text}; VISH_DELIMITER={delimiter}; "
            "if [[ -z $VISH_DELIMITER ]]; then printf '%s' \"$VISH_TEXT\"; "
            "else printf '%s' \"${VISH_TEXT//$VISH_DELIMITER/$'\\n'}\"; fi)"
        )


@register_node(
    "join",
    category="Strings",
    label="Join",
    description="Joins newline-separated items with a delimiter",
)
class JoinNode(BinaryStringNode):
    def __init__(self):
        super().__init__("join", "Join")
        self._setup("items", "delimiter")
        self.add_output("Result", PortType.STRING, "Joined text")

    def emit_bash_value(self, context):
        items = self._argument("items", 0, context)
        delimiter = self._argument("delimiter", 1, context)
        return (
            f"$(VISH_ITEMS={items}; VISH_DELIMITER={delimiter}; VISH_FIRST=1; "
            "while IFS= read -r VISH_ITEM || [[ -n $VISH_ITEM ]]; do "
            "if (( VISH_FIRST )); then VISH_FIRST=0; "
            "else printf '%s' \"$VISH_DELIMITER\"; fi; "
            "printf '%s' \"$VISH_ITEM\"; done <<< \"$VISH_ITEMS\")"
        )


@register_node(
    "match_regex",
    category="Strings",
    label="Match Regex",
    description="Checks whether text matches a regular expression",
)
class MatchRegexNode(BinaryStringNode):
    def __init__(self):
        super().__init__("match_regex", "Match Regex")
        self._setup("text", "pattern")
        self.add_output("Result", PortType.CONDITION, "Whether the regex matches")

    def emit_condition(self, context):
        text = self._argument("text", 0, context)
        pattern = self._argument("pattern", 1, context)
        return f"(VISH_REGEX={pattern}; [[ {text} =~ $VISH_REGEX ]])"


@register_node(
    "capture_regex",
    category="Strings",
    label="Capture Regex",
    description="Returns one capture group from a regular expression match",
)
class CaptureRegexNode(ArgumentNode):
    def __init__(self):
        super().__init__("capture_regex", "Capture Regex")
        self.add_input("Text", PortType.STRING, "Text to search")
        self.add_input("Pattern", PortType.STRING, "Regular expression")
        self.add_input("Group", PortType.INT, "Capture group index")
        self.add_output("Capture", PortType.STRING, "Captured text")
        self.properties["text"] = ""
        self.properties["pattern"] = ""
        self.properties["group"] = 1

    def emit_bash_value(self, context):
        text = self._argument("text", 0, context)
        pattern = self._argument("pattern", 1, context)
        group = self._argument("group", 2, context, 1)
        return (
            f"$(VISH_TEXT={text}; VISH_REGEX={pattern}; VISH_GROUP={group}; "
            "if [[ $VISH_TEXT =~ $VISH_REGEX ]]; then "
            "printf '%s' \"${BASH_REMATCH[$VISH_GROUP]}\"; fi)"
        )


@register_node(
    "multiline_text",
    category="Constants",
    label="Multiline Text",
    description="Stores a multiline text constant",
)
class MultilineTextNode(ArgumentNode):
    def __init__(self):
        super().__init__("multiline_text", "Multiline Text")
        self.add_output("Text", PortType.STRING, "Multiline text")
        self.properties["text"] = ""
        self.multiline_properties.add("text")

    def emit_bash_value(self, context):
        return self._argument("text", None, context)
