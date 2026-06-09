
## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/loknxq/aquarium_monitor.git
cd aquarium_monitor
```

### 2. Создание и активация виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных PostgreSQL

Создайте базу данных и пользователя:

```sql
CREATE DATABASE aquarium_db;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aquarium_db TO your_user;
```

### 5. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/aquarium_db
SECRET_KEY=your_secret_key_min_32_characters
```

### 6. Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: **http://localhost:8000**

### 7. Документация API

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**
```