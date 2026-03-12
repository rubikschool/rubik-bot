# Инструкция по деплою бота в Google Cloud Run

Бот переделан на **webhook** режим для оптимальной работы в Cloud Run.

## Преимущества webhook:
- ✅ Платите только за обработку сообщений (не за простой)
- ✅ Автоматическое масштабирование (до 0 инстансов когда нет трафика)
- ✅ Мгновенная доставка сообщений
- ✅ Меньше нагрузка на Telegram API

---

## Шаг 1: Деплой через GitHub (веб-интерфейс)

### 1.1 Запушьте изменения в GitHub

```bash
git add .
git commit -m "Switch to webhook mode for Cloud Run"
git push origin main
```

### 1.2 Откройте Google Cloud Console

1. Перейдите на https://console.cloud.google.com/
2. Выберите ваш проект или создайте новый

### 1.3 Перейдите в Cloud Run

- В поиске наверху введите "Cloud Run"
- Или через меню ☰ → Cloud Run

### 1.4 Создайте новый сервис

1. Нажмите **"CREATE SERVICE"**
2. Выберите **"Continuously deploy from a source repository (source-based)"**
3. Нажмите **"SET UP WITH CLOUD BUILD"**

### 1.5 Подключите GitHub репозиторий

1. **Repository Provider**: выберите "GitHub"
2. Нажмите **"AUTHENTICATE"** (авторизуйте GitHub если нужно)
3. Выберите ваш репозиторий `rubikschool/imagen`
4. **Branch**: `main`
5. **Build Type**: выберите **"Dockerfile"**
6. **Dockerfile path**: `/Dockerfile`
7. Нажмите **"SAVE"**

### 1.6 Настройте сервис

**Основные настройки:**
- **Service name**: `telegram-imagen-bot` (или любое другое имя)
- **Region**: `europe-west1` (или ближайший регион)

**CPU allocation:**
- ⚠️ **ВАЖНО**: Оставьте **"CPU is only allocated during request processing"** (по умолчанию)
- Это позволит экономить деньги (масштабирование до 0)

**Autoscaling:**
- **Minimum instances**: `0` (бот будет останавливаться когда нет сообщений)
- **Maximum instances**: `3` (можно больше если нужно)

**Container settings:**
- **Container port**: `8080`
- **Memory**: `512 MiB` (можно больше если нужны сложные изображения)
- **CPU**: `1`

### 1.7 Настройте переменные окружения

1. Раскройте **"Container, Variables & Secrets, Connections, Security"**
2. Перейдите на вкладку **"Variables & Secrets"**
3. Нажмите **"ADD VARIABLE"** для каждой переменной:

**Обязательные переменные:**
- Name: `TELEGRAM_BOT_TOKEN`
  - Value: `ваш_токен_от_BotFather`
- Name: `GEMINI_API_KEY`
  - Value: `ваш_ключ_от_Google_AI_Studio`

### 1.8 Настройте доступ

- **Authentication**: выберите **"Allow unauthenticated invocations"**
  - Это нужно чтобы Telegram мог отправлять webhook запросы

### 1.9 Создайте сервис

1. Нажмите **"CREATE"**
2. Подождите 3-5 минут пока Cloud Build соберет и задеплоит образ
3. Дождитесь статуса ✅ (зеленая галочка)

---

## Шаг 2: Настройка Webhook в Telegram

### 2.1 Получите URL вашего сервиса

После успешного деплоя:
1. Откройте ваш сервис в Cloud Run
2. Скопируйте **Service URL** (например: `https://telegram-imagen-bot-xxxxx-ew.a.run.app`)

### 2.2 Зарегистрируйте webhook в Telegram

Откройте браузер и перейдите по URL (замените на свои значения):

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_SERVICE_URL>/telegram
```

**Пример:**
```
https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/setWebhook?url=https://telegram-imagen-bot-xxxxx-ew.a.run.app/telegram
```

Вы должны увидеть:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### 2.4 Проверьте webhook

Откройте в браузере:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Должно показать ваш URL и `pending_update_count: 0`

---

## Шаг 3: Проверка работы

1. Откройте Telegram
2. Найдите ваш бот
3. Отправьте команду `/start`
4. Напишите сообщение с упоминанием бота в разрешенной теме
5. Бот должен ответить и сгенерировать изображение

---

## Мониторинг и логи

### Просмотр логов:
1. Откройте ваш сервис в Cloud Run
2. Перейдите на вкладку **"LOGS"**
3. Здесь можно увидеть все запросы и ошибки

### Метрики:
1. Вкладка **"METRICS"**
2. Показывает количество запросов, латентность, использование CPU/памяти

---

## Стоимость

При использовании webhook:
- **Первые 2 млн запросов в месяц** — БЕСПЛАТНО
- **CPU/Memory** — оплата только за время обработки запросов
- **Масштабирование до 0** — не платите когда бот не используется

Примерная стоимость для небольшого бота: **$0-5 в месяц**

---

## Устранение проблем

### Webhook не работает:
1. Проверьте логи в Cloud Run — там будет ошибка если URL не определился
2. Убедитесь что сервисный аккаунт имеет роль `roles/run.viewer`
3. Проверьте webhook info: `/getWebhookInfo`
4. Удалите webhook и установите заново: `/deleteWebhook` → `/setWebhook`

### Бот не отвечает:
1. Проверьте что сообщение в разрешенной теме (см. `groups_config.json`)
2. Проверьте что бот упомянут: `@your_bot_name промпт`
3. Проверьте логи на ошибки

### Ошибки генерации изображений:
1. Проверьте что `GEMINI_API_KEY` правильный
2. Проверьте квоты Google AI Studio
3. Проверьте логи на детали ошибки

---

## Обновление бота

Для обновления кода:
1. Внесите изменения в код
2. Запушьте в GitHub: `git push origin main`
3. Cloud Run автоматически пересоберет и задеплоит новую версию
4. Webhook останется настроенным

---

## Дополнительные команды (опционально)

### Удалить webhook (вернуться к polling):
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook
```

### Проверить статус бота:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
```

---

## Готово! 🎉

Ваш бот теперь работает в Cloud Run с webhook режимом.

