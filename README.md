# 🤖 Telegram bot for generating images

Hi! This bot can draw images from your description using Google’s neural network.

## What do you need to run it?

You’ll need two keys:
1. **A Telegram bot token**. You get it from [@BotFather](https://t.me/botfather) in Telegram.
2. **A Google API key**. You can get it at [Google AI Studio](https://aistudio.google.com/).

## 🚀 How to run the bot on your computer

### Step 1. Configuration

In the bot folder, create a file named `.env` (the leading dot is required) and put your keys in it like this:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token
GEMINI_API_KEY=your_google_key
# Bot mode: "group" (groups only), "private" (DMs only), or "both"
BOT_MODE=group
```

### Step 2. Start the program

Open a terminal (command prompt) in the bot folder and run these commands in order:

```cmd
# 1. Create a virtual environment (so nothing on your computer breaks)
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install the required libraries
pip install -r requirements.txt

# 4. Start the bot!
python main.py
```

🎉 **That’s it!** Open Telegram, send `/start` to your bot, and ask it to draw something, for example: "an orange cat flying into space".

### Bot modes (BOT_MODE)

In the `.env` file you can choose where the bot replies:
- `BOT_MODE=group` — the bot replies only in allowed groups/topics (you must mention it with `@BotName`). Direct messages are ignored.
- `BOT_MODE=private` — the bot replies only in direct messages (no mention required). Group messages are ignored.
- `BOT_MODE=both` — the bot replies in both direct messages and groups.

### How to stop the bot

If the bot is running in a terminal, press `Ctrl + C` (Windows/Linux) or `Cmd + C` (macOS).

If it was started in the background on Linux, you can stop it with:
```bash
pkill -f "python main.py"
```
