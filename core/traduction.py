import json
from core.debug import Info, Debug
import os

class Traduction:
    langs_path = Info.resource_path('assets/models/lang')
    model = {}

    @staticmethod
    def get_languages():
        langs = []
        for file in os.scandir(Traduction.langs_path):
            if file.is_file() and file.name[-5:] == '.json' and file.name != 'en.json':
                try:
                    with open(file.path, encoding='utf-8') as data:
                        lang = json.load(data)
                        lang_name = lang.get('language_name', 'Unknown language')
                        file_name = file.name[:-5]
                        langs.append((lang_name, file_name))
                except json.JSONDecodeError:
                    Debug.Error(f'{file.path} is not a valid json file')
                except UnicodeDecodeError:
                    Debug.Error(f'{file.path} is not compatible with unicode encoding')
        langs.sort(key=lambda pair : pair[1])
        langs.insert(0, ('English', 'en'))
        return langs

    @staticmethod
    def set_translate_model(lang: str):
        trad_file = os.path.join(Traduction.langs_path, lang + '.json')
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
