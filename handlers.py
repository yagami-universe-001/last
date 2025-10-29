from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import Database
from encoder import VideoEncoder
from utils import is_admin, format_size, format_time
import os

db = Database()
encoder = VideoEncoder()


# Admin command decorators
def admin_only(func):
    """Decorator to restrict commands to admins only"""
    async def wrapper(client, message):
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ This command is for admins only!")
            return
        return await func(client, message)
    return wrapper


# ============= Admin Commands =============

@Client.on_message(filters.command("codec") & filters.private)
@admin_only
async def set_codec_command(client, message: Message):
    """Set encoding codec (admin only)"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current_codec = db.get_codec()
        await message.reply_text(
            f"**Current Codec:** `{current_codec}`\n\n"
            "**Available Codecs:**\n"
            "├ `libx264` - H.264 (fast, compatible)\n"
            "├ `libx265` - H.265/HEVC (better compression)\n"
            "├ `libvpx-vp9` - VP9 (web-friendly)\n"
            "└ `libaom-av1` - AV1 (best compression)\n\n"
            "**Usage:** `/codec libx265`"
        )
        return
    
    codec = args[1].strip()
    valid_codecs = ['libx264', 'libx265', 'libvpx-vp9', 'libaom-av1', 'mpeg4']
    
    if codec not in valid_codecs:
        await message.reply_text(f"❌ Invalid codec! Choose from: {', '.join(valid_codecs)}")
        return
    
    db.set_codec(codec)
    await message.reply_text(f"✅ Codec set to: `{codec}`")


@Client.on_message(filters.command("preset") & filters.private)
@admin_only
async def set_preset_command(client, message: Message):
    """Set encoding preset (admin only)"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current_preset = db.get_preset()
        await message.reply_text(
            f"**Current Preset:** `{current_preset}`\n\n"
            "**Available Presets:**\n"
            "├ `ultrafast` - Fastest (lowest quality)\n"
            "├ `superfast` - Super fast\n"
            "├ `veryfast` - Very fast\n"
            "├ `faster` - Faster\n"
            "├ `fast` - Fast\n"
            "├ `medium` - Balanced (recommended)\n"
            "├ `slow` - Slower (better quality)\n"
            "├ `slower` - Very slow\n"
            "└ `veryslow` - Slowest (best quality)\n\n"
            "**Usage:** `/preset medium`"
        )
        return
    
    preset = args[1].strip()
    valid_presets = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
    
    if preset not in valid_presets:
        await message.reply_text(f"❌ Invalid preset! Choose from: {', '.join(valid_presets)}")
        return
    
    db.set_preset(preset)
    await message.reply_text(f"✅ Preset set to: `{preset}`")


@Client.on_message(filters.command("crf") & filters.private)
@admin_only
async def set_crf_command(client, message: Message):
    """Set CRF value (admin only)"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current_crf = db.get_crf()
        await message.reply_text(
            f"**Current CRF:** `{current_crf}`\n\n"
            "**CRF Range:** 0-51\n"
            "├ 0-17: Visually lossless\n"
            "├ 18-23: High quality\n"
            "├ 24-28: Good quality (default)\n"
            "├ 29-35: Lower quality\n"
            "└ 36-51: Poor quality\n\n"
            "Lower = better quality, larger file\n"
            "Higher = worse quality, smaller file\n\n"
            "**Usage:** `/crf 28`"
        )
        return
    
    try:
        crf = int(args[1].strip())
        if crf < 0 or crf > 51:
            raise ValueError
    except ValueError:
        await message.reply_text("❌ CRF must be a number between 0 and 51!")
        return
    
    db.set_crf(crf)
    await message.reply_text(f"✅ CRF set to: `{crf}`")


@Client.on_message(filters.command("audio") & filters.private)
@admin_only
async def set_audio_bitrate_command(client, message: Message):
    """Set audio bitrate (admin only)"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current_bitrate = db.get_audio_bitrate()
        await message.reply_text(
            f"**Current Audio Bitrate:** `{current_bitrate}`\n\n"
            "**Common Bitrates:**\n"
            "├ `64k` - Low quality\n"
            "├ `96k` - Medium quality\n"
            "├ `128k` - Good quality (default)\n"
            "├ `192k` - High quality\n"
            "└ `320k` - Very high quality\n\n"
            "**Usage:** `/audio 128k`"
        )
        return
    
    bitrate = args[1].strip()
    
    # Validate bitrate format
    if not bitrate.endswith('k') or not bitrate[:-1].isdigit():
        await message.reply_text("❌ Invalid format! Use format like: 128k, 192k, 320k")
        return
    
    db.set_audio_bitrate(bitrate)
    await message.reply_text(f"✅ Audio bitrate set to: `{bitrate}`")


