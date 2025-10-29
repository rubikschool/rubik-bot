#!/bin/bash

# Script to setup Telegram webhook for Cloud Run deployment

echo "🤖 Telegram Webhook Setup Script"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Load environment variables from .env
export $(cat .env | grep -v '^#' | xargs)

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not found in .env file"
    exit 1
fi

# Prompt for Cloud Run service URL
echo "Enter your Cloud Run Service URL (without /telegram at the end):"
echo "Example: https://telegram-imagen-bot-xxxxx-ew.a.run.app"
read -r SERVICE_URL

# Remove trailing slash if present
SERVICE_URL=${SERVICE_URL%/}

echo ""
echo "Setting webhook to: ${SERVICE_URL}/telegram"
echo ""

# Set webhook
RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${SERVICE_URL}/telegram")

echo "Response: $RESPONSE"
echo ""

# Check if successful
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook set successfully!"
    echo ""
    echo "Checking webhook info..."
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
else
    echo "❌ Failed to set webhook"
    echo "Please check your bot token and service URL"
fi

echo ""
echo "Don't forget to add WEBHOOK_URL=${SERVICE_URL} to your Cloud Run environment variables!"

