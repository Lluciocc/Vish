class Colors:
    RESET  = "\033[0m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    GREEN  = "\033[32m"
    CYAN   = "\033[36m"

class Logger:
    @staticmethod
    def LogMessage(message: str):
        print(f"{Colors.CYAN}[INFO] {message} {Colors.RESET}")

    @staticmethod
    def LogWarning(message: str):
        print(f"{Colors.YELLOW}[WARN] {message} {Colors.RESET}")

    @staticmethod
    def LogError(message: str):
        print(f"{Colors.RED}[ERROR] {message} {Colors.RESET}")