@Client.on_message(filters.command("addpaid") & filters.private)
@admin_only
async def add_premium_user_command(client, message: Message):
    """Add premium user (admin only)"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text(
            "**Add Premium User**\n\n"
            "**Usage:** `/addpaid user_id [days]`\n"
            "**Example:** `/addpaid 123456789 30`\n\n"
            "If days not specified, premium is permanent."
        )
        return
    
    try:
        user_id = int(args[1])
        days = int(args[2]) if len(args) > 2 else None
        
        expiry_date = None
        if days:
            from datetime import datetime, timedelta
            expiry_date = datetime.now() + timedelta(days=days)
        
        db.add_premium_user(user_id, message.from_user.id, expiry_date)
        
        expiry_text = f"for {days} days" if days else "permanently"
        await message.reply_text(f"✅ User {user_id} added to premium {expiry_text}!")
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"🎉 **Congratulations!**\n\n"
                f"You've been granted premium access {expiry_text}!\n\n"
                f"Enjoy all premium features! 💎"
            )
        except:
            pass
    
    except ValueError:
        await message.reply_text("❌ Invalid user ID or days!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("rempaid") & filters.private)
@admin_only
async def remove_premium_user_command(client, message: Message):
    """Remove premium user (admin only)"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("**Usage:** `/rempaid user_id`")
        return
    
    try:
        user_id = int(args[1])
        db.remove_premium_user(user_id)
        await message.reply_text(f"✅ User {user_id} removed from premium!")
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "ℹ️ Your premium access has ended.\n\n"
                "Thank you for using our premium service!"
            )
        except:
            pass
    
    except ValueError:
        await message.reply_text("❌ Invalid user ID!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("listpaid") & filters.private)
@admin_only
async def list_premium_users_command(client, message: Message):
    """List all premium users (admin only)"""
    users = db.get_all_premium_users()
    
    if not users:
        await message.reply_text("📭 No premium users found!")
        return
    
    text = "**💎 Premium Users:**\n\n"
    for i, user in enumerate(users, 1):
        expiry = user.get('expiry_date', 'Permanent')
        text += f"{i}. User ID: `{user['user_id']}`\n"
        text += f"   Name: {user['first_name']}\n"
        text += f"   Expiry: {expiry}\n\n"
    
    await message.reply_text(text)


@Client.on_message(filters.command("addchnl") & filters.private)
@admin_only
async def add_force_subscribe_channel_command(client, message: Message):
    """Add force subscribe channel (admin only)"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply_text(
            "**Add Force Subscribe Channel**\n\n"
            "**Usage:** `/addchnl @channel_username or channel_id`\n"
            "**Example:** `/addchnl @mychannel`"
        )
        return
    
    channel = args[1].strip()
    
    try:
        # Get channel info
        chat = await client.get_chat(channel)
        
        db.add_force_subscribe_channel(
            chat.id,
            f"https://t.me/{chat.username}" if chat.username else "",
            chat.title
        )
        
        await message.reply_text(
            f"✅ Channel added to force subscribe!\n\n"
            f"**Name:** {chat.title}\n"
            f"**ID:** `{chat.id}`"
        )
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("delchnl") & filters.private)
@admin_only
async def delete_force_subscribe_channel_command(client, message: Message):
    """Remove force subscribe channel (admin only)"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("**Usage:** `/delchnl channel_id`")
        return
    
    try:
        channel_id = int(args[1])
        db.remove_force_subscribe_channel(channel_id)
        await message.reply_text(f"✅ Channel removed from force subscribe!")
    
    except ValueError:
        await message.reply_text("❌ Invalid channel ID!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("listchnl") & filters.private)
@admin_only
async def list_force_subscribe_channels_command(client, message: Message):
    """List all force subscribe channels (admin only)"""
    channels = db.get_force_subscribe_channels()
    
    if not channels:
        await message.reply_text("📭 No force subscribe channels!")
        return
    
    text = "**📢 Force Subscribe Channels:**\n\n"
    for i, channel in enumerate(channels, 1):
        text += f"{i}. {channel['channel_name']}\n"
        text += f"   ID: `{channel['channel_id']}`\n"
        text += f"   URL: {channel['channel_url']}\n\n"
    
    await message.reply_text(text)


@Client.on_message(filters.command("fsub_mode") & filters.private)
@admin_only
async def set_fsub_mode_command(client, message: Message):
    """Set force subscribe mode (admin only)"""
    args = message.text.split()
    
    if len(args) < 2:
        current_mode = db.get_fsub_mode()
        await message.reply_text(
            f"**Current Mode:** `{current_mode}`\n\n"
            "**Usage:** `/fsub_mode on` or `/fsub_mode off`"
        )
        return
    
    mode = args[1].strip().lower()
    
    if mode not in ['on', 'off']:
        await message.reply_text("❌ Mode must be 'on' or 'off'!")
        return
    
    db.set_fsub_mode(mode)
    await message.reply_text(f"✅ Force subscribe mode set to: `{mode}`")


@Client.on_message(filters.command("setstartpic") & filters.private)
@admin_only
async def set_start_picture_command(client, message: Message):
    """Set start picture (admin only)"""
    if message.reply_to_message and message.reply_to_message.photo:
        file_id = message.reply_to_message.photo.file_id
        db.set_start_picture(file_id)
        await message.reply_text("✅ Start picture updated!")
    else:
        await message.reply_text("❌ Please reply to a photo with this command!")


@Client.on_message(filters.command("getstartpic") & filters.private)
@admin_only
async def get_start_picture_command(client, message: Message):
    """Get current start picture (admin only)"""
    pic = db.get_start_picture()
    
    if pic:
        await message.reply_photo(pic, caption="**Current Start Picture**")
    else:
        await message.reply_text("📭 No start picture set!")


@Client.on_message(filters.command("delstartpic") & filters.private)
@admin_only
async def delete_start_picture_command(client, message: Message):
    """Delete start picture (admin only)"""
    db.set_start_picture("")
    await message.reply_text("✅ Start picture removed!")


# ============= User Commands =============

@Client.on_message(filters.command("rename") & filters.private)
async def rename_command(client, message: Message):
    """Rename file command"""
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text(
            "**Rename File**\n\n"
            "Reply to a video/document with:\n"
            "`/rename newfilename.mkv`"
        )
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ Please provide new filename!")
        return
    
    new_name = args[1].strip()
    
    # Download and re-upload with new name
    status = await message.reply_text("📥 Processing...")
    
    try:
        file_path = await message.reply_to_message.download()
        new_path = os.path.join(Config.DOWNLOAD_DIR, new_name)
        os.rename(file_path, new_path)
        
        await status.edit_text("📤 Uploading...")
        
        if message.reply_to_message.video:
            await client.send_video(
                message.chat.id,
                video=new_path,
                caption=f"📝 Renamed to: `{new_name}`"
            )
        else:
            await client.send_document(
                message.chat.id,
                document=new_path,
                caption=f"📝 Renamed to: `{new_name}`"
            )
        
        os.remove(new_path)
        await status.delete()
    
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("mediainfo") & filters.private)
async def mediainfo_command(client, message: Message):
    """Show media information"""
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("❌ Reply to a video/document with this command!")
        return
    
    status = await message.reply_text("🔍 Analyzing media...")
    
    try:
        file_path = await message.reply_to_message.download()
        info = await encoder.get_media_info(file_path)
        
        # Parse information
        format_info = info.get('format', {})
        video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'audio'), None)
        
        text = "**📊 Media Information**\n\n"
        
        # General info
        text += f"**Format:** {format_info.get('format_long_name', 'Unknown')}\n"
        text += f"**Duration:** {format_time(int(float(format_info.get('duration', 0))))}\n"
        text += f"**Size:** {format_size(int(format_info.get('size', 0)))}\n"
        text += f"**Bitrate:** {int(format_info.get('bit_rate', 0)) // 1000} Kbps\n\n"
        
        # Video info
        if video_stream:
            text += "**Video Stream:**\n"
            text += f"├ Codec: {video_stream.get('codec_long_name', 'Unknown')}\n"
            text += f"├ Resolution: {video_stream.get('width')}x{video_stream.get('height')}\n"
            text += f"├ FPS: {eval(video_stream.get('r_frame_rate', '0/1')):.2f}\n"
            text += f"└ Bitrate: {int(video_stream.get('bit_rate', 0)) // 1000} Kbps\n\n"
        
        # Audio info
        if audio_stream:
            text += "**Audio Stream:**\n"
            text += f"├ Codec: {audio_stream.get('codec_long_name', 'Unknown')}\n"
            text += f"├ Channels: {audio_stream.get('channels', 'Unknown')}\n"
            text += f"├ Sample Rate: {audio_stream.get('sample_rate', 'Unknown')} Hz\n"
            text += f"└ Bitrate: {int(audio_stream.get('bit_rate', 0)) // 1000} Kbps\n"
        
        await status.edit_text(text)
        os.remove(file_path)
    
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("setwatermark") & filters.private)
async def set_watermark_command(client, message: Message):
    """Set watermark text"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current = db.get_user_watermark(message.from_user.id)
        await message.reply_text(
            f"**Current Watermark:** `{current}`\n\n"
            "**Usage:** `/setwatermark Your Text Here`"
        )
        return
    
    watermark = args[1].strip()
    db.set_user_watermark(message.from_user.id, watermark)
    await message.reply_text(f"✅ Watermark set to: `{watermark}`")


@Client.on_message(filters.command("getwatermark") & filters.private)
async def get_watermark_command(client, message: Message):
    """Get current watermark"""
    watermark = db.get_user_watermark(message.from_user.id)
    await message.reply_text(f"**Your Watermark:** `{watermark}`")


@Client.on_message(filters.command("setmedia") & filters.private)
async def set_media_type_command(client, message: Message):
    """Set upload media type"""
    buttons = [
        [
            InlineKeyboardButton("📹 Video", callback_data="setmedia_video"),
            InlineKeyboardButton("📄 Document", callback_data="setmedia_document")
        ]
    ]
    
    current = "Document" if db.get_user_setting(message.from_user.id, 'upload_as_document', False) else "Video"
    
    await message.reply_text(
        f"**Current Upload Type:** {current}\n\n"
        "Select upload type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("spoiler") & filters.private)
async def toggle_spoiler_command(client, message: Message):
    """Toggle spoiler mode"""
    current = db.get_user_setting(message.from_user.id, 'spoiler_mode', False)
    new_value = not current
    
    db.set_user_setting(message.from_user.id, 'spoiler_mode', new_value)
    
    status = "enabled" if new_value else "disabled"
    await message.reply_text(f"✅ Spoiler mode {status}!")


print("Handlers module loaded successfully!")
