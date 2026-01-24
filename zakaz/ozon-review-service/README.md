# 📋 Ozon Review Service - Полная документация

## 🎯 О проекте
Автоматизированная система управления отзывами на Ozon marketplace с AI-генерацией ответов через OpenAI.

---

## 📁 Структура проекта

```
ozon-review-service/
├── main.py                          # 🚀 Точка входа FastAPI приложения
├── run_with_ngrok.py               # 🌐 Запуск с публичной HTTPS ссылкой (для демо)
├── load_test_data.py               # 🧪 Загрузка тестовых отзывов в БД
├── verify_api.py                   # ✅ Проверка подключения к OpenAI
├── verify_system.ps1               # 🔧 PowerShell скрипт проверки системы
├── verify_system.sh                # 🔧 Bash скрипт проверки системы
├── requirements.txt                # 📦 Python зависимости
├── setup.bat                       # 🪟 Windows setup скрипт
├── setup.sh                        # 🐧 Unix/Linux setup скрипт
├── docker-compose.yml              # 🐳 Docker конфигурация
├── Dockerfile                      # 🐳 Docker образ
├── .env                            # ⚙️ Переменные окружения (не коммитить!)
│
├── app/
│   ├── __init__.py
│   ├── config.py                   # ⚙️ Настройки приложения (из .env)
│   ├── database.py                 # 🗄️ SQLAlchemy подключение и сессии
│   ├── background_tasks.py         # 🔄 Фоновые задачи (опрос отзывов каждые N минут)
│   │
│   ├── models/                     # 📊 SQLAlchemy модели БД
│   │   ├── review.py              # Review - отзыв клиента
│   │   ├── response.py            # Response - отправленный ответ на Ozon
│   │   ├── settings.py            # Settings - ключ-значение конфиг (obsolete)
│   │
│   ├── schemas/                   # 📄 Pydantic валидация запросов/ответов
│   │   ├── review.py              # ReviewSchema
│   │   ├── response.py            # ResponseSchema, ResponseDraftSchema
│   │   ├── settings.py            # SettingsSchema
│   │
│   ├── services/                  # 🔧 Бизнес-логика
│   │   ├── ozon_service.py        # 🛒 Ozon API (получить отзывы, отправить ответ)
│   │   ├── review_service.py      # 📝 Обработка отзывов (сохранить, пометить ответ)
│   │   ├── ai_service.py          # 🤖 Анализ тональности отзыва (obsolete - используем AutoResponseService)
│   │   ├── auto_response_service.py # ⚡ Генерация ответов через OpenAI (основной)
│   │
│   ├── api/                       # 🌐 REST API эндпоинты
│   │   └── routes/
│   │       ├── reviews.py         # GET/POST отзывы, синк с Ozon
│   │       ├── responses.py       # POST отправить ответ, GET историю
│   │       ├── settings.py        # GET/POST ключи, конфиг, тестирование AI
│   │       ├── integrations.py    # Health check интеграций
│   │
│   └── migrations/                # Alembic миграции (если используется)
│
└── frontend/
    └── index.html                 # 💻 SPA - весь фронт в одном файле (1900+ строк)
        ├── HTML (0-680)           # Разметка: карточки, модали, настройки
        ├── CSS (680-1250)         # Стили: фильтры, кнопки, модали
        └── JavaScript (1250-1900+)  # Логика: загрузка отзывов, отправка ответов, API

ozon_reviews.db                    # 🗄️ SQLite БД (создаётся автоматически)
```

---

## 🔑 Ключевые файлы и их функции

### Backend - Python

#### `main.py` - Главный файл приложения
- Создание FastAPI приложения
- CORS middleware
- Подключение всех route'ов (reviews, responses, settings, integrations)
- Старт/стоп фоновых задач (polling reviews)
- Точка входа для Uvicorn: `uvicorn.run("main:app")`

#### `app/config.py` - Конфигурация
Читает из `.env` файла переменные:
- `OZON_CLIENT_ID`, `OZON_API_KEY` - для подключения к Ozon API
- `OPENAI_API_KEY`, `OPENAI_MODEL` - для OpenAI
- `RESPONSE_TONE` - тон ответов (friendly/official/formal)
- `RESPONSE_SIGNATURE` - подпись в конце ответа
- `POLLING_INTERVAL_MINUTES` - как часто опрашивать новые отзывы
- `AUTO_RESPONSE_ENABLED` - автогенерировать ответ при новом отзыве

#### `app/database.py` - БД подключение
- SQLAlchemy engine и Session factory
- Использует SQLite: `sqlite:///./ozon_reviews.db`

#### `app/background_tasks.py` - Фоновые задачи
- `ReviewPoller` - класс для периодического опроса Ozon
- `poll_reviews()` - fetch новых отзывов каждые N минут
- `reschedule()` - изменить интервал опроса при изменении настроек
- APScheduler - управление расписанием

