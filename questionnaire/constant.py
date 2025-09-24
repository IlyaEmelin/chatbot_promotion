from typing import Final

MAX_LEN_STRING: Final = 40
STATUS_LEN: Final = 25
ANSWER_LEN: Final = 30
QUESTION_TYPE_LEN: Final = 30
FILE_URL_MAX_LEN = 2048

STATUS_CHOICES = [
    ("draft", "Черновик"),
    ("new", "Новая"),
    ("waiting_docs", "Ожидает документов"),
    ("processing", "В обработке"),
    ("completed", "Завершена"),
]

QUESTION_TYPE = [
    ("standart", "Cтандартный"),
    ("start_web", "Стартовый вопрос для веб"),
    ("start_telegram", "Стартовый вопрос для телеграм"),
    ("waiting_docs", "Ожидает документов"),
]
