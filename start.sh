#!/bin/bash

echo "🚀 DRX POWER SYSTEM STARTING ON RAILWAY..."

# 1. Install libraries
echo "📦 Installing Python libraries..."
pip install flask telebot requests psutil --quiet

# 2. Compile C Binary
echo "⚙️ Compiling drx.c binary..."
gcc drx.c -o drx -lpthread -O3
chmod +x drx

# 3. Start Telegram Bot in the BACKGROUND
echo "🤖 Starting Telegram Bot in background..."
nohup python3 drx.py > bot_logs.txt 2>&1 &
sleep 2

# 4. Start Flask API in the FOREGROUND
# Railway requires the web server (Flask) to be in the foreground to monitor port 8080.
echo "🌐 Starting Flask API on port 8080..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SYSTEM IS NOW LIVE ON RAILWAY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 api.py
