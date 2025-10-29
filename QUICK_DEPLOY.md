# Быстрый деплой в Cloud Run (веб-интерфейс)

## 1️⃣ Запушьте код в GitHub
```bash
git add .
git commit -m "Switch to webhook mode"
git push origin main
```

## 2️⃣ Cloud Console → Cloud Run → CREATE SERVICE

**Выберите:**
- ✅ "Continuously deploy from source repository"
- ✅ SET UP WITH CLOUD BUILD
- ✅ GitHub → ваш репозиторий → branch: `main`
- ✅ Build Type: **Dockerfile**

**Настройки сервиса:**
- Service name: `telegram-imagen-bot`
- Region: `europe-west1`
- Min instances: `0` (автомасштабирование)
- Max instances: `3`
- Authentication: **Allow unauthenticated**

**Переменные окружения:**
```
TELEGRAM_BOT_TOKEN = ваш_токен
GEMINI_API_KEY = ваш_ключ
WEBHOOK_URL = (оставьте пустым сейчас)
```

**Нажмите CREATE** → подождите 3-5 минут

---

## 3️⃣ После деплоя

### A) Скопируйте Service URL
Например: `https://telegram-imagen-bot-xxxxx-ew.a.run.app`

### B) Обновите WEBHOOK_URL
- EDIT & DEPLOY NEW REVISION
- Variables: `WEBHOOK_URL = https://telegram-imagen-bot-xxxxx-ew.a.run.app`
- DEPLOY

### C) Установите webhook в Telegram
Откройте в браузере (замените на свои значения):
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_SERVICE_URL>/telegram
```

Должно вернуть: `{"ok":true,"result":true}`

---

## 4️⃣ Готово! 🎉

Проверьте: отправьте `/start` боту в Telegram.

**Подробная инструкция:** см. `DEPLOY_GUIDE.md`

