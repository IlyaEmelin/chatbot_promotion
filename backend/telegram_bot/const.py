from enum import StrEnum


class TelegramCommand(StrEnum):
    """Класс телеграмм команд"""

    START = "start"
    STATUS = "status"
    PROCESSING = "processing"
    HELP = "help"
    LOG = "log"

    def get_call_name(self) -> str:
        """
        Получить команду для нажатия

        Returns:
            str: команда для нажатия
        """
        return f"/{self.value}"
