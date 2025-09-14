# Telegram Image Generation Bot

A Telegram bot that generates images using Google's Gemini 2.5 Flash model. Send any text prompt and get AI-generated images in return.

## Features

- 🤖 Telegram bot integration with python-telegram-bot
- 🎨 Image generation using Google Gemini 2.5 Flash Image Preview
- 🐳 Docker support for easy deployment
- 📝 Environment-based configuration
- 🔧 Error handling and logging

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google AI API Key (from [Google AI Studio](https://aistudio.google.com/))

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd imagen
```

### 2. Configure Environment

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_API_KEY=your_google_api_key_here
BOT_USERNAME=your_bot_username
```

### 3. Run Locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

### 4. Run with Docker

```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Or build and run manually
docker build -t telegram-bot .
docker run --env-file .env telegram-bot
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send any text prompt (e.g., "a sunset over mountains")
4. Receive an AI-generated image based on your prompt

## Project Structure

```
.
├── main.py              # Main bot implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image configuration
├── docker-compose.yml  # Docker Compose setup
├── .dockerignore       # Docker ignore file
├── .env                # Environment variables (create this)
└── README.md           # This file
```

## Dependencies

- **python-telegram-bot**: Telegram Bot API wrapper
- **google-generativeai**: Google Gemini AI client
- **python-dotenv**: Environment variable management
- **pillow**: Image processing utilities
- **aiofiles**: Async file operations

## Configuration

The bot uses environment variables for configuration:

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from BotFather | Yes |
| `GOOGLE_API_KEY` | Your Google AI API key | Yes |
| `BOT_USERNAME` | Your bot's username (optional) | No |

## How It Works

1. Bot receives text messages from users
2. Sends the text as a prompt to Google's Gemini 2.5 Flash Image Preview model
3. Extracts the generated image from the API response
4. Sends the image back to the user via Telegram

## Error Handling

The bot includes comprehensive error handling:
- API failures are logged and reported to users
- Network issues are handled gracefully
- Invalid responses are caught and reported

## Deployment

### Local Development
Use the virtual environment setup for local development and testing.

### Production Deployment
Use Docker Compose for production deployment:

```bash
# Production deployment
docker-compose up -d --build
```

## Troubleshooting

**Bot not responding:**
- Check your `TELEGRAM_BOT_TOKEN` is correct
- Verify the bot is running without errors in logs

**Images not generating:**
- Verify your `GOOGLE_API_KEY` is valid and has quota
- Check Google AI Studio for API limits and usage

**Docker issues:**
- Ensure `.env` file exists and contains required variables
- Check Docker logs: `docker-compose logs`

## License

MIT License - feel free to use and modify as needed.