#### `app/services/ozon_service.py` - Интеграция с Ozon
```python
# Основные методы:
get_reviews(limit=100, offset=0)  # Получить список отзывов
send_response(review_id, text)     # Отправить ответ на отзыв
validate_credentials()              # Проверить наличие ключей
```

#### `app/services/review_service.py` - Бизнес-логика отзывов
```python
# Основные методы:
process_new_review(review_data)    # Обработать новый отзыв, сохранить в БД
generate_response_drafts()          # Создать варианты ответов
submit_response(review_id, text)    # Отправить ответ на Ozon + пометить answered=True
```

#### `app/services/auto_response_service.py` - AI генерация ответов
```python
generate_response(review_text)      # Генерация ответа через OpenAI или fallback
# Поддерживает 3 режима:
# - AI (OpenAI API) - если есть ключ и баланс
# - Fallback - встроенные шаблоны ответов по тональности
# - Sentiment detection - определение позитива/негатива в отзыве
```

#### `app/models/review.py` - ORM модель отзыва
```python
class Review:
    id                  # ID в нашей БД
    ozon_review_id      # ID на маркетплейсе (уникальный)
    product_id          # SKU товара
    customer_name       # Имя покупателя
    rating              # Оценка (1-5)
    text                # Текст отзыва
    sentiment           # Тональность (positive/neutral/negative)
    answered            # Ответили ли (True/False)
    created_at          # Когда пришёл отзыв
```

#### `app/models/response.py` - ORM модель ответа
```python
class Response:
    id                  # ID в БД
    review_id           # На какой отзыв ответили
    text                # Текст ответа
    status              # sent/draft/failed
    ozon_response_id    # ID ответа на маркетплейсе (если успешно)
    created_at          # Когда отправили
```

#### `app/api/routes/reviews.py` - REST API отзывов
```
GET  /api/reviews                    # Список отзывов (с фильтрацией по answered)
GET  /api/reviews/stats              # Статистика
GET  /api/reviews/products           # Товары и их статистика
POST /api/reviews/sync               # Синхронизировать с Ozon
```

#### `app/api/routes/responses.py` - REST API ответов
```
GET  /api/responses/drafts/{review_id}  # Варианты ответов для отзыва
POST /api/responses                     # Отправить ответ на Ozon
GET  /api/responses/history/recent      # История отправленных ответов
```

#### `app/api/routes/settings.py` - REST API настроек
```
GET  /api/settings/ozon/credentials           # Получить Ozon ключи
POST /api/settings/ozon/credentials           # Сохранить Ozon ключи (в .env)
GET  /api/settings/openai/credentials         # Получить OpenAI ключ
POST /api/settings/openai/credentials         # Сохранить OpenAI ключ (в .env)
POST /api/settings/openai/check-key           # Проверить валидность ключа
GET  /api/settings/auto-response/config       # Получить конфиг автоответов
POST /api/settings/auto-response/config       # Сохранить конфиг
POST /api/settings/auto-response/test         # Тестировать генерацию ответа
```

### Frontend - HTML/CSS/JavaScript

#### `frontend/index.html` - Основное приложение
**HTML (строки 0-680):**
- Структура страницы
- Разделы: Товары, Отзывы, История ответов
- Модали: Настройки, Ответить на отзыв
- Фильтры: по тональности, по статусу ответа (Все/Позитив/Негатив/Без ответов/С ответами)

**CSS (строки 680-1250):**
- `.card` - карточка блока
- `.filter-btn` - кнопка фильтра
- `.modal` - модальное окно
- `.review-item` - карточка отзыва
- Классы для статусов и тональности

**JavaScript (строки 1250-1900+):**

Основные функции:

1. **Загрузка отзывов:**
```javascript
loadReviews()              // GET /api/reviews
filterReviews(filter)      // Фильтровать по тональности/статусу
filterSort(sort)           // Сортировать (новые/старые)
```

2. **Отправка ответа:**
```javascript
openResponseModal()        // Открыть модаль с формой ответа
submitResponse()           // POST /api/responses - отправить на Ozon
```

3. **AI генерация:**
```javascript
attachResponseButtonHandlers()  // Вешать события на кнопки "Ответить"
generateAIResponse()            // POST /api/settings/auto-response/test - генерировать ответ
```

4. **Настройки:**
```javascript
loadSettings()             // Загрузить текущие значения
saveSettings(type)         // Сохранить (ozon/openai/response)
checkAIHealth()            // Проверить статус API
```

5. **Утилиты:**
```javascript
escapeHtml()               // Защита от XSS
showNotification()         // Показать уведомление (toast)
```

---

## 🚀 Запуск приложения

### Вариант 1: Локально на машине
```bash
cd d:\KWork\zakaz\ozon-review-service
python main.py
# Доступно по http://localhost:8000
```

