import json
from core.debug import Info

class NodeColor:
    node_colors = {}

    @staticmethod
    def set_node_colors():
        filename = "node_colors.json"
        color_file = Info.resource_path(f"assets/models/{filename}")
        try:
            with open(color_file) as data:
                NodeColor.node_colors = json.load(data)
        except FileNotFoundError:
            print(f"Cannot find file '{filename}'.")

    @staticmethod
    def get_color(node_type):
        color = NodeColor.node_colors.get(node_type)
        return color