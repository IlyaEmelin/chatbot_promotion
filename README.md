# Чат-бот для благотворительного фонда «Продвижение»
## О проекте
Чат-бот для автоматизации сбора заявок от подопечных и их представителей на сайте dvizhenie.life и в мессенджерах.

## Цели проекта
Сократить время обработки заявок сотрудниками фонда

Сделать процесс заполнения анкеты удобным для пользователя

Обеспечить сохранение черновиков и возможность вернуться к анкете позже

Соответствие требованиям 152-ФЗ «О персональных данных»

## Основные функции
### Для пользователей

Пошаговое заполнение анкеты с валидацией данных
Загрузка документов (JPG, PNG, PDF)
Сохранение прогресса и возможность продолжить позже
Предпросмотр перед отправкой
Адаптивный дизайн для ПК и смартфонов

### Для администраторов

Просмотр заявок в структурированном виде
Сортировка по статусам: «новая», «в обработке», «завершена»
Экспорт в Excel/Google Таблицы
Добавление комментариев к заявкам
Безопасный доступ через личный кабинет

## Установка и запуск

#### Клонирование репозитория

```bash
git clone https://github.com/IlyaEmelin/chatbot_promotion.git
```
```bash
cd chatbot_promotion
```
#### Пример .env файла
```
# base settings
SECRET_KEY=django-insecure-q%@n0uxcwe^)#k+l2cdqq6nwmi4ugauec3z483le+!%um_aaaa
DEBUG=true
CSRF_TRUSTED=http://51.250.113.76:580,http://localhost:3000/

#db settings
ENABLE_POSTGRES=false
POSTGRES_USER=django
POSTGRES_PASSWORD=django
POSTGRES_DB=django
DB_HOST=db
TZ=Europe/Moscow

# Logging level
LOGGING_DESTINATION=file  # file&console
LOGGING_LEVEL=DEBUG

# Telegram
TELEGRAM_BOT_TOKEN=< TelegramBotToken >
TELEGRAM_WEBHOOK_URL=https://<yourdomain.com>/webhook/
ADMIN_IDS=< TelegramID >

# Я.Диск токен
DISK_TOKEN=< Токен Яндекс-диска >
```
#### Локальный запуск Django сервера
```bash
cd backend
```
```bash
python manage.py runserver
```

#### Endpoints
Админ-панель - http://dvizhenie.myftp.biz:580/admin/ \
АПИ - http://dvizhenie.myftp.biz:580/api/v1/ \
REDOC (Только в Debug режиме) - http://dvizhenie.myftp.biz:580/redoc/

## Развертывание

### Docker Compose:

**Из корневой папки:**

```bash
sudo docker-compose up -d
```

#### При необходимости: зачистка базы и создание тестовых пользователей
```bash
python manage.py clear_data_base --add_user --add_survey_data
```
