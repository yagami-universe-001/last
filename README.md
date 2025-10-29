# 🎬 Advanced Telegram Video Encoder Bot

A powerful, feature-rich Telegram bot for video encoding with turbo-fast processing speed and beautiful progress tracking UI.

## ✨ Features

### 🎯 Core Encoding Features
- **Multiple Quality Options**: 144p, 240p, 360p, 480p, 720p, 1080p, 4K (2160p)
- **Fast Encoding**: Optimized FFmpeg settings for turbo-speed processing
- **Batch Processing**: Encode all qualities at once (Premium)
- **Video Compression**: Compress by percentage
- **Custom Codec Support**: H.264, H.265/HEVC, VP9, AV1

### ✂️ Video Editing Tools
- **Trim/Cut**: Cut videos by time range
- **Crop**: Change aspect ratio
- **Merge**: Combine multiple videos
- **Rename**: Custom filename support

### 🎨 Media Enhancement
- **Watermark**: Add text or logo watermarks
- **Subtitles**: Add soft/hard subtitles
- **Remove Subtitles**: Extract or remove subtitle tracks
- **Audio Management**: Add, remove, or extract audio

### 📸 Thumbnail Management
- **Extract Thumbnails**: Get video screenshots
- **Custom Thumbnails**: Set personal thumbnails
- **Auto-Thumbnails**: Automatic thumbnail generation

### 📦 Additional Tools
- **Archive Extraction**: Unzip ZIP, TAR, 7Z files
- **Media Info**: Detailed video information
- **Task Management**: View and cancel active tasks
- **Format Conversion**: Convert between formats

### 👑 Premium Features
- **All Quality Encoding**: Encode all qualities simultaneously
- **Higher File Size Limits**: Up to 4GB (vs 2GB free)
- **Priority Processing**: Faster queue priority
- **Advanced Settings**: Custom CRF, bitrate control

### 🔐 Admin Features
- **User Management**: Add/remove premium users
- **Bot Settings**: Configure codec, preset, CRF
- **Force Subscribe**: Channel subscription enforcement
- **Shortener Integration**: Monetize with URL shorteners
- **Statistics**: User counts and analytics
- **Queue Management**: View and clear task queue

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed and in PATH
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/encoder-bot.git
cd encoder-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

4. **Configure environment**
```bash
cp .env.example .env
nano .env
```

Fill in your credentials:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_user_id
```

5. **Create directories**
```bash
mkdir downloads encodes thumbnails
```

6. **Run the bot**
```bash
python bot.py
```

## 📖 Usage

### Basic Commands

**General:**
- `/start` - Start the bot and see main menu
- `/help` - Show all available commands
- `/tasks` - View active encoding tasks
- `/stop` - Cancel ongoing task

**Encoding:**
- `/144p` - Convert to 144p
- `/240p` - Convert to 240p
- `/360p` - Convert to 360p
- `/480p` - Convert to 480p (SD)
- `/720p` - Convert to 720p (HD)
- `/1080p` - Convert to 1080p (Full HD)
- `/2160p` - Convert to 2160p (4K)
- `/compress` - Compress video by percentage
- `/all` - Encode all qualities (Premium only)

**Editing:**
- `/cut` - Trim video (e.g., `/cut 00:00:10 00:02:30`)
- `/crop` - Change aspect ratio
- `/merge` - Merge multiple videos
- `/rename` - Rename file

**Media:**
- `/addwatermark` - Add watermark to video
- `/sub` - Add soft subtitles
- `/hsub` - Add hard subtitles (burned-in)
- `/rsub` - Remove all subtitles
- `/extract_sub` - Extract subtitle file
- `/addaudio` - Add audio track
- `/remaudio` - Remove audio
- `/extract_audio` - Extract audio as MP3

**Thumbnails:**
- `/extract_thumb` - Extract thumbnail from video
- `/setthumb` - Set custom thumbnail
- `/getthumb` - View saved thumbnail
- `/delthumb` - Delete thumbnail

**Settings:**
- `/setwatermark` - Set watermark text
- `/getwatermark` - View current watermark
- `/setmedia` - Set upload type (video/document)
- `/spoiler` - Toggle spoiler mode
- `/upload` - Set upload destination

**Utilities:**
- `/unzip` - Extract compressed archives
- `/mediainfo` - Get detailed video information

### Admin Commands

**User Management:**
- `/addpaid` - Add premium user
- `/listpaid` - List all premium users
- `/rempaid` - Remove premium user

**Bot Configuration:**
- `/codec` - Set video codec
- `/preset` - Set encoding preset
- `/crf` - Set quality level (0-51)
- `/audio` - Set audio bitrate
- `/restart` - Restart the bot

**Queue Management:**
- `/queue` - Check total queue tasks
- `/clear` - Clear all queued tasks

**Force Subscribe:**
- `/addchnl` - Add force subscribe channel
- `/delchnl` - Remove force subscribe channel
- `/listchnl` - List all channels
- `/fsub_mode` - Set force subscribe mode

**Shortener:**
- `/shortner` - View shortener settings
- `/shortlink1` - Set shortener 1 API and URL
- `/tutorial1` - Set tutorial for shortener 1
- `/shortlink2` - Set shortener 2 API and URL
- `/tutorial2` - Set tutorial for shortener 2
- `/shortner1` - View shortener 1 configuration
- `/shortner2` - View shortener 2 configuration

**Appearance:**
- `/setstartpic` - Set start banner/picture
- `/getstartpic` - View current start picture
- `/delstartpic` - Remove start picture

**System:**
- `/update` - Pull latest updates from Git

## 🎨 Progress Display

The bot features a beautiful progress display similar to professional encoding tools:

```
1. Downloading
Peaky.blinders.S02.Ep[1-6].mkv

