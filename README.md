# SearchEstate

API для поиска и бронирования недвижимости. Django REST Framework проект с системой аутентификации JWT, управлением объявлениями, бронированиями и отзывами.

## 📋 Описание проекта

SearchEstate — это платформа для аренды недвижимости, которая позволяет:
- **Арендодателям** публиковать объявления о недвижимости
- **Арендаторам** искать и бронировать объекты
- **Всем пользователям** оставлять отзывы и просматривать историю

## 🏗️ Архитектура

### Приложения

- **users** — управление пользователями и аутентификацией
- **listings** — объявления недвижимости и поиск
- **bookings** — система бронирования
- **reviews** — система отзывов

### Технологии

- **Django 6.0.5** — веб-фреймворк
- **Django REST Framework 3.17.1** — API
- **SimpleJWT 5.5.1** — JWT аутентификация
- **drf-spectacular 0.29.0** — OpenAPI/Swagger документация
- **django-filter 25.2** — фильтрация данных
- **MySQL/SQLite** — база данных
- **Docker** — контейнеризация

## 🚀 Установка и запуск

### Требования

- Python 3.11+
- Docker и Docker Compose (опционально)

### Локальная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd SearchEstate
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**

Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=True

# Для MySQL (если USE_SQLITE=False)
DB_NAME=searchestate
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

5. **Миграции базы данных**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Запуск сервера**
```bash
python manage.py runserver
```

### Docker установка

1. **Сборка и запуск контейнеров**
```bash
docker-compose up --build
```

2. **Выполнение миграций**
```bash
docker-compose exec web python manage.py migrate
```

3. **Создание суперпользователя**
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📚 API Документация

После запуска сервера доступна Swagger документация:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## 🔐 Аутентификация

Проект использует JWT токены для аутентификации.

### Регистрация
```http
POST /api/users/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Имя пользователя",
  "role": "tenant"
}
```

### Вход
```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Использование токена
```http
Authorization: Bearer <access_token>
```

## 📡 API Эндпоинты

### Пользователи (`/api/users/`)

- `POST /register/` — регистрация пользователя
- `POST /login/` — вход в систему
- `POST /logout/` — выход из системы
- `POST /token/refresh/` — обновление токена
- `GET /profile/` — профиль пользователя
- `GET /current/` — текущий пользователь
- `POST /change-password/` — смена пароля

### Объявления (`/api/listings/`)

- `GET /` — список всех объявлений
- `POST /` — создание объявления (только арендодатель)
- `GET /my/` — мои объявления
- `GET /search/` — поиск объявлений
- `GET /popular/` — популярные объявления
- `GET /<id>/` — детальная информация об объявлении
- `POST /<id>/toggle-status/` — изменение статуса
- `GET /popular-searches/` — популярные поисковые запросы
- `GET /my-view-history/` — история просмотров пользователя
- `GET /<id>/view-history/` — история просмотров объявления

### Бронирования (`/api/bookings/`)

- `GET /` — список всех бронирований
- `POST /` — создание бронирования
- `GET /my/` — мои бронирования
- `GET /owner/` — бронирования моих объектов
- `GET /<id>/` — детальная информация о бронировании
- `POST /<id>/confirm/` — подтверждение бронирования
- `POST /<id>/reject/` — отклонение бронирования
- `POST /<id>/cancel/` — отмена бронирования
- `POST /<id>/checkin/` — подтверждение заезда

### Отзывы (`/api/reviews/`)

- `GET /` — список всех отзывов
- `POST /` — создание отзыва
- `GET /my/` — мои отзывы
- `GET /listing/<id>/` — отзывы для объявления
- `GET /<id>/` — детальная информация об отзыве

## 👥 Роли пользователей

### Администратор (admin)
- Полный доступ ко всем данным
- Управление пользователями
- Доступ к админ-панели: `/admin/`

### Арендодатель (landlord)
- Создание и управление объявлениями
- Подтверждение/отклонение бронирований
- Просмотр бронирований своих объектов

### Арендатор (tenant)
- Поиск и просмотр объявлений
- Создание бронирований
- Оставление отзывов
- Управление своими бронированиями

## 🏢 Модели данных


### Estate
- `owner` — владелец
- `title` — название
- `description` — описание
- `price` — цена
- `rooms` — количество комнат
- `housing_type` — тип жилья (apartment/house/studio/room)
- `city` — город
- `district` — район

### Listing
- `estate` — объект недвижимости
- `status` — статус (active/booked/archived)
- `views_count` — количество просмотров
- `created_at` — дата создания
- `updated_at` — дата обновления

### Booking
- `listing` — объявление
- `tenant` — арендатор
- `start_date` — дата начала
- `end_date` — дата окончания
- `status` — статус (new/confirmed/rejected/canceled)
- `is_checked_in` — подтверждение заезда

### Review
- `listing` — объявление
- `author` — автор
- `rating` — оценка (1-5)
- `text` — текст отзыва
- `created_at` — дата создания


### User
- `email` — email (используется для логина)
- `name` — имя
- `role` — роль (tenant/landlord/admin)
- `phone_number` — номер телефона
- `bio` — о себе
- `is_active` / `is_staff` — системные флаги

