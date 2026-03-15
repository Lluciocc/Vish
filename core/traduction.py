import json
from core.debug import Info, Debug

class Traduction:
    model = {}
    
    @staticmethod
    def set_translate_model(lang: str):
        trad_file = Info.resource_path(f"assets/models/{lang}.json")
        try:
            with open(trad_file, encoding='utf-8') as data:
                Traduction.model = json.load(data)
        except FileNotFoundError:
            Debug.Error(f"Cannot find language model for {lang}")

    @staticmethod
    def get_trad(msgid, fallback="", **kwargs):
        text = Traduction.model.get(msgid, fallback)
        try:
            return text.format(**kwargs)
        except Exception:
            return text
