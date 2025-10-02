# Чат-бот для благотворительного фонда «Продвижение»


- [О проекте](#anchor-about)
- [Цели проекта](#anchor-target)
- [Основные функции](#anchor-functions)
- [Установка и запуск](#anchor-install)
- [Развертывание](#anchor-deployment)
- [Используемый стек](#anchor-stack)
- [Команда проекта](#anchor-team)


#### Эндпоинты
**Сайт** - https://dvizhenie.sytes.net
**Админ-панель** - https://dvizhenie.sytes.net/admin/ \
**АПИ** - https://dvizhenie.sytes.net/api/v1/ \
**REDOC (Только в Debug режиме)** - https://dvizhenie.sytes.net/redoc/ \
**Swagger** - https://dvizhenie.sytes.net/swagger/ \
**ТГ-Бот** - https://t.me/ProDvizhenie_5Bot \

<a name="anchor-about"></a>
## О проекте
Чат-бот для автоматизации сбора заявок от подопечных и их представителей на сайте dvizhenie.life и в мессенджерах.

<a name="anchor-target"></a>
## Цели проекта
Сократить время обработки заявок сотрудниками фонда

Сделать процесс заполнения анкеты удобным для пользователя

Обеспечить сохранение черновиков и возможность вернуться к анкете позже

Соответствие требованиям 152-ФЗ «О персональных данных»

<a name="anchor-functions"></a>
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

<a name="anchor-install"></a>
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
TELEGRAM_WEBHOOK_URL=https://<yourdomain.com>/telegram/webhook/
ADMIN_IDS=< TelegramID >

# Я.Диск токен
DISK_TOKEN=< Токен Яндекс-диска >
```
### Локальный запуск Django сервера
```bash
cd backend
```
```bash
python manage.py runserver
```

<a name="anchor-deployment"></a>
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

### Локальный запуск front-end приложения
```bash
cd frontend
```
```bash
npm i
npm run dev
```
#### Сборка front-end приложения

```bash
npm run build
```

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

<a name="anchor-stack"></a>
## Используемый стек Backend
* **Django 5.2.6**
* **Python 3.12**
* **PostgreSQL DB**
* **Docker**
* **pytest 8.4.2**

## Используемый стек Frontend

* **React**
* **TypeScript**
* **CSS**
* **redux/toolkit**
* **react-router**


<a name="anchor-team"></a>
## Команда проекта:
| Фото                                                                                                  | Участник            | Роль                          |Контакты|
|-------------------------------------------------------------------------------------------------------|---------------------|-------------------------------|-|
| ![Емелин Илья](https://github.com/IlyaEmelin/chatbot_promotion/commit/EmelinIliya.jpg)                | Емелин Илья         | TeamLead, backend-разработчик |[GitHub](https://github.com/IlyaEmelin), [Telegram](https://t.me/Ilya_Emelin)|
| ![Евстефеева Анна](https://github.com/IlyaEmelin/chatbot_promotion/commit/EvstefeevaAnna.jpg)         | Евстефеева Анна     | Project-менеджер              |[GitHub](https://github.com/AnnaEvstifeeva), [Telegram](https://t.me/annievstifeeva)|
| ![Богомолова Ольга](https://github.com/IlyaEmelin/chatbot_promotion/commit/BogomolovaOlga.jpg)         | Богомолова Ольга    | Product-менеджер              |[Telegram](https://t.me/OlgaBogomolova16)|
| ![Шарипова Динара](https://github.com/IlyaEmelin/chatbot_promotion/commit/SharipovaDinara.jpg)          | Шарипова Динара     | UX/UI дизайнер                |[Telegram](https://t.me/DinaraCalifornia)|
| ![Долгих Кирилл](https://github.com/IlyaEmelin/chatbot_promotion/commit/DolgikhKirill.jpg)            | Долгих Кирилл       | Frontend-разработчик          |[GitHub](https://github.com/nonncal), [Telegram](https://t.me/nonncal)|
| ![Кладова Ольга](https://github.com/IlyaEmelin/chatbot_promotion/commit/xxxxxxxxxxxxx.jpg)            | Кладова Ольга       | Frontend-разработчик          |[GitHub](https://github.com/OlgaKladova), [Telegram](https://t.me/MidoriKl)|
| ![Гурин Валерий](https://github.com/IlyaEmelin/chatbot_promotion/commit/GurinValeriy.jpg)             | Гурин Валерий       | Backend-разработчик           |[GitHub](https://github.com/FuntikPiggy), [Telegram](https://t.me/CallSign_Yakuza)|
| ![Мисхожев Олег](https://github.com/IlyaEmelin/chatbot_promotion/commit/MischozhevOleg.jpg)           | Мисхожев Олег       | Backend-разработчик           |[GitHub](https://github.com/OlegMiskhozhev), [Telegram](https://t.me/miskhozhev)|
| ![Михайлов Харалампий](https://github.com/IlyaEmelin/chatbot_promotion/commit/MihaylovHaralampiy.jpg) | Михайлов Харалампий | DevOps, backend-разработчик   |[GitHub](https://github.com/HarisNvr), [Telegram](https://t.me/HarisNvr)|

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>