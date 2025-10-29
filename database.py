import sqlite3
import json
from datetime import datetime
from config import Config


class Database:
    """Database handler for bot"""
    
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create necessary database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium BOOLEAN DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                watermark_text TEXT,
                thumbnail_path TEXT,
                upload_as_document BOOLEAN DEFAULT 0,
                spoiler_mode BOOLEAN DEFAULT 0,
                upload_destination TEXT DEFAULT 'private',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Premium users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                added_by INTEGER,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Force subscribe channels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS force_subscribe_channels (
                channel_id INTEGER PRIMARY KEY,
                channel_url TEXT,
                channel_name TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Initialize default bot settings
        default_settings = {
            'codec': Config.DEFAULT_CODEC,
            'preset': Config.DEFAULT_PRESET,
            'crf': str(Config.DEFAULT_CRF),
            'audio_bitrate': Config.DEFAULT_AUDIO_BITRATE,
            'fsub_mode': Config.FSUB_MODE,
            'start_picture': '',
            'shortener_1_api': Config.SHORTENER_1_API,
            'shortener_1_url': Config.SHORTENER_1_URL,
            'tutorial_1': Config.TUTORIAL_1,
            'shortener_2_api': Config.SHORTENER_2_API,
            'shortener_2_url': Config.SHORTENER_2_URL,
            'tutorial_2': Config.TUTORIAL_2
        }
        
        for key, value in default_settings.items():
            cursor.execute('''
                INSERT OR IGNORE INTO bot_settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
        
        conn.commit()
        conn.close()
    
    # User Management
    def add_user(self, user_id, first_name, username=None):
        """Add new user to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_active)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name))
        
        # Create user settings if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (user_id)
            VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Get user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def is_premium_user(self, user_id):
        """Check if user has premium access"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM premium_users 
            WHERE user_id = ? AND (expiry_date IS NULL OR expiry_date > CURRENT_TIMESTAMP)
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def add_premium_user(self, user_id, added_by, expiry_date=None):
        """Add premium user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO premium_users (user_id, added_by, expiry_date)
            VALUES (?, ?, ?)
        ''', (user_id, added_by, expiry_date))
        
        conn.commit()
        conn.close()
    
    def remove_premium_user(self, user_id):
        """Remove premium user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM premium_users WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_premium_users(self):
        """Get list of all premium users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.first_name, p.added_date, p.expiry_date
            FROM premium_users p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.expiry_date IS NULL OR p.expiry_date > CURRENT_TIMESTAMP
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return users
    
    # User Settings
    def get_user_setting(self, user_id, setting_key, default=None):
        """Get specific user setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT {setting_key} FROM user_settings WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[setting_key] is not None:
            return result[setting_key]
        return default
    
    def set_user_setting(self, user_id, setting_key, value):
        """Set user setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE user_settings
            SET {setting_key} = ?
            WHERE user_id = ?
        ''', (value, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_watermark(self, user_id):
        """Get user's watermark text"""
        return self.get_user_setting(user_id, 'watermark_text', Config.DEFAULT_WATERMARK_TEXT)
    
    def set_user_watermark(self, user_id, text):
        """Set user's watermark text"""
        self.set_user_setting(user_id, 'watermark_text', text)
    
    def get_user_thumbnail(self, user_id):
        """Get user's thumbnail path"""
        return self.get_user_setting(user_id, 'thumbnail_path')
    
    def set_user_thumbnail(self, user_id, path):
        """Set user's thumbnail path"""
        self.set_user_setting(user_id, 'thumbnail_path', path)
    
    # Force Subscribe Channels
    def add_force_subscribe_channel(self, channel_id, channel_url, channel_name):
        """Add force subscribe channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO force_subscribe_channels (channel_id, channel_url, channel_name)
            VALUES (?, ?, ?)
        ''', (channel_id, channel_url, channel_name))
        
        conn.commit()
        conn.close()
    
    def remove_force_subscribe_channel(self, channel_id):
        """Remove force subscribe channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM force_subscribe_channels WHERE channel_id = ?', (channel_id,))
        
        conn.commit()
        conn.close()
    
    def get_force_subscribe_channels(self):
        """Get all force subscribe channels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM force_subscribe_channels')
        channels = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return channels
    
    # Bot Settings
    def get_bot_setting(self, key, default=None):
        """Get bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM bot_settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result['value'] if result else default
    
    def set_bot_setting(self, key, value):
        """Set bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_codec(self):
        """Get encoding codec"""
        return self.get_bot_setting('codec', Config.DEFAULT_CODEC)
    
    def set_codec(self, codec):
        """Set encoding codec"""
        self.set_bot_setting('codec', codec)
    
    def get_preset(self):
        """Get encoding preset"""
        return self.get_bot_setting('preset', Config.DEFAULT_PRESET)
    
    def set_preset(self, preset):
        """Set encoding preset"""
        self.set_bot_setting('preset', preset)
    
    def get_crf(self):
        """Get CRF value"""
        return int(self.get_bot_setting('crf', Config.DEFAULT_CRF))
    
    def set_crf(self, crf):
        """Set CRF value"""
        self.set_bot_setting('crf', str(crf))
    
    def get_audio_bitrate(self):
        """Get audio bitrate"""
        return self.get_bot_setting('audio_bitrate', Config.DEFAULT_AUDIO_BITRATE)
    
    def set_audio_bitrate(self, bitrate):
        """Set audio bitrate"""
        self.set_bot_setting('audio_bitrate', bitrate)
    
    def get_start_picture(self):
        """Get start picture file_id"""
        return self.get_bot_setting('start_picture')
    
    def set_start_picture(self, file_id):
        """Set start picture file_id"""
        self.set_bot_setting('start_picture', file_id)
    
    def get_fsub_mode(self):
        """Get force subscribe mode"""
        return self.get_bot_setting('fsub_mode', 'off')
    
    def set_fsub_mode(self, mode):
        """Set force subscribe mode"""
        self.set_bot_setting('fsub_mode', mode)
    
    # Statistics
    def get_total_users(self):
        """Get total user count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM users')
        result = cursor.fetchone()
        
        conn.close()
        return result['count']
    
    def get_premium_count(self):
        """Get premium user count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM premium_users
            WHERE expiry_date IS NULL OR expiry_date > CURRENT_TIMESTAMP
        ''')
        result = cursor.fetchone()
        
        conn.close()
        return result['count']
