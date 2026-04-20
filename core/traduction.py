import json
from core.debug import Info, Debug
import os

class Traduction:
    langs_path = Info.resource_path('assets/models/lang')
    models = {}
    current_model = ''

    @staticmethod
    def get_languages():
        langs = []
        for lang_id in Traduction.models:
            if lang_id == 'en':
                continue
            model = Traduction.models[lang_id]
            lang_name = model.get('language_name', 'Unknown language')
            langs.append((lang_name, lang_id))
        langs.sort(key=lambda pair : pair[1])
        langs.insert(0, ('English', 'en'))
        return langs


    @staticmethod
    def load_languages():
        Traduction.models = {}
        for file in os.scandir(Traduction.langs_path):
            if file.is_file() and file.name[-5:] == '.json':
                try:
                    with open(file.path, encoding='utf-8') as data:
                        lang = json.load(data)
                        file_name = file.name[:-5]
                        Traduction.models[file_name] = lang
                except json.JSONDecodeError:
                    Debug.Error(f'{file.path} is not a valid json file')
                except UnicodeDecodeError:
                    Debug.Error(f'{file.path} is not compatible with unicode encoding')

    @staticmethod
    def set_translate_model(lang: str):
        if lang in Traduction.models:
            Traduction.current_model = lang
        else:
            Debug.Error(f"Cannot find language model for {lang}")

    @staticmethod
    def get_trad(msgid, fallback="", **kwargs):
        text = Traduction.models[Traduction.current_model].get(msgid, fallback)
        try:
            return text.format(**kwargs)
        except Exception:
            return text
