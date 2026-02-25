from nodes.base_node import BaseNode
from core.port_types import PortType
from core.bash_context import BashContext
from nodes.registry import register_node

class MathNode(BaseNode):
    def _resolve(self, port, context: BashContext, default="0"):
        if port.connected_edges:
            return port.connected_edges[0].source.node.emit_bash_value(context)
        return default

@register_node("number_constant", category="Constants", label="Number Constant", description="Represents a number constant value")
class NumberConstant(MathNode):
    def __init__(self):
        super().__init__("number_constant", "Number Constant", "#BDC3C7")
        self.add_output("Value", PortType.INT, "Integer value")
        self.properties["value"] = 0

    def emit_bash_value(self, context: BashContext) -> str:
        return str(self.properties.get("value", 0))

@register_node("addition", category="Math", label="Addition")
class Addition(MathNode):
    def __init__(self):
        super().__init__("addition", "Addition", "#F1C40F")
        self.add_input("A", PortType.INT, "Summand")
        self.add_input("B", PortType.INT, "Summand")
        self.add_output("Result", PortType.INT, "Sum")

    def emit_bash_value(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"$(({a} + {b}))"

@register_node("subtraction", category="Math", label="Subtraction")
class Subtraction(MathNode):
    def __init__(self):
        super().__init__("subtraction", "Subtraction", "#E67E22")
        self.add_input("A", PortType.INT, "Minuend")
        self.add_input("B", PortType.INT, "Subtrahend")
        self.add_output("Result", PortType.INT, "Difference")

    def emit_bash_value(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"$(({a} - {b}))"

@register_node("multiplication", category="Math", label="Multiplication")
class Multiplication(MathNode):
    def __init__(self):
        super().__init__("multiplication", "Multiplication", "#9B59B6")
        self.add_input("A", PortType.INT, "Multiplier")
        self.add_input("B", PortType.INT, "Mulitplicand")
        self.add_output("Result", PortType.INT, "Product")

    def emit_bash_value(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"$(({a} * {b}))"

@register_node("division", category="Math", label="Division")
class Division(MathNode):
    def __init__(self):
        super().__init__("division", "Division", "#3498DB")
        self.add_input("A", PortType.INT, "Numerator")
        self.add_input("B", PortType.INT, "Denominator")
        self.add_output("Result", PortType.INT, "Fraction")

    def emit_bash_value(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"$(({a} / {b}))"

@register_node("modulo", category="Math", label="Modulo", description="Calculates the remainder of the division")
class Modulo(MathNode):
    def __init__(self):
        super().__init__("modulo", "Modulo", "#1ABC9C")
        self.add_input("A", PortType.INT, "Dividend")
        self.add_input("B", PortType.INT, "Divisor")
        self.add_output("Result", PortType.INT, "Remainder")

    def emit_bash_value(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"$(({a} % {b}))"

@register_node("less_than", category="Logic", label="Less Than", description="Is A less than B?")
class LessThan(MathNode):
    def __init__(self):
        super().__init__("less_than", "Less Than", "#95A5A6")
        self.add_input("A", PortType.INT, "A")
        self.add_input("B", PortType.INT, "B")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"(( {a} < {b} ))"

@register_node("greater_than", category="Logic", label="Greater Than", description="Is A greater than B?")
class GreaterThan(MathNode):
    def __init__(self):
        super().__init__("greater_than", "Greater Than", "#95A5A6")
        self.add_input("A", PortType.INT, "A")
        self.add_input("B", PortType.INT, "B")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"(( {a} > {b} ))"

@register_node("equals", category="Logic", label="Equals")
class Equals(MathNode):
    def __init__(self):
        super().__init__("equals", "Equals", "#2ECC71")
        self.add_input("A", PortType.INT, "A")
        self.add_input("B", PortType.INT, "B")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self._resolve(self.inputs[0], context)
        b = self._resolve(self.inputs[1], context)
        return f"(( {a} == {b} ))"

@register_node("logical_and", category="Logic", label="AND")
class LogicalAnd(MathNode):
    def __init__(self):
        super().__init__("logical_and", "AND", "#34495E")
        self.add_input("A", PortType.CONDITION, "A")
        self.add_input("B", PortType.CONDITION, "B")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self.inputs[0].get_condition(context)
        b = self.inputs[1].get_condition(context)
        if not a:
            a = "false"
        if not b:
            b = "false"
        return f"{a} && {b}"

@register_node("logical_or", category="Logic", label="OR")
class LogicalOr(MathNode):
    def __init__(self):
        super().__init__("logical_or", "OR", "#34495E")
        self.add_input("A", PortType.CONDITION, "A")
        self.add_input("B", PortType.CONDITION, "B")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self.inputs[0].get_condition(context)
        b = self.inputs[1].get_condition(context)
        if not a:
            a = "false"
        if not b:
            b = "false"
        return f"{a} || {b}"

@register_node("logical_not", category="Logic", label="NOT")
class LogicalNot(MathNode):
    def __init__(self):
        super().__init__("logical_not", "NOT", "#34495E")
        self.add_input("A", PortType.CONDITION, "A")
        self.add_output("Result", PortType.CONDITION, "Result")

    def emit_condition(self, context: BashContext) -> str:
        a = self.inputs[0].get_condition(context)
        if not a:
            a = "false"
        return f"! {a}"

@register_node("command_condition", category="Logic", label="Command Condition", description="Uses a custom command as a condition")
class CommandConditionNode(BaseNode):
    def __init__(self):
        super().__init__("command_condition", "Command Condition", "#34495E")
        self.add_output("command", PortType.CONDITION, "Command")
        self.properties["command"] = ""

    def emit_condition(self, context: BashContext) -> str:
        return f"[ {self.properties['command']} ]"