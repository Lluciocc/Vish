from pathlib import Path
import datetime

class Colors:
    RESET  = "\033[0m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    GREEN  = "\033[32m"
    CYAN   = "\033[36m"

class Logger:
    logged_messages = []

    @staticmethod
    def _log(level: str, message: str, color: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        msg_log = f"[{timestamp}] [{level}] {message}"
        Logger.logged_messages.append(msg_log)

        from core.config import Config
        if Config.DEBUG:
            msg = f"{color}{msg_log} {Colors.RESET}"
            print(msg)

    @staticmethod
    def LogMessage(message: str):
        message = Logger.anonymize(message)
        Logger._log("INFO", message, Colors.CYAN)

    @staticmethod
    def LogWarning(message: str):
        message = Logger.anonymize(message)
        Logger._log("WARN", message, Colors.YELLOW)

    @staticmethod
    def LogError(message: str):
        message = Logger.anonymize(message)
        Logger._log("ERROR", message, Colors.RED)

    @staticmethod
    def save_logged_messages(message_error: str = None):
        from core.debug import Info

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = Path(Info.get_config_path()).parent / "logs" / f"vish_log_{timestamp}.log"

        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "w") as f:
            f.write("\n".join(Logger.logged_messages))
            if message_error:
                f.write(f"\n{message_error}")

        Logger.LogMessage(f"Logged messages saved to {log_path}")

    @staticmethod
    def anonymize(message: str):
        message = message.replace(f"{Path.home()}", "~")
        return message
