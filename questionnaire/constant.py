from typing import Final

MAX_LEN_STRING: Final = 40
STATUS_LEN: Final = 25
QUICK_SELECTION_LEN: Final = 20
ANSWER_LEN: Final = 20

STATUS_CHOICES = [
    ("draft", "Черновик"),
    ("new", "Новая"),
    ("waiting_docs", "Ожидает документов"),
    ("processing", "В обработке"),
    ("completed", "Завершена"),
]