### Вариант 2: С ngrok (публичная ссылка для демо)
```bash
python run_with_ngrok.py
# Выведет: https://xxxxx.ngrok-free.app
# Ссылка живёт 2 часа, потом нужен рестарт
```

### Вариант 3: Docker
```bash
docker-compose up
# Доступно по http://localhost:8000
```

---

## ⚙️ Переменные окружения (.env)

```env
# Ozon Marketplace
OZON_CLIENT_ID=417663
OZON_API_KEY=xxxxxxx

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxx
OPENAI_MODEL=gpt-3.5-turbo  # или gpt-4, gpt-4-turbo

# Ответы на отзывы
RESPONSE_TONE=friendly      # friendly, official, formal
RESPONSE_SIGNATURE=С уважением,\nКоманда маркетплейса
RESPONSE_PROMPT=            # Пустой = использовать стандартный

# Автоматизация
POLLING_INTERVAL_MINUTES=30 # Каждые 30 минут проверять новые отзывы
AUTO_RESPONSE_ENABLED=false # Создавать черновик при новом отзыве
```

---

## 🔄 Процесс работы

### 1. Получение отзывов (каждые N минут)
```
ReviewPoller.poll_reviews()
  → OzonService.get_reviews()
  → ReviewService.process_new_review()
    → Проверить: answered ли отзыв на маркетплейсе?
    → Если НЕ answered:
      → Сохранить в БД
      → Если AUTO_RESPONSE_ENABLED: генерировать черновик через AI
      → Создать варианты ответов (draft'ы)
```

### 2. Отправка ответа (нажал кнопка в интерфейсе)
```
Frontend: submitResponse()
  → POST /api/responses {review_id, text}
  → ReviewService.submit_response()
    → Проверить: не answered ли уже?
    → OzonService.send_response(ozon_review_id, text)
    → Если успех: пометить review.answered = True
    → Записать в Response таблицу (статус: sent)
```

### 3. Генерация ответа AI (кнопка в модали)
```
Frontend: generateAIResponse()
  → POST /api/settings/auto-response/test {review_text}
  → AutoResponseService.generate_response()
    → Попробовать OpenAI API
    → Если fail: использовать fallback (встроенные шаблоны)
    → Вернуть текст ответа
  → Подставить в textarea в модали
```

---

## 📊 БД структура (SQLite)

### Таблица `reviews`
```
id, ozon_review_id, product_id, product_name, customer_name, 
rating, text, sentiment, category, answered, created_at, fetched_at
```

### Таблица `responses`
```
id, review_id (FK), draft_id, text, status, ozon_response_id, 
error_message, created_at
```

### Таблица `response_drafts`
```
id, review_id (FK), text, variant_number, created_at
```

### Таблица `settings` (для расширения, сейчас не используется)
```
key, value, updated_at
```

---

## 🧪 Тестирование

### Загрузить тестовые отзывы
```bash
python load_test_data.py
# Создаст 100 фиктивных отзывов в БД
```

### Проверить OpenAI ключ
```bash
python verify_api.py
# Проверит, работает ли API и баланс
```

---

## 🐛 Troubleshooting

### Ошибка: "python-dotenv could not parse statement"
Проблема в `.env` файле - там неправильный синтаксис. Игнорируется, не влияет на работу.

### Ошибка: "ozon_service: validate_credentials failed"
Нет ключей Ozon в `.env`. Укажи в интерфейсе Настройки → Ozon.

### Ошибка: "OpenAI API Error"
- Проверь ключ (Settings → OpenAI)
- Проверь баланс (https://platform.openai.com/account/billing)
- AI отключится, но ответы в fallback режиме всё ещё работают

### Ошибка: "ngrok: tunnel failed"
Нужно скачать ngrok или установить: `pip install pyngrok`

---

## 📝 Что сделано

✅ Интеграция с Ozon API (получение отзывов)  
✅ Интеграция с OpenAI API (AI генерация ответов)  
✅ Автоматический опрос отзывов по расписанию  
✅ Отправка ответов обратно на маркетплейс  
✅ Простой web-интерфейс (SPA)  
✅ Фильтрация отзывов (тональность, статус ответа)  
✅ Автопроверка: уже ли ответили на маркетплейсе (избегаем дублей)  
✅ Настраиваемый интервал опроса  
✅ Публичная ссылка через ngrok для демо  
✅ Fallback режим при недоступности OpenAI  

---

## 👨‍💼 Для заказчика

Просто откройте в браузере: **http://localhost:8000** или ngrok ссылку

**Функции:**
1. Настроить ключи (Ozon + OpenAI)
2. Видеть список отзывов с фильтрацией
3. Нажать "Ответить" → выбрать вариант (вручную или AI генерация)
4. Ответ отправляется на маркетплейс автоматически
5. История всех отправленных ответов

---

**Версия:** 1.0  
**Дата:** January 2026  
**Статус:** Production-ready
