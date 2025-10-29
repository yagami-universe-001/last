import os
import re
import asyncio
import subprocess
from config import Config
from database import Database

db = Database()


class VideoEncoder:
    """Video encoding class with FFmpeg"""
    
    def __init__(self):
        self.ffmpeg = Config.FFMPEG_PATH
        self.ffprobe = Config.FFPROBE_PATH
    
    async def encode_video(self, input_file, quality, progress_callback=None):
        """
        Encode video to specified quality
        
        Args:
            input_file: Path to input video
            quality: Target quality (144p, 240p, etc.)
            progress_callback: Async callback function for progress updates
        
        Returns:
            Path to encoded video
        """
        # Get quality settings
        preset = Config.QUALITY_PRESETS.get(quality, Config.QUALITY_PRESETS['480p'])
        codec = db.get_codec()
        ffmpeg_preset = db.get_preset()
        crf = db.get_crf()
        audio_bitrate = db.get_audio_bitrate()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{base_name}_{quality}_encoded.mkv"
        )
        
        # Get video duration for progress calculation
        duration = await self.get_duration(input_file)
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-c:v', codec,
            '-preset', ffmpeg_preset,
            '-crf', str(crf),
            '-s', preset['resolution'],
            '-b:v', preset['video_bitrate'],
            '-c:a', 'aac',
            '-b:a', audio_bitrate,
            '-map', '0',
            '-y',
            output_file
        ]
        
        # Run FFmpeg with progress monitoring
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor progress
        if progress_callback:
            asyncio.create_task(
                self._monitor_progress(process, duration, progress_callback)
            )
        
        # Wait for completion
        await process.wait()
        
        if process.returncode != 0:
            stderr = await process.stderr.read()
            raise Exception(f"FFmpeg error: {stderr.decode()}")
        
        return output_file
    
    async def _monitor_progress(self, process, total_duration, callback):
        """Monitor FFmpeg progress and call callback"""
        pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
        
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            
            line = line.decode('utf-8', errors='ignore')
            match = pattern.search(line)
            
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                
                if total_duration > 0:
                    percentage = min((current_time / total_duration) * 100, 100)
                else:
                    percentage = 0
                
                # Extract speed
                speed_match = re.search(r'speed=\s*(\S+)x', line)
                speed = speed_match.group(1) + 'x' if speed_match else '0x'
                
                # Calculate time left
                time_left = self._calculate_time_left(current_time, total_duration, speed)
                
                # Call callback
                if callback:
                    await callback({
                        'percentage': percentage,
                        'current_time': current_time,
                        'total_duration': total_duration,
                        'speed': speed,
                        'time_left': time_left
                    })
    
    def _calculate_time_left(self, current, total, speed_str):
        """Calculate estimated time remaining"""
        try:
            speed = float(speed_str.replace('x', ''))
            if speed > 0:
                remaining = (total - current) / speed
                return self._format_time(int(remaining))
            return "Calculating..."
        except:
            return "Unknown"
    
    def _format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    async def get_duration(self, file_path):
        """Get video duration using FFprobe"""
        cmd = [
            self.ffprobe,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        
        try:
            return float(stdout.decode().strip())
        except:
            return 0
    
    async def get_media_info(self, file_path):
        """Get detailed media information"""
        cmd = [
            self.ffprobe,
            '-v', 'error',
            '-show_format',
            '-show_streams',
            '-print_format', 'json',
            file_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        
        import json
        return json.loads(stdout.decode())
    
    async def compress_video(self, input_file, percentage, progress_callback=None):
        """Compress video by percentage"""
        # Calculate target bitrate
        info = await self.get_media_info(input_file)
        original_bitrate = int(info['format'].get('bit_rate', 1000000))
        target_bitrate = int(original_bitrate * (percentage / 100))
        
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_compressed.mkv"
        )
        
        duration = await self.get_duration(input_file)
        
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-c:v', 'libx264',
            '-b:v', f"{target_bitrate}",
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if progress_callback:
            asyncio.create_task(
                self._monitor_progress(process, duration, progress_callback)
            )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Compression failed")
        
        return output_file
    
    async def add_watermark(self, input_file, watermark_text, progress_callback=None):
        """Add text watermark to video"""
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_watermarked.mkv"
        )
        
        duration = await self.get_duration(input_file)
        
        # Escape special characters in watermark text
        watermark_text = watermark_text.replace("'", "\\'").replace(":", "\\:")
        
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-vf', f"drawtext=text='{watermark_text}':fontcolor=white:fontsize=24:x={Config.WATERMARK_POSITION.split(':')[0]}:y={Config.WATERMARK_POSITION.split(':')[1]}",
            '-c:a', 'copy',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if progress_callback:
            asyncio.create_task(
                self._monitor_progress(process, duration, progress_callback)
            )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Watermark addition failed")
        
        return output_file
    
    async def add_subtitle(self, input_file, subtitle_file, hard=False, progress_callback=None):
        """Add subtitles to video"""
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_subbed.mkv"
        )
        
        duration = await self.get_duration(input_file)
        
        if hard:
            # Hard subtitle (burned in)
            cmd = [
                self.ffmpeg,
                '-i', input_file,
                '-vf', f"subtitles={subtitle_file}",
                '-c:a', 'copy',
                '-y',
                output_file
            ]
        else:
            # Soft subtitle (separate track)
            cmd = [
                self.ffmpeg,
                '-i', input_file,
                '-i', subtitle_file,
                '-c', 'copy',
                '-c:s', 'mov_text',
                '-y',
                output_file
            ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if progress_callback:
            asyncio.create_task(
                self._monitor_progress(process, duration, progress_callback)
            )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Subtitle addition failed")
        
        return output_file
    
    async def extract_audio(self, input_file, progress_callback=None):
        """Extract audio from video as MP3"""
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}.mp3"
        )
        
        duration = await self.get_duration(input_file)
        
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-vn',
            '-acodec', 'libmp3lame',
            '-q:a', '2',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if progress_callback:
            asyncio.create_task(
                self._monitor_progress(process, duration, progress_callback)
            )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Audio extraction failed")
        
        return output_file
    
    async def trim_video(self, input_file, start_time, end_time, progress_callback=None):
        """Trim video between start and end time"""
        output_file = os.path.join(
            Config.ENCODE_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_trimmed.mkv"
        )
        
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-ss', start_time,
            '-to', end_time,
            '-c', 'copy',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Video trimming failed")
        
        return output_file
    
    async def merge_videos(self, input_files, progress_callback=None):
        """Merge multiple videos into one"""
        # Create concat file
        concat_file = os.path.join(Config.ENCODE_DIR, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for file in input_files:
                f.write(f"file '{file}'\n")
        
        output_file = os.path.join(Config.ENCODE_DIR, "merged_video.mkv")
        
        cmd = [
            self.ffmpeg,
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.wait()
        
        # Cleanup
        os.remove(concat_file)
        
        if process.returncode != 0:
            raise Exception("Video merging failed")
        
        return output_file
    
    async def extract_thumbnail(self, input_file, time="00:00:01"):
        """Extract thumbnail from video"""
        output_file = os.path.join(
            Config.THUMB_DIR,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_thumb.jpg"
        )
        
        cmd = [
            self.ffmpeg,
            '-i', input_file,
            '-ss', time,
            '-vframes', '1',
            '-q:v', '2',
            '-y',
            output_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Thumbnail extraction failed")
        
        return output_file
