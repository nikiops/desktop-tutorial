# 🚀 Инструкция по развертыванию на сервер

## Информация о сервере
- **IP:** 147.45.185.92
- **Домен:** review-assistant.ru
- **ОС:** Linux (Debian/Ubuntu)
- **Доступ:** root

## Шаг 1: Подключитесь к серверу

```bash
ssh root@147.45.185.92
# Пароль: v-ux?,,4FMyXAE
```

## Шаг 2: Скачайте скрипт развертывания

```bash
# Вариант 1: Через curl
curl -O https://raw.githubusercontent.com/Henta1ka/OzonRevui/main/ozon-review-service/deploy.sh
chmod +x deploy.sh

# Вариант 2: Вручную
git clone https://github.com/Henta1ka/OzonRevui.git
cd OzonRevui/ozon-review-service
chmod +x deploy.sh
```

## Шаг 3: Запустите скрипт развертывания

```bash
sudo ./deploy.sh
```

⏱️ Процесс займет 3-5 минут. Скрипт автоматически:
- ✅ Обновит систему
- ✅ Установит Python 3.9, Nginx, Certbot
- ✅ Клонирует/обновит репозиторий
- ✅ Создаст виртуальное окружение Python
- ✅ Установит зависимости
- ✅ Создаст `.env` файл
- ✅ Настроит Nginx как обратный прокси
- ✅ Установит SSL сертификат (Let's Encrypt)
- ✅ Запустит сервис через systemd

## Шаг 4: Отредактируй `.env` файл

После запуска скрипта отредактируй конфиг с реальными ключами:

```bash
nano /opt/OzonRevui/ozon-review-service/.env
```

Заполни эти переменные:
```env
# Ozon API (получи на https://seller.ozone.ru)
OZON_CLIENT_ID=12345  # Твой Client-ID
OZON_API_KEY=xxxx...  # Твой API Key

# OpenAI (получи на https://platform.openai.com)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# YandexGPT (опционально)
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...
YANDEX_MODEL=yandexgpt-3

# Остальное по необходимости
```

Сохрани: `Ctrl+O` → Enter → `Ctrl+X`

## Шаг 5: Перезапустись сервис

```bash
sudo systemctl restart ozon-service
```

## Шаг 6: Проверь статус

```bash
# Статус сервиса
sudo systemctl status ozon-service

# Логи в реальном времени
sudo journalctl -u ozon-service -f

# Проверь Nginx
curl http://localhost:8000/health
```

## Шаг 7: Открой приложение

```
🌐 https://review-assistant.ru
📊 API: https://review-assistant.ru/api
📚 Docs: https://review-assistant.ru/docs
```

---

## 📋 Полезные команды

### Управление сервисом
```bash
# Статус
sudo systemctl status ozon-service

# Логи
sudo journalctl -u ozon-service -f

# Перезапуск
sudo systemctl restart ozon-service

# Остановка
sudo systemctl stop ozon-service

# Запуск
sudo systemctl start ozon-service
```

### Обновление кода
```bash
cd /opt/OzonRevui/ozon-review-service
git pull origin main
pip install -r requirements.txt
sudo systemctl restart ozon-service
```

### Просмотр и редактирование конфига
```bash
nano /opt/OzonRevui/ozon-review-service/.env
sudo systemctl restart ozon-service  # перезагрузи после изменений
```

### SSL сертификат
```bash
# Проверить статус
sudo certbot certificates

# Продлить (cron сам делает каждый день)
sudo certbot renew --dry-run

# Пересоздать
sudo certbot certonly --nginx -d review-assistant.ru
```

---

## 🔍 Если что-то не работает

### Ошибка подключения
```bash
# Проверь Nginx
sudo systemctl status nginx
sudo nginx -t  # проверь конфиг

# Проверь Python сервис
sudo systemctl status ozon-service
sudo journalctl -u ozon-service -n 50  # последние 50 строк
```

### Приложение не стартует
```bash
# Проверь логи
sudo journalctl -u ozon-service -f

# Проверь .env файл
cat /opt/OzonRevui/ozon-review-service/.env

# Запусти вручную для диагностики
cd /opt/OzonRevui/ozon-review-service
source venv/bin/activate
python main.py  # или uvicorn main:app
```

### SSL проблемы
```bash
# Переоформи сертификат
sudo certbot remove --cert-name review-assistant.ru
sudo certbot certonly --nginx -d review-assistant.ru
```

---

## 📊 Архитектура

```
┌─────────────────────────────────────────┐
│          Клиент (браузер)               │
│     https://review-assistant.ru         │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS (443)
               ▼
┌─────────────────────────────────────────┐
│    Nginx (обратный прокси)              │
│    ├─ Кэшировать статику               │
│    ├─ SSL сертификаты                  │
│    └─ Маршрутизация на 8000            │
└──────────────┬──────────────────────────┘
               │
               │ HTTP (8000)
               ▼
┌─────────────────────────────────────────┐
│     FastAPI (uvicorn server)            │
│    ├─ GET  /api/reviews                 │
│    ├─ POST /api/reviews/sync            │
│    ├─ POST /api/responses/send          │
│    ├─ GET/POST /api/settings/*          │
│    └─ WebUI с фронтенд-ом              │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┬─────────────────┐
       │               │                 │
       ▼               ▼                 ▼
  SQLite DB      Ozon API          OpenAI API
  (локально)     (маркетплейс)     (НейроСеть)
                                    YandexGPT
```

---

## ✅ Чек-лист первого запуска

- [ ] SSH доступ к серверу работает
- [ ] Скрипт deploy.sh запущен успешно
- [ ] .env файл отредактирован с реальными ключами
- [ ] Статус сервиса: `active (running)`
- [ ] https://review-assistant.ru открывается
- [ ] Нет ошибок в логах (`journalctl`)
- [ ] API docs доступны: https://review-assistant.ru/docs
- [ ] Настроены ключи Ozon API
- [ ] Настроены ключи OpenAI или YandexGPT
- [ ] Первое лицензированию работает (загруженный отзыв анализируется)

---

## 🆘 Техподдержка

Если есть вопросы:
1. Проверь логи: `sudo journalctl -u ozon-service -f`
2. Проверь конфиг: `cat /opt/OzonRevui/ozon-review-service/.env`
3. Проверь git: `cd /opt/OzonRevui && git status`
4. Отправь логи и конфиг (без ключей) в поддержку

---

**Сервис готов к работе! 🎉**
