import json

class Traduction:
    model = {}
    
    @staticmethod
    def set_translate_model(lang: str):
        trad_file = "assets/models/{}.json".format(lang)
        try:
            with open(trad_file) as data:
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
        