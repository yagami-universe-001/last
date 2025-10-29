import os
import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config
from database import Database
from encoder import VideoEncoder
from utils import (
    format_progress_bar, 
    format_time, 
    format_size,
    check_user_subscription,
    generate_shortlink
)

# Initialize bot
app = Client(
    "encoder_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Initialize database and encoder
db = Database()
encoder = VideoEncoder()

# Active tasks dictionary
active_tasks = {}
user_settings = {}


@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Check force subscribe
    if not await check_user_subscription(client, user_id):
        channels = db.get_force_subscribe_channels()
        buttons = []
        for channel in channels:
            buttons.append([InlineKeyboardButton("Join Channel", url=channel['url'])])
        buttons.append([InlineKeyboardButton("✅ Joined", callback_data="check_join")])
        
        await message.reply_text(
            "⚠️ **You must join our channels to use this bot!**\n\n"
            "Click the buttons below to join:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Add user to database
    db.add_user(user_id, message.from_user.first_name)
    
    # Get start picture if set
    start_pic = db.get_start_picture()
    
    buttons = [
        [InlineKeyboardButton("📊 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
         InlineKeyboardButton("💎 Premium", callback_data="premium")]
    ]
    
    text = (
        f"👋 **Welcome {message.from_user.mention}!**\n\n"
        "🎬 **I'm an Advanced Video Encoder Bot**\n\n"
        "**Features:**\n"
        "├ 🎯 Multiple Quality Options\n"
        "├ 🔄 Fast Encoding (Turbo Speed)\n"
        "├ ✂️ Video Editing Tools\n"
        "├ 🎨 Watermark & Subtitles\n"
        "└ 📦 Batch Processing\n\n"
        "**Send me a video to get started!**\n"
        "Use /help to see all commands."
    )
    
    if start_pic:
        await message.reply_photo(
            photo=start_pic,
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    """Show help message with all commands"""
    help_text = """
**📚 Available Commands:**

**🎬 Encoding Commands:**
├ /144p - Convert to 144p
├ /240p - Convert to 240p
├ /360p - Convert to 360p
├ /480p - Convert to 480p (SD)
├ /720p - Convert to 720p (HD)
├ /1080p - Convert to 1080p (Full HD)
├ /2160p - Convert to 2160p (4K)
├ /compress - Compress video by %
└ /all - Encode all qualities (Premium)

**✂️ Editing Commands:**
├ /cut - Trim video by time
├ /crop - Change aspect ratio
├ /merge - Merge multiple videos
└ /rename - Rename file

**🎨 Media Commands:**
├ /addwatermark - Add watermark
├ /sub - Add soft subtitles
├ /hsub - Hard subtitles
├ /rsub - Remove subtitles
├ /extract_sub - Extract subtitle
├ /addaudio - Add audio track
├ /remaudio - Remove audio
└ /extract_audio - Extract as MP3

**📸 Thumbnail Commands:**
├ /extract_thumb - Get thumbnail
├ /setthumb - Set custom thumb
├ /getthumb - View saved thumb
└ /delthumb - Delete thumb

**⚙️ Settings Commands:**
├ /setwatermark - Set watermark text
├ /getwatermark - View watermark
├ /setmedia - Set upload type
├ /spoiler - Toggle spoiler mode
└ /upload - Set destination

**📦 Utility Commands:**
├ /unzip - Extract archives
├ /mediainfo - Video information
├ /tasks - Active tasks
└ /stop - Cancel task

**Use /start to return to main menu**
"""
    
    buttons = [[InlineKeyboardButton("◀️ Back", callback_data="start")]]
    await message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_message(filters.video | filters.document)
async def handle_media(client, message: Message):
    """Handle incoming video/document files"""
    user_id = message.from_user.id
    
    # Check subscription
    if not await check_user_subscription(client, user_id):
        await message.reply_text("⚠️ Please join our channels first! Use /start")
        return
    
    # Check if user has active task
    if user_id in active_tasks and active_tasks[user_id].get('status') == 'processing':
        await message.reply_text(
            "⚠️ **You already have an active task!**\n\n"
            "Please wait for it to complete or use /stop to cancel it."
        )
        return
    
    # Get file info
    media = message.video or message.document
    file_name = media.file_name
    file_size = media.file_size
    duration = getattr(media, 'duration', 0)
    
    # Check file size limits
    is_premium = db.is_premium_user(user_id)
    max_size = Config.PREMIUM_MAX_SIZE if is_premium else Config.FREE_MAX_SIZE
    
    if file_size > max_size:
        await message.reply_text(
            f"❌ **File too large!**\n\n"
            f"Your file: {format_size(file_size)}\n"
            f"Max allowed: {format_size(max_size)}\n\n"
            f"{'Upgrade to premium for larger files!' if not is_premium else ''}"
        )
        return
    
    # Show quality selection buttons
    buttons = [
        [
            InlineKeyboardButton("144p", callback_data=f"encode_144p"),
            InlineKeyboardButton("240p", callback_data=f"encode_240p"),
            InlineKeyboardButton("360p", callback_data=f"encode_360p")
        ],
        [
            InlineKeyboardButton("480p", callback_data=f"encode_480p"),
            InlineKeyboardButton("720p", callback_data=f"encode_720p"),
            InlineKeyboardButton("1080p", callback_data=f"encode_1080p")
        ],
        [
            InlineKeyboardButton("2160p (4K)", callback_data=f"encode_2160p"),
            InlineKeyboardButton("🗜 Compress", callback_data=f"compress")
        ]
    ]
    
    if is_premium:
        buttons.append([InlineKeyboardButton("🎯 All Qualities", callback_data="encode_all")])
    
    buttons.append([InlineKeyboardButton("ℹ️ Media Info", callback_data="show_mediainfo")])
    
    # Store file message for later use
    user_settings[user_id] = {
        'file_message': message,
        'file_name': file_name,
        'file_size': file_size,
        'duration': duration
    }
    
    await message.reply_text(
        f"📥 **File Received!**\n\n"
        f"📝 Name: `{file_name}`\n"
        f"📦 Size: {format_size(file_size)}\n"
        f"⏱ Duration: {format_time(duration)}\n\n"
        f"**Select encoding quality:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"^encode_"))
async def handle_encode_callback(client, callback_query):
    """Handle encoding quality selection"""
    user_id = callback_query.from_user.id
    quality = callback_query.data.replace("encode_", "")
    
    if user_id not in user_settings:
        await callback_query.answer("❌ File data expired! Send the file again.", show_alert=True)
        return
    
    await callback_query.answer("🔄 Starting encoding...", show_alert=False)
    
    file_data = user_settings[user_id]
    file_message = file_data['file_message']
    
    # Start encoding task
    asyncio.create_task(
        encode_video(client, callback_query.message, file_message, user_id, quality)
    )


async def encode_video(client, status_message, file_message, user_id, quality):
    """Main encoding function with progress tracking"""
    try:
        # Mark task as active
        active_tasks[user_id] = {
            'status': 'processing',
            'start_time': time.time(),
            'current_stage': 'downloading'
        }
        
        file_data = user_settings[user_id]
        file_name = file_data['file_name']
        
        # Create unique task ID
        task_id = f"{user_id}_{int(time.time())}"
        
        # Download file with progress
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{task_id}_{file_name}")
        
        progress_msg = await status_message.edit_text(
            "**1. Downloading**\n"
            f"`{file_name}`\n\n"
            f"{format_progress_bar(0)}\n"
            f"├ Speed: 0 MB/s\n"
            f"├ Size: 0 MB / {format_size(file_data['file_size'])}\n"
            f"├ ETA: Calculating...\n"
            f"├ Elapsed: 00:00:00\n"
            f"└ Task By: {file_message.from_user.mention}\n\n"
            f"`/stop{task_id}` to cancel"
        )
        
        start_time = time.time()
        
        async def download_progress(current, total):
            """Progress callback for download"""
            if active_tasks[user_id]['status'] == 'cancelled':
                raise Exception("Task cancelled by user")
            
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            percentage = (current / total) * 100
            
            # Update every 3 seconds to avoid flood
            if int(elapsed) % 3 == 0:
                try:
                    await progress_msg.edit_text(
                        "**1. Downloading**\n"
                        f"`{file_name}`\n\n"
                        f"{format_progress_bar(percentage)}\n"
                        f"├ Speed: {format_size(speed)}/s\n"
                        f"├ Size: {format_size(current)} / {format_size(total)}\n"
                        f"├ ETA: {format_time(int(eta))}\n"
                        f"├ Elapsed: {format_time(int(elapsed))}\n"
                        f"└ Task By: {file_message.from_user.mention}\n\n"
                        f"`/stop{task_id}` to cancel"
                    )
                except:
                    pass
        
        # Download the file
        await client.download_media(
            file_message,
            file_name=download_path,
            progress=download_progress
        )
        
        # Update status to encoding
        active_tasks[user_id]['current_stage'] = 'encoding'
        
        await progress_msg.edit_text(
            "**2. Encoding**\n"
            f"`{file_name}`\n\n"
            f"{format_progress_bar(0)}\n"
            f"├ Quality: {quality}\n"
            f"├ Codec: {db.get_codec()}\n"
            f"├ Preset: {db.get_preset()}\n"
            f"├ Status: Starting...\n"
            f"└ Task By: {file_message.from_user.mention}\n\n"
            f"`/stop{task_id}` to cancel"
        )
        
        # Encode video
        encode_start = time.time()
        output_path = await encoder.encode_video(
            download_path,
            quality,
            progress_callback=lambda data: asyncio.create_task(
                update_encode_progress(progress_msg, file_name, quality, data, encode_start, file_message.from_user, task_id)
            )
        )
        
        # Update status to uploading
        active_tasks[user_id]['current_stage'] = 'uploading'
        
        await progress_msg.edit_text(
            "**3. Uploading**\n"
            f"`{file_name}`\n\n"
            f"{format_progress_bar(0)}\n"
            f"├ Quality: {quality}\n"
            f"├ Status: Starting upload...\n"
            f"└ Task By: {file_message.from_user.mention}"
        )
        
        # Upload encoded video
        upload_start = time.time()
        
        async def upload_progress(current, total):
            """Progress callback for upload"""
            elapsed = time.time() - upload_start
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            percentage = (current / total) * 100
            
            if int(elapsed) % 3 == 0:
                try:
                    await progress_msg.edit_text(
                        "**3. Uploading**\n"
                        f"`{file_name}`\n\n"
                        f"{format_progress_bar(percentage)}\n"
                        f"├ Speed: {format_size(speed)}/s\n"
                        f"├ Size: {format_size(current)} / {format_size(total)}\n"
                        f"├ ETA: {format_time(int(eta))}\n"
                        f"├ Elapsed: {format_time(int(elapsed))}\n"
                        f"└ Task By: {file_message.from_user.mention}"
                    )
                except:
                    pass
        
        # Get user settings for upload
        upload_as_doc = db.get_user_setting(user_id, 'upload_as_document', False)
        use_spoiler = db.get_user_setting(user_id, 'spoiler_mode', False)
        
        caption = f"📹 **Encoded by Turbo Encoder Bot**\n\n"
        caption += f"Quality: {quality}\n"
        caption += f"Encoded by: {file_message.from_user.mention}"
        
        if upload_as_doc:
            await client.send_document(
                chat_id=user_id,
                document=output_path,
                caption=caption,
                progress=upload_progress
            )
        else:
            await client.send_video(
                chat_id=user_id,
                video=output_path,
                caption=caption,
                has_spoiler=use_spoiler,
                progress=upload_progress
            )
        
        # Cleanup
        os.remove(download_path)
        os.remove(output_path)
        
        # Update final status
        total_time = time.time() - active_tasks[user_id]['start_time']
        
        await progress_msg.edit_text(
            f"✅ **Encoding Complete!**\n\n"
            f"📝 File: `{file_name}`\n"
            f"🎯 Quality: {quality}\n"
            f"⏱ Time Taken: {format_time(int(total_time))}\n\n"
            f"Thank you for using Turbo Encoder! 🚀"
        )
        
        # Remove from active tasks
        del active_tasks[user_id]
        
    except Exception as e:
        await status_message.edit_text(
            f"❌ **Encoding Failed!**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again or contact support."
        )
        
        if user_id in active_tasks:
            del active_tasks[user_id]
        
        # Cleanup files
        try:
            if os.path.exists(download_path):
                os.remove(download_path)
        except:
            pass


async def update_encode_progress(msg, filename, quality, data, start_time, user, task_id):
    """Update encoding progress message"""
    try:
        elapsed = time.time() - start_time
        percentage = data.get('percentage', 0)
        speed = data.get('speed', '0x')
        time_left = data.get('time_left', '00:00:00')
        
        await msg.edit_text(
            "**2. Encoding**\n"
            f"`{filename}`\n\n"
            f"{format_progress_bar(percentage)}\n"
            f"├ Speed: {speed}\n"
            f"├ Quality: {quality}\n"
            f"├ Time Left: {time_left}\n"
            f"├ Elapsed: {format_time(int(elapsed))}\n"
            f"└ Task By: {user.mention}\n\n"
            f"`/stop{task_id}` to cancel"
        )
    except:
        pass


@app.on_message(filters.command("stop") & filters.private)
async def stop_task(client, message: Message):
    """Cancel active encoding task"""
    user_id = message.from_user.id
    
    if user_id not in active_tasks:
        await message.reply_text("❌ No active task to cancel!")
        return
    
    active_tasks[user_id]['status'] = 'cancelled'
    await message.reply_text("✅ Task cancelled successfully!")


@app.on_message(filters.command("tasks") & filters.private)
async def show_tasks(client, message: Message):
    """Show active tasks"""
    user_id = message.from_user.id
    
    if user_id not in active_tasks:
        await message.reply_text("📭 No active tasks!")
        return
    
    task = active_tasks[user_id]
    elapsed = time.time() - task['start_time']
    
    text = f"**📊 Active Task:**\n\n"
    text += f"├ Status: {task['status'].title()}\n"
    text += f"├ Stage: {task['current_stage'].title()}\n"
    text += f"└ Elapsed: {format_time(int(elapsed))}\n\n"
    text += f"Use /stop to cancel"
    
    await message.reply_text(text)


if __name__ == "__main__":
    print("🚀 Bot starting...")
    app.run()
