import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration"""
    
    # Telegram Bot Settings
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    
    # Admin Settings
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split()))
    
    # File Size Limits (in bytes)
    FREE_MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
    PREMIUM_MAX_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB
    
    # Directory Settings
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
    ENCODE_DIR = os.getenv("ENCODE_DIR", "encodes")
    THUMB_DIR = os.getenv("THUMB_DIR", "thumbnails")
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    
    # Encoding Settings
    DEFAULT_CODEC = os.getenv("DEFAULT_CODEC", "libx265")
    DEFAULT_PRESET = os.getenv("DEFAULT_PRESET", "medium")
    DEFAULT_CRF = int(os.getenv("DEFAULT_CRF", "28"))
    DEFAULT_AUDIO_BITRATE = os.getenv("DEFAULT_AUDIO_BITRATE", "128k")
    
    # FFmpeg Path
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
    FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")
    
    # Shortener Settings
    SHORTENER_1_API = os.getenv("SHORTENER_1_API", "")
    SHORTENER_1_URL = os.getenv("SHORTENER_1_URL", "")
    TUTORIAL_1 = os.getenv("TUTORIAL_1", "")
    
    SHORTENER_2_API = os.getenv("SHORTENER_2_API", "")
    SHORTENER_2_URL = os.getenv("SHORTENER_2_URL", "")
    TUTORIAL_2 = os.getenv("TUTORIAL_2", "")
    
    # Force Subscribe Mode
    FSUB_MODE = os.getenv("FSUB_MODE", "off")  # on/off
    
    # Quality Presets
    QUALITY_PRESETS = {
        '144p': {'resolution': '256x144', 'video_bitrate': '95k'},
        '240p': {'resolution': '426x240', 'video_bitrate': '150k'},
        '360p': {'resolution': '640x360', 'video_bitrate': '276k'},
        '480p': {'resolution': '854x480', 'video_bitrate': '500k'},
        '720p': {'resolution': '1280x720', 'video_bitrate': '1024k'},
        '1080p': {'resolution': '1920x1080', 'video_bitrate': '2000k'},
        '2160p': {'resolution': '3840x2160', 'video_bitrate': '4000k'}
    }
    
    # Watermark Settings
    DEFAULT_WATERMARK_TEXT = "Encoded by Turbo Bot"
    WATERMARK_POSITION = "10:10"  # x:y position
    WATERMARK_FONT_SIZE = 24
    
    # Create directories if they don't exist
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        directories = [
            Config.DOWNLOAD_DIR,
            Config.ENCODE_DIR,
            Config.THUMB_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Create directories on import
Config.create_directories()
