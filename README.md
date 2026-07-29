# Animal Weighing System

Система учёта поголовья животных: типы животных, породы, карточки животных, история взвешиваний. Ролевая модель (`user`/`admin`), регистрация с активацией по email-ссылке. REST API (FastAPI) + веб-интерфейс (React).

## Стек

- **Backend:** Python, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, JWT-аутентификация
- **Frontend:** React (Vite), react-router-dom
- **Тесты:** pytest
- **Инфраструктура:** Docker, Docker Compose

## Быстрый запуск (backend + БД через Docker)

1. Скопировать пример переменных окружения и заполнить своими значениями:

   ```
   cp .env.example .env
   ```

   В `.env` нужно указать `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` и `JWT_SECRET_KEY` (любая непустая строка для теста, для продакшена — случайный секрет).

2. Поднять backend и Postgres:

   ```
   docker compose up --build
   ```

   Миграции Alembic применяются автоматически при старте контейнера (см. `backend/Dockerfile`) — руками их накатывать не нужно.

3. Backend будет доступен на `http://localhost:8000`, автогенерируемая документация API — на `http://localhost:8000/docs`.

## Запуск frontend

Frontend поднимается отдельно от Docker (обычный `npm`):

```
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend будет на `http://localhost:5173`. Backend должен быть уже запущен — CORS настроен именно на этот адрес (`http://localhost:5173`), при другом порте запросы будут блокироваться браузером.

## Переменные окружения

| Файл | Переменная | Назначение |
|---|---|---|
| `.env` (корень) | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | доступ к БД |
| `.env` (корень) | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | подпись и срок жизни JWT-токена |
| `frontend/.env` | `VITE_API_URL` | адрес backend API для фронтенда |

## Регистрация и активация

Активации по email нет — ссылка активации выводится в лог backend-контейнера:

Linux/macOS:
```
docker compose logs backend | grep "Activation link"
```

Windows (PowerShell):
```
docker compose logs backend | Select-String "Activation link"
```

Скопируйте ссылку (или просто токен из неё) и откройте `http://localhost:8000/auth/activate/{token}` в браузере — либо через `/docs` (Swagger, `GET /auth/activate/{token}`, "Try it out").

## Тестовые учётки / доступ администратора

Эндпоинта для создания администратора нет — искусственно вводить "секретный" способ регистрации первого admin в реальной системе небезопасно. Первый администратор назначается напрямую в БД:

```
docker exec -it animal_weighing_system_db psql -U <POSTGRES_USER> -d <POSTGRES_DB> \
  -c "UPDATE users SET role='admin' WHERE login='ваш_логин';"
```

Пользователь должен быть уже зарегистрирован и активирован обычным способом. После смены роли нужно перелогиниться (роль читается из БД при каждом запросе, но токен лучше перевыпустить для чистоты).

## Тесты

```
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Тесты поднимают отдельный временный Postgres (пакет `pgserver`, embedded-бинарник, не требует прав root и не трогает БД из `docker compose`) и прогоняются на реальных constraints БД, а не на моках — покрыты самые важные с точки зрения бизнес-логики сценарии:

- полный флоу регистрации (неактивен → логин отклонён → активация → логин проходит);
- защита от каскадного удаления `breed`/`animaltype`, на которые ссылаются существующие записи (409, а не тихая порча данных);
- уникальность породы в рамках типа животного;
- уникальность взвешивания животного в рамках одной даты;
- доступ к чужой записи взвешивания — 404 для обычного пользователя, полный доступ для admin.

## Структура проекта

```
backend/
  app/
    api/        - роутеры FastAPI (auth, users, animals, catalog, weightings, admin)
    core/       - конфиг, безопасность (JWT, хеширование), зависимости (auth, RBAC)
    db/         - подключение к БД, CRUD-функции
    models.py   - модели SQLAlchemy
    schemas.py  - схемы Pydantic
  alembic/      - миграции БД
  tests/        - pytest
frontend/
  src/
    api/        - единая точка обращения к backend (fetch, обработка ошибок, JWT)
    components/ - переиспользуемые компоненты (таблица, поля форм, роут-guards)
    context/    - хранение JWT и данных пользователя (в памяти, не localStorage)
    pages/      - страницы приложения
```

## Роли и права

| Действие | user | admin |
|---|---|---|
| CRUD animaltype / breed / animal | да | да |
| CRUD weighting | только свои записи | все записи |
| Список пользователей | нет | да |
| Включение/отключение пользователя | нет | да |
