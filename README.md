# Чат-бот для благотворительного фонда «Продвижение»
<a name="Start-point"></a>

- [О проекте](#anchor-about)
- [Цели проекта](#anchor-target)
- [Основные функции](#anchor-functions)
- [Установка и запуск](#anchor-install)
- [Развертывание](#anchor-deployment)
- [Технический стек](#anchor-stack)
- [Команда проекта](#anchor-team)


#### Эндпоинты

**Главная страница** - https://pro-dvizhenie.ddns.net \
**Админ-панель** - https://pro-dvizhenie.ddns.net/pro-admin-dvizh \
(Тестовый пользователь: login: **admin** password: **admin123**) \
**АПИ** - https://pro-dvizhenie.ddns.net/api/v1 \
**REDOC** - https://pro-dvizhenie.ddns.net/redoc \
**Swagger** - https://pro-dvizhenie.ddns.net/swagger \
**ТГ-Бот** - https://t.me/ProDvizhenie_5Bot

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

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

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

# frontend
VITE_API_URL=https://pro-dvizhenie.ddns.net/api/
REACT_APP_DEBUG=true

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
# Отображать в текстовом сообщение варианты ответа
TELEGRAM_SHOW_RESPONSE_CHOICE=true
# Отображать в телеграмм боте ответ "Вернуться к предыдущему вопросу"
TELEGRAM_SHOW_REVERT_PREVIOUS_QUESTION=true 

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

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

<a name="anchor-deployment"></a>
## Развертывание

### Подключение к удалённому серверу
Необходимо добавить свой публичный ssh ключ в список авторизованных на **YandexCloud**

Далее выполнить команду для подключения к серверу:
```bash
ssh -l fondprodvizhenie 158.160.185.86
```

### Docker Compose:

**Из корневой папки:**

Обычный перезапуск
```bash
sudo docker compose up -d
```

Перезапуск со сборкой нового билда
```bash
git pull
```
```bash
sudo docker compose up -d --build
```

#### При необходимости: зачистка базы и создание тестовых пользователей

Открываем терминал bash внутри контейнера
```bash
sudo docker exec -it chatbot_promotion-backend-1 /bin/bash
```

Очистка базы и создаём mock данные
```bash
python manage.py clear_data_base --add_user --add_survey_data
```
Или перезапись списка вопросов из файла steps.json
```bash
python manage.py add_survey_data --overwrite
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
## Технический стек backend
* [Python 3.12](https://www.python.org/)
* [Django 5.2.6](https://www.djangoproject.com/)
* [Pytest 8.4.2](https://pypi.org/project/pytest/)
* [PostgreSQL DB](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)

## Технический стек frontend
* [React](https://react.dev/)
* [TypeScript](https://www.typescriptlang.org/)
* [CSS](https://www.w3.org/TR/css/#css)
* [Redux Toolkit](https://redux-toolkit.js.org/)
* [React Router](https://reactrouter.com/)
  
<p align="right"><a href="#Start-point">Вернуться к началу</a></p>


<a name="anchor-team"></a>
## Команда проекта:
| Фото                                                                                                  | Участник            | Роль                          |Контакты|
|-------------------------------------------------------------------------------------------------------|---------------------|-------------------------------|-|
| ![EmelinIliya](https://github.com/user-attachments/assets/b679a20b-54ac-4929-9ffb-b84b58217a5f) | Емелин Илья | TeamLead, backend-разработчик |[GitHub](https://github.com/IlyaEmelin), [Telegram](https://t.me/Ilya_Emelin)|
| ![EvstefeevaAnna](https://github.com/user-attachments/assets/a5e2f675-558b-47bc-8cf3-d7d8ec003f4e) | Евстефеева Анна | Project-менеджер |[GitHub](https://github.com/AnnaEvstifeeva), [Telegram](https://t.me/annievstifeeva)|
| ![BogomolovaOlga](https://github.com/user-attachments/assets/33484226-14df-46e8-ae77-bfb8e30d0bb8) | Богомолова Ольга | Product-менеджер |[Telegram](https://t.me/OlgaBogomolova16)|
| ![SolovevaElena](https://github.com/user-attachments/assets/43cf86ac-6e24-459b-82fd-4c58827736bc) | Соловьёва Елена | UX/UI-дизайнер |[Telegram](https://t.me/Semidea)|
| ![SharipovaDinara](https://github.com/user-attachments/assets/681ffec2-95c5-46fb-8771-fe6bbaa4db4a) | Шарипова Динара | UX/UI-дизайнер |[Telegram](https://t.me/DinaraCalifornia)|
| ![MikhaylovHaralampiy](https://github.com/user-attachments/assets/94588f0d-cb69-46d8-8160-fcf6b2a19134) | Михайлов Харалампий | DevOps, backend-разработчик |[GitHub](https://github.com/HarisNvr), [Telegram](https://t.me/HarisNvr)|
| ![DolgikhKirill](https://github.com/user-attachments/assets/9f62d065-7205-4719-8261-75a251e43d03) | Долгих Кирилл | Frontend-разработчик |[GitHub](https://github.com/nonncal), [Telegram](https://t.me/nonncal)|
| ![KladovaOlga](https://github.com/user-attachments/assets/bf472fad-0ccd-437f-a5ff-372c1e7a728a) | Кладова Ольга | Frontend-разработчик |[GitHub](https://github.com/OlgaKladova), [Telegram](https://t.me/MidoriKl)|
| ![GurinValeriy](https://github.com/user-attachments/assets/096e634d-00a2-4b54-96e3-dcff56dbd33a) | Гурин Валерий | Backend-разработчик |[GitHub](https://github.com/FuntikPiggy), [Telegram](https://t.me/FuntikPiggy)|
| ![MiskhozhevOleg](https://github.com/user-attachments/assets/8d674c23-9895-4f21-9cf9-021339e42a1b) | Мисхожев Олег | Backend-разработчик |[GitHub](https://github.com/OlegMiskhozhev), [Telegram](https://t.me/miskhozhev)|

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>
