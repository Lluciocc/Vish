# Developer Guide

## General 
The Application is written using Python3 and the PySide6 (Qt) UI libary.
Before running the application make sure PySide6 is installed. (`pip install pyside6`)

## Branching
New features, bugfixes and translations should be developed on separate branches.
Note: The repo uses "Squash and Merge" on Pull Requests, so the number ob commits on a development branch does not affect the resulting Commit on `master`. Feel free to change/revise committed implementations as much as you like.

## Translation
All texts that are visible in the UI should be translated. If you add a new text element use the `Traduction.get_trad(key, value)` method to get the displayed text and add corresponding translation keys to the language specific json files in `assests/models/*.json` instead of hard coding the text string. 
Please Note: While you are not required to translate all texts you've added into all languages please create a translation issue after your PR has been merged.

## Creating a new Node
A standard note consits of a node_type, category, label and description. To create a new node the folling points have to be kept in mind:
1. The `node_type` and `label` must be the same in `@register_node()` and `super().__init__()`
2. A node class must ultimatily be derivied from `BaseNode` (e.g. math operation inherits from `MathNode` which inherits from `BaseNode`)
3. Each type of node should have a distinct color (exeception: same functionalliy but diffent Port Types (e.g. equals))
4. Each Port should have a tooltip

```python
@register_node("string_constant", category="Constants", label="String Constant", description="Represents a string constant value")
class StringConstantNode(BaseNode):
    def __init__(self):
        super().__init__("string_constant", "String Constant", "#BDC3C7")
        self.add_output("Value", PortType.STRING, "String value")
        self.properties["value"] = ""

    def emit_bash_value(self, context: BashContext) -> str:
        return f'"{self.properties.get("value", "")}"'
```

# References

* [PySide6 documentation](https://doc.qt.io/qtforpython-6/index.html)