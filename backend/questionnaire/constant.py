from typing import Final
from enum import Enum

MAX_LEN_STRING: Final = 40
STATUS_LEN: Final = 25
ANSWER_LEN: Final = 30
QUESTION_TYPE_LEN: Final = 30
FILE_URL_MAX_LEN = 2048


class SurveyStatus(Enum):
    NEW = ("new", "Новая", "🆕")
    WAITING_DOCS = ("waiting_docs", "Ожидает документов", "📎")
    PROCESSING = ("processing", "В обработке", "⏳")
    COMPLETED = ("completed", "Завершена", "✅")

    def __init__(self, value: str, label: str, icon: str) -> None:
        """
        Конструктор

        Args:
            value: значение
            label: описание
            icon: иконка
        """
        self.__value = value
        self.__label = label
        self.__icon = icon

    @property
    def value(self) -> str:
        """str: значение"""
        return self.__value

    @property
    def label(self) -> str:
        """str: описание"""
        return self.__label

    @property
    def ext_label(self) -> str:
        """str: расширенное описание"""
        return f"{self.__icon} {self.__label}"

    @classmethod
    def choices(cls) -> tuple[tuple[str, str], ...]:
        """Возвращает список кортежей для использования в моделях Django"""
        return tuple((status.value, status.label) for status in cls)

    @classmethod
    def from_value(cls, value: str) -> "SurveyStatus":
        """
        Получить объект Enum по значению value

        Args:
            value: значение

        Returns:
            SurveyStatus: экземпляр enum
        """
        """Получить объект Enum по значению value"""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Недопустимое значение статуса: {value}")

    @classmethod
    def get_ext_label(cls, value: str) -> str:
        """
        Получить расширенное описание по значению value

        Args:
            value: значение

        Returns:
            str: расширенное описание
        """
        try:
            return cls.from_value(value).ext_label
        except ValueError:
            return "❌ Ошибка"


QUESTION_TYPE = [
    ("standart", "Cтандартный"),
    ("start", "Стартовый вопрос"),
    ("waiting_docs", "Ожидает документов"),
]

EXTERNAL_TABLE_FIELD_NAME_CHOICES = [
    ("User.first_name", "Имя"),
    ("User.last_name", "Фамилия"),
    ("User.patronymic", "Отчество"),
    ("User.ward_first_name", "Имя"),
    ("User.ward_last_name", "Фамилия"),
    ("User.ward_patronymic", "Отчество"),
    ("User.residence", "Город проживания"),
    ("User.phone_number", "Телефонный номер"),
    ("User.email", "Электронная почта"),
    ("User.telegram_username", "Имя пользователя в Телеграм"),
    ("User.birthday", "Дата рождения подопечного (в формате ДД.ММ.ГГГГ)"),
]