[●●○○○○○○○○] 25.5%
├ Speed: 2.95 MB/s
├ Size: 62.00 MB / 2.40 GB
├ ETA: 13m 31s
├ Elapsed: 00:00:16
└ Task By: @username

/stop2bCD3QTTP to cancel
```

## ⚙️ Configuration

### Encoding Presets

**Codec Options:**
- `libx264` - H.264 (widely compatible)
- `libx265` - H.265/HEVC (better compression)
- `libvpx-vp9` - VP9 (web-friendly)
- `libaom-av1` - AV1 (best compression, slower)

**Preset Options:**
- `ultrafast` - Fastest encoding, lower quality
- `superfast` - Very fast encoding
- `veryfast` - Fast encoding
- `faster` - Faster than default
- `fast` - Fast encoding
- `medium` - Balanced (recommended)
- `slow` - Slower encoding, better quality
- `slower` - Very slow, high quality
- `veryslow` - Slowest, best quality

**CRF Values:**
- `0-17` - Visually lossless (huge files)
- `18-23` - High quality (recommended)
- `24-28` - Good quality (default: 28)
- `29-35` - Lower quality (smaller files)
- `36-51` - Poor quality

### Quality Presets

| Quality | Resolution | Bitrate |
|---------|-----------|---------|
| 144p | 256x144 | 95 Kbps |
| 240p | 426x240 | 150 Kbps |
| 360p | 640x360 | 276 Kbps |
| 480p | 854x480 | 500 Kbps |
| 720p | 1280x720 | 1024 Kbps |
| 1080p | 1920x1080 | 2000 Kbps |
| 2160p | 3840x2160 | 4000 Kbps |

## 🔧 Advanced Configuration

### Database Schema

The bot uses SQLite with the following tables:
- `users` - User information and stats
- `user_settings` - Individual user preferences
- `premium_users` - Premium membership tracking
- `force_subscribe_channels` - Required channels
- `bot_settings` - Global bot configuration

### File Structure

```
encoder-bot/
├── bot.py              # Main bot file
├── config.py           # Configuration
├── database.py         # Database handler
├── encoder.py          # Video encoding engine
├── utils.py            # Utility functions
├── requirements.txt    # Dependencies
├── .env               # Environment variables
├── README.md          # Documentation
├── downloads/         # Downloaded files
├── encodes/           # Encoded outputs
└── thumbnails/        # Thumbnail storage
```

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

**Permission errors:**
```bash
# Fix directory permissions
chmod -R 755 downloads encodes thumbnails
```

**Database errors:**
```bash
# Delete and recreate database
rm bot.db
python bot.py
```

**Encoding fails:**
- Check FFmpeg installation: `ffmpeg -version`
- Verify file is valid video
- Check available disk space
- Review FFmpeg logs in console

## 📊 Performance Optimization

**Tips for faster encoding:**

1. Use faster presets (`fast`, `veryfast`, `superfast`)
2. Choose H.264 over H.265 for speed
3. Lower CRF values encode faster but larger files
4. Use hardware acceleration if available
5. Process during off-peak hours

**Hardware Acceleration:**

Add to config for GPU encoding:
```python
# NVIDIA
'-hwaccel', 'cuda', '-c:v', 'h264_nvenc'

# Intel Quick Sync
'-hwaccel', 'qsv', '-c:v', 'h264_qsv'

# AMD
'-hwaccel', 'vaapi', '-c:v', 'h264_vaapi'
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## ⚠️ Disclaimer

This bot is for educational purposes. Ensure you have rights to any content you process. Respect copyright laws and Telegram's Terms of Service.

## 🌟 Support

If you find this bot helpful:
- ⭐ Star the repository
- 🐛 Report bugs via Issues
- 💡 Suggest features
- 🤝 Contribute code

## 📞 Contact

For support or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/encoder-bot/issues)
- Telegram: @YourChannel
- Email: your.email@example.com

## 🎉 Credits

Developed with ❤️ using:
- [Pyrogram](https://docs.pyrogram.org/) - Telegram MTProto API framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing
- [Python](https://python.org/) - Programming language

---

**Made with 🚀 for the Telegram community**
