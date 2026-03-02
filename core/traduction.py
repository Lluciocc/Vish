import json
from core.debug import Info

class Traduction:
    model = {}
    node_colors = {}
    
    @staticmethod
    def set_translate_model(lang: str):
        trad_file = Info.resource_path(f"assets/models/{lang}.json")
        try:
            with open(trad_file, encoding='utf-8') as data:
                Traduction.model = json.load(data)
        except FileNotFoundError:
            print(f"Cannot find language model for {lang}")

    @staticmethod
    def get_trad(msgid, fallback="", **kwargs):
        text = Traduction.model.get(msgid, fallback)
        try:
            return text.format(**kwargs)
        except Exception:
            return text
        
    @staticmethod
    def set_node_colors():
        trad_file = Info.resource_path(f"assets/models/node_colors.json")
        try:
            with open(trad_file) as data:
                Traduction.node_colors = json.load(data)
        except FileNotFoundError:
            print(f"Cannot find node_colors file")

    @staticmethod
    def get_color(node_type):
        color = Traduction.node_colors.get(node_type)
        return color
        