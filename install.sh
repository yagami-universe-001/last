#!/bin/bash

# Advanced Telegram Video Encoder Bot - Installation Script
# This script automates the installation process

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

# Print banner
print_banner() {
    clear
    print_msg "╔════════════════════════════════════════════════════════╗" "$PURPLE"
    print_msg "║                                                        ║" "$PURPLE"
    print_msg "║     🎬 ADVANCED TELEGRAM VIDEO ENCODER BOT 🎬          ║" "$BLUE"
    print_msg "║                                                        ║" "$PURPLE"
    print_msg "║        Fast | Reliable | Feature-Rich                 ║" "$GREEN"
    print_msg "║                                                        ║" "$PURPLE"
    print_msg "╚════════════════════════════════════════════════════════╝" "$PURPLE"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install package
install_package() {
    package=$1
    print_msg "📦 Installing $package..." "$BLUE"
    
    if command_exists apt-get; then
        sudo apt-get install -y "$package" >/dev/null 2>&1
    elif command_exists yum; then
        sudo yum install -y "$package" >/dev/null 2>&1
    elif command_exists brew; then
        brew install "$package" >/dev/null 2>&1
    else
        print_msg "❌ Unable to install $package. Please install manually." "$RED"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        print_msg "✅ $package installed successfully!" "$GREEN"
        return 0
    else
        print_msg "❌ Failed to install $package" "$RED"
        return 1
    fi
}

# Main installation
main() {
    print_banner
    
    print_msg "🚀 Starting installation process..." "$BLUE"
    echo ""
    
    # Check Python
    print_msg "🔍 Checking Python installation..." "$YELLOW"
    if command_exists python3; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_msg "✅ Python $python_version found!" "$GREEN"
    else
        print_msg "❌ Python 3 not found!" "$RED"
        print_msg "   Installing Python 3..." "$YELLOW"
        install_package python3
    fi
    
    # Check pip
    print_msg "🔍 Checking pip installation..." "$YELLOW"
    if command_exists pip3; then
        print_msg "✅ pip3 found!" "$GREEN"
    else
        print_msg "   Installing pip3..." "$YELLOW"
        install_package python3-pip
    fi
    
    # Check git
    print_msg "🔍 Checking git installation..." "$YELLOW"
    if command_exists git; then
        print_msg "✅ git found!" "$GREEN"
    else
        print_msg "   Installing git..." "$YELLOW"
        install_package git
    fi
    
    # Check FFmpeg
    print_msg "🔍 Checking FFmpeg installation..." "$YELLOW"
    if command_exists ffmpeg; then
        ffmpeg_version=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
        print_msg "✅ FFmpeg $ffmpeg_version found!" "$GREEN"
    else
        print_msg "   Installing FFmpeg..." "$YELLOW"
        install_package ffmpeg
    fi
    
    echo ""
    print_msg "📥 Setting up project..." "$BLUE"
    
    # Create virtual environment
    print_msg "🐍 Creating virtual environment..." "$YELLOW"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        print_msg "✅ Virtual environment created!" "$GREEN"
    else
        print_msg "❌ Failed to create virtual environment!" "$RED"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_msg "⬆️  Upgrading pip..." "$YELLOW"
    pip install --upgrade pip >/dev/null 2>&1
    
    # Install requirements
    print_msg "📦 Installing Python dependencies..." "$YELLOW"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_msg "✅ Dependencies installed!" "$GREEN"
    else
        print_msg "❌ Failed to install dependencies!" "$RED"
        exit 1
    fi
    
    # Create directories
    print_msg "📁 Creating directories..." "$YELLOW"
    mkdir -p downloads encodes thumbnails backups
    touch downloads/.gitkeep encodes/.gitkeep thumbnails/.gitkeep
    print_msg "✅ Directories created!" "$GREEN"
    
    # Create .env file if not exists
    if [ ! -f .env ]; then
        print_msg "⚙️  Creating .env file..." "$YELLOW"
        cp .env.example .env
        print_msg "✅ .env file created!" "$GREEN"
        print_msg "⚠️  Please edit .env and add your credentials!" "$YELLOW"
    else
        print_msg "✅ .env file already exists!" "$GREEN"
    fi
    
    # Make scripts executable
    print_msg "🔧 Making scripts executable..." "$YELLOW"
    chmod +x start.sh
    print_msg "✅ Scripts are now executable!" "$GREEN"
    
    echo ""
    print_msg "╔════════════════════════════════════════════════════════╗" "$GREEN"
    print_msg "║                                                        ║" "$GREEN"
    print_msg "║     ✅ INSTALLATION COMPLETED SUCCESSFULLY! ✅          ║" "$GREEN"
    print_msg "║                                                        ║" "$GREEN"
    print_msg "╚════════════════════════════════════════════════════════╝" "$GREEN"
    echo ""
    
    print_msg "📝 Next Steps:" "$BLUE"
    echo ""
    print_msg "1. Edit .env file with your credentials:" "$YELLOW"
    print_msg "   nano .env" "$NC"
    echo ""
    print_msg "2. Add your Telegram Bot Token:" "$YELLOW"
    print_msg "   - Get it from @BotFather on Telegram" "$NC"
    print_msg "   - Add API_ID and API_HASH from my.telegram.org" "$NC"
    print_msg "   - Add your Telegram user ID to ADMIN_IDS" "$NC"
    echo ""
    print_msg "3. Start the bot:" "$YELLOW"
    print_msg "   ./start.sh start" "$NC"
    echo ""
    print_msg "4. Check status:" "$YELLOW"
    print_msg "   ./start.sh status" "$NC"
    echo ""
    print_msg "5. View logs:" "$YELLOW"
    print_msg "   ./start.sh logs" "$NC"
    echo ""
    print_msg "📚 For more help, check README.md" "$BLUE"
    echo ""
    print_msg "🌟 Star the repo if you find it useful!" "$PURPLE"
    echo ""
    
    # Ask if user wants to configure now
    read -p "$(echo -e ${YELLOW}Do you want to edit .env now? \(y/n\):${NC} )" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command_exists nano; then
            nano .env
        elif command_exists vim; then
            vim .env
        else
            print_msg "Please edit .env with your preferred editor" "$YELLOW"
        fi
    fi
    
    echo ""
    print_msg "🎉 Happy Encoding!" "$GREEN"
}

# Run main function
main
