#!/bin/bash

# Advanced Telegram Video Encoder Bot - Start Script
# This script helps you easily start, stop, and manage the bot

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Bot configuration
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_NAME="encoder-bot"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/bot.log"

# Print colored message
print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Check if bot is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Start bot
start_bot() {
    if is_running; then
        print_message "$YELLOW" "⚠️  Bot is already running!"
        return
    fi

    print_message "$BLUE" "🚀 Starting $BOT_NAME..."

    # Check if virtual environment exists
    if [ ! -d "$BOT_DIR/venv" ]; then
        print_message "$YELLOW" "📦 Creating virtual environment..."
        python3 -m venv "$BOT_DIR/venv"
    fi

    # Activate virtual environment
    source "$BOT_DIR/venv/bin/activate"

    # Install/update dependencies
    print_message "$BLUE" "📥 Installing dependencies..."
    pip install -q -r "$BOT_DIR/requirements.txt"

    # Check FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        print_message "$RED" "❌ FFmpeg not found! Please install FFmpeg first."
        print_message "$YELLOW" "   Ubuntu/Debian: sudo apt install ffmpeg"
        print_message "$YELLOW" "   macOS: brew install ffmpeg"
        exit 1
    fi

    # Check .env file
    if [ ! -f "$BOT_DIR/.env" ]; then
        print_message "$RED" "❌ .env file not found!"
        print_message "$YELLOW" "   Copy .env.example to .env and configure it."
        exit 1
    fi

    # Create directories
    mkdir -p "$BOT_DIR/downloads"
    mkdir -p "$BOT_DIR/encodes"
    mkdir -p "$BOT_DIR/thumbnails"

    # Start bot in background
    nohup python3 "$BOT_DIR/bot.py" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    sleep 2

    if is_running; then
        print_message "$GREEN" "✅ Bot started successfully!"
        print_message "$BLUE" "   PID: $(cat $PID_FILE)"
        print_message "$BLUE" "   Logs: $LOG_FILE"
    else
        print_message "$RED" "❌ Failed to start bot!"
        print_message "$YELLOW" "   Check logs: tail -f $LOG_FILE"
    fi
}

# Stop bot
stop_bot() {
    if ! is_running; then
        print_message "$YELLOW" "⚠️  Bot is not running!"
        return
    fi

    print_message "$BLUE" "🛑 Stopping $BOT_NAME..."
    
    pid=$(cat "$PID_FILE")
    kill "$pid"
    
    # Wait for process to stop
    timeout=10
    while [ $timeout -gt 0 ] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        ((timeout--))
    done

    if ps -p "$pid" > /dev/null 2>&1; then
        print_message "$YELLOW" "⚠️  Force killing bot..."
        kill -9 "$pid"
    fi

    rm -f "$PID_FILE"
    print_message "$GREEN" "✅ Bot stopped!"
}

# Restart bot
restart_bot() {
    print_message "$BLUE" "🔄 Restarting $BOT_NAME..."
    stop_bot
    sleep 2
    start_bot
}

# Show bot status
status_bot() {
    if is_running; then
        pid=$(cat "$PID_FILE")
        uptime=$(ps -p "$pid" -o etime= | tr -d ' ')
        memory=$(ps -p "$pid" -o rss= | awk '{print $1/1024 " MB"}')
        cpu=$(ps -p "$pid" -o %cpu= | tr -d ' ')
        
        print_message "$GREEN" "✅ Bot is running"
        print_message "$BLUE" "   PID: $pid"
        print_message "$BLUE" "   Uptime: $uptime"
        print_message "$BLUE" "   CPU: ${cpu}%"
        print_message "$BLUE" "   Memory: $memory"
    else
        print_message "$RED" "❌ Bot is not running"
    fi
}

# View logs
view_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_message "$RED" "❌ Log file not found!"
        return
    fi

    print_message "$BLUE" "📋 Viewing logs (Ctrl+C to exit)..."
    tail -f "$LOG_FILE"
}

# Update bot
update_bot() {
    print_message "$BLUE" "📥 Updating $BOT_NAME..."

    # Check if git repo
    if [ ! -d "$BOT_DIR/.git" ]; then
        print_message "$RED" "❌ Not a git repository!"
        return
    fi

    # Stop bot if running
    was_running=false
    if is_running; then
        was_running=true
        stop_bot
    fi

    # Pull latest changes
    print_message "$BLUE" "🔄 Pulling latest changes..."
    cd "$BOT_DIR"
    git pull origin main

    # Update dependencies
    if [ -d "$BOT_DIR/venv" ]; then
        source "$BOT_DIR/venv/bin/activate"
        print_message "$BLUE" "📦 Updating dependencies..."
        pip install -q -r "$BOT_DIR/requirements.txt"
    fi

    # Restart if it was running
    if [ "$was_running" = true ]; then
        start_bot
    fi

    print_message "$GREEN" "✅ Bot updated successfully!"
}

# Clean temporary files
clean_bot() {
    print_message "$BLUE" "🧹 Cleaning temporary files..."

    # Remove encoded files
    rm -rf "$BOT_DIR/downloads/"*
    rm -rf "$BOT_DIR/encodes/"*

    # Calculate freed space
    print_message "$GREEN" "✅ Temporary files cleaned!"
}

# Show bot info
info_bot() {
    print_message "$BLUE" "ℹ️  Bot Information"
    echo ""
    print_message "$GREEN" "Directory: $BOT_DIR"
    print_message "$GREEN" "Python: $(python3 --version)"
    print_message "$GREEN" "FFmpeg: $(ffmpeg -version | head -n 1)"
    echo ""
    print_message "$BLUE" "📊 Storage Usage:"
    echo "   Downloads: $(du -sh $BOT_DIR/downloads 2>/dev/null | cut -f1)"
    echo "   Encodes: $(du -sh $BOT_DIR/encodes 2>/dev/null | cut -f1)"
    echo "   Thumbnails: $(du -sh $BOT_DIR/thumbnails 2>/dev/null | cut -f1)"
    echo "   Database: $(du -sh $BOT_DIR/bot.db 2>/dev/null | cut -f1)"
}

# Backup database
backup_bot() {
    print_message "$BLUE" "💾 Backing up database..."
    
    backup_dir="$BOT_DIR/backups"
    mkdir -p "$backup_dir"
    
    backup_file="$backup_dir/bot_backup_$(date +%Y%m%d_%H%M%S).db"
    
    if [ -f "$BOT_DIR/bot.db" ]; then
        cp "$BOT_DIR/bot.db" "$backup_file"
        print_message "$GREEN" "✅ Database backed up to: $backup_file"
    else
        print_message "$RED" "❌ Database file not found!"
    fi
}

# Show help
show_help() {
    echo ""
    print_message "$BLUE" "🎬 Advanced Telegram Video Encoder Bot"
    echo ""
    print_message "$GREEN" "Usage: ./start.sh [command]"
    echo ""
    print_message "$YELLOW" "Commands:"
    echo "   start      - Start the bot"
    echo "   stop       - Stop the bot"
    echo "   restart    - Restart the bot"
    echo "   status     - Show bot status"
    echo "   logs       - View bot logs"
    echo "   update     - Update bot from git"
    echo "   clean      - Clean temporary files"
    echo "   info       - Show bot information"
    echo "   backup     - Backup database"
    echo "   help       - Show this help message"
    echo ""
}

# Main script
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        view_logs
        ;;
    update)
        update_bot
        ;;
    clean)
        clean_bot
        ;;
    info)
        info_bot
        ;;
    backup)
        backup_bot
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
