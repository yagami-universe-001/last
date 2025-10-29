import requests
from pyrogram.errors import UserNotParticipant
from database import Database

db = Database()


def format_progress_bar(percentage):
    """Format progress bar with percentage"""
    filled = int(percentage / 10)
    empty = 10 - filled
    bar = '●' * filled + '○' * empty
    return f"[{bar}] {percentage:.2f}%"


def format_time(seconds):
    """Format seconds to readable time"""
    if seconds < 0:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


async def check_user_subscription(client, user_id):
    """Check if user is subscribed to required channels"""
    fsub_mode = db.get_fsub_mode()
    
    if fsub_mode == 'off':
        return True
    
    channels = db.get_force_subscribe_channels()
    
    if not channels:
        return True
    
    for channel in channels:
        try:
            member = await client.get_chat_member(channel['channel_id'], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            # If we can't check, allow access
            pass
    
    return True


def generate_shortlink(url, shortener_num=1):
    """Generate short link using shortener API"""
    if shortener_num == 1:
        api_key = db.get_bot_setting('shortener_1_api')
        api_url = db.get_bot_setting('shortener_1_url')
    else:
        api_key = db.get_bot_setting('shortener_2_api')
        api_url = db.get_bot_setting('shortener_2_url')
    
    if not api_key or not api_url:
        return url
    
    try:
        response = requests.get(
            f"{api_url}/api",
            params={'api': api_key, 'url': url},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('shortenedUrl', url)
    except Exception:
        pass
    
    return url


def parse_time_format(time_str):
    """Parse time string to seconds (HH:MM:SS or MM:SS)"""
    parts = time_str.split(':')
    
    try:
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return int(time_str)
    except:
        return 0


def seconds_to_time_format(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def is_admin(user_id):
    """Check if user is admin"""
    from config import Config
    return user_id in Config.ADMIN_IDS


def get_readable_file_size(size_in_bytes):
    """Get human readable file size"""
    return format_size(size_in_bytes)


def extract_file_extension(filename):
    """Extract file extension from filename"""
    import os
    return os.path.splitext(filename)[1]


def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    return filename.strip()


def generate_stream_link(file_id):
    """Generate streaming link for file (if implemented)"""
    # This is a placeholder - implement based on your streaming service
    return f"https://stream.example.com/{file_id}"


def format_bitrate(bitrate_str):
    """Format bitrate string"""
    if bitrate_str.endswith('k'):
        return f"{bitrate_str[:-1]} Kbps"
    elif bitrate_str.endswith('m'):
        return f"{bitrate_str[:-1]} Mbps"
    return bitrate_str


def get_codec_name(codec):
    """Get friendly codec name"""
    codec_names = {
        'libx264': 'H.264 (x264)',
        'libx265': 'H.265 (x265/HEVC)',
        'libvpx-vp9': 'VP9',
        'libaom-av1': 'AV1',
        'mpeg4': 'MPEG-4'
    }
    return codec_names.get(codec, codec)


def get_preset_description(preset):
    """Get preset description"""
    descriptions = {
        'ultrafast': '⚡ Fastest (lowest quality)',
        'superfast': '🚀 Super Fast',
        'veryfast': '⏩ Very Fast',
        'faster': '▶️ Faster',
        'fast': '▶ Fast',
        'medium': '⚖️ Balanced (recommended)',
        'slow': '🐢 Slow (better quality)',
        'slower': '🐌 Slower',
        'veryslow': '🦥 Very Slow (best quality)'
    }
    return descriptions.get(preset, preset)


def calculate_estimated_size(duration, quality):
    """Calculate estimated output file size"""
    from config import Config
    
    preset = Config.QUALITY_PRESETS.get(quality, Config.QUALITY_PRESETS['480p'])
    video_bitrate = int(preset['video_bitrate'].replace('k', ''))
    audio_bitrate = int(Config.DEFAULT_AUDIO_BITRATE.replace('k', ''))
    
    # Total bitrate in kbps
    total_bitrate = video_bitrate + audio_bitrate
    
    # Calculate size in bytes
    estimated_size = (total_bitrate * 1000 / 8) * duration
    
    return int(estimated_size)


def is_video_file(filename):
    """Check if file is a video"""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v']
    import os
    return os.path.splitext(filename.lower())[1] in video_extensions


def is_audio_file(filename):
    """Check if file is audio"""
    audio_extensions = ['.mp3', '.aac', '.flac', '.wav', '.ogg', '.m4a', '.wma']
    import os
    return os.path.splitext(filename.lower())[1] in audio_extensions


def is_subtitle_file(filename):
    """Check if file is subtitle"""
    subtitle_extensions = ['.srt', '.ass', '.ssa', '.vtt', '.sub']
    import os
    return os.path.splitext(filename.lower())[1] in subtitle_extensions


def is_archive_file(filename):
    """Check if file is archive"""
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    import os
    return os.path.splitext(filename.lower())[1] in archive_extensions


def create_video_thumbnail_grid(screenshots):
    """Create thumbnail grid from screenshots (for future implementation)"""
    # Placeholder for creating thumbnail grid
    pass


def get_video_quality_name(quality):
    """Get friendly quality name"""
    quality_names = {
        '144p': '144p (Low)',
        '240p': '240p (Basic)',
        '360p': '360p (Standard)',
        '480p': '480p (SD)',
        '720p': '720p (HD)',
        '1080p': '1080p (Full HD)',
        '2160p': '2160p (4K Ultra HD)'
    }
    return quality_names.get(quality, quality)


def format_speed(speed_value):
    """Format encoding speed value"""
    try:
        speed = float(str(speed_value).replace('x', ''))
        if speed > 1:
            return f"⚡ {speed:.2f}x"
        else:
            return f"🐌 {speed:.2f}x"
    except:
        return speed_value


async def send_log_message(client, message):
    """Send log message to admin log channel (if configured)"""
    from config import Config
    
    if hasattr(Config, 'LOG_CHANNEL') and Config.LOG_CHANNEL:
        try:
            await client.send_message(Config.LOG_CHANNEL, message)
        except:
            pass
