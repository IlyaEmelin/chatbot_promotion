from typing import Final

MAX_LEN_STRING: Final = 40
STATUS_LEN: Final = 25
ANSWER_LEN: Final = 30
QUESTION_TYPE_LEN: Final = 30
FILE_URL_MAX_LEN = 2048

STATUS_CHOICES = [
    ("new", "Новая"),
    ("waiting_docs", "Ожидает документов"),
    ("processing", "В обработке"),
    ("completed", "Завершена"),
]

QUESTION_TYPE = [
    ("standart", "Cтандартный"),
    ("start", "Стартовый вопрос"),
    ("waiting_docs", "Ожидает документов"),
]

EXTERNAL_TABLE_FIELD_NAME_CHOICES = [
    ("User.agent", "Контактное лицо"),
    ("User.first_name", "Имя"),
    ("User.last_name", "Фамилия"),
    ("User.patronymic", "Отчество"),
    ("User.residence", "Город проживания"),
    ("User.phone_number", "Телефонный номер"),
    ("User.email", "Электронная почта"),
    ("User.telegram_username", "Имя пользователя в Телеграм"),
    ("User.birthday", "Дата рождения подопечного (в формате ДД.ММ.ГГГГ)"),
]
