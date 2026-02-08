import json
from core.debug import Debug, Info

class Config:
    DEBUG = False
    USING_TTY = True
    lang = "en"
    theme = "dark"
    
class ConfigManager:
    @staticmethod
    def serialize_config(config: Config):
        for attr in dir(config):
            if not attr.startswith("__") and not callable(getattr(config, attr)):
                yield (attr, getattr(config, attr))

    @staticmethod
    def load_config():
        try:
            with open(Info.get_config_path(), "r") as f:
                config_dict = json.load(f)
                for key, value in config_dict.items():
                    if hasattr(Config, key):
                        current = getattr(Config, key)
                        if isinstance(value, type(current)):
                            setattr(Config, key, value)
                        else:
                            Debug.Warn(f"Invalid type for {key}, ignoring")
        except FileNotFoundError:
            Debug.Warn("Config file not found. Using default configuration.")
        except Exception as e:
            Debug.Error(f"Failed to load config: {e}")
    @staticmethod
    def save_config():
        config_dict = dict(ConfigManager.serialize_config(Config))
        with open(Info.get_config_path(), "w") as f:
            json.dump(config_dict, f, indent=4)