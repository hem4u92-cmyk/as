import os
import subprocess
import asyncio
from typing import Optional, List
from pathlib import Path


class VideoProcessor:
    """Service for video processing using FFmpeg and MoviePy"""
    
    def __init__(self, output_dir: str = "processed"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("frames", exist_ok=True)
        os.makedirs("audio", exist_ok=True)
    
    async def download_youtube(self, url: str, session_id: str) -> str:
        """Download video from YouTube using yt-dlp"""
        output_path = f"uploads/{session_id}_video.mp4"
        
        try:
            # Use yt-dlp to download
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", output_path,
                "--no-playlist",
                url,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"YouTube download failed: {stderr.decode()}")
            
            return output_path
        
        except FileNotFoundError:
            raise Exception("yt-dlp not found. Please install it: pip install yt-dlp")
        except Exception as e:
            raise Exception(f"YouTube download failed: {str(e)}")
    
    async def extract_audio(self, video_path: str, session_id: str) -> str:
        """Extract audio from video file"""
        audio_path = f"audio/{session_id}_audio.wav"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        try:
            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # PCM codec
                "-ar", "16000",  # 16kHz sample rate (good for Whisper)
                "-ac", "1",  # Mono
                audio_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Audio extraction failed: {stderr.decode()}")
            
            return audio_path
        
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please install FFmpeg.")
        except Exception as e:
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    async def extract_frames(
        self,
        video_path: str,
        session_id: str,
        fps: float = 1.0,
        max_frames: int = 50,
    ) -> List[str]:
        """
        Extract key frames from video
        
        Args:
            video_path: Path to video file
            session_id: Session identifier
            fps: Frames per second to extract (default: 1)
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of paths to extracted frames
        """
        frames_dir = f"frames/{session_id}"
        os.makedirs(frames_dir, exist_ok=True)
        
        try:
            # First, get video duration
            duration_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *duration_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            duration = float(stdout.decode().strip())
            
            # Calculate number of frames
            num_frames = min(int(duration * fps), max_frames)
            if num_frames < 1:
                num_frames = 1
            
            # Calculate interval between frames
            interval = duration / num_frames if num_frames > 0 else 1
            
            # Extract frames at regular intervals
            frame_paths = []
            
            for i in range(num_frames):
                timestamp = i * interval
                frame_path = f"{frames_dir}/frame_{i:04d}.jpg"
                
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-ss", f"{timestamp:.3f}",
                    "-i", video_path,
                    "-vframes", "1",
                    "-q:v", "2",  # High quality
                    frame_path,
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                _, stderr = await process.communicate()
                
                if process.returncode == 0 and os.path.exists(frame_path):
                    frame_paths.append(frame_path)
            
            return frame_paths
        
        except FileNotFoundError:
            raise Exception("FFmpeg/FFprobe not found. Please install FFmpeg.")
        except Exception as e:
            raise Exception(f"Frame extraction failed: {str(e)}")
    
    async def get_video_info(self, video_path: str) -> dict:
        """Get video metadata"""
        try:
            cmd = [
                "ffprobe",
                "-v", "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                import json
                return json.loads(stdout.decode())
            else:
                return {}
        
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}
    
    def cleanup_session(self, session_id: str, keep_video: bool = False):
        """Clean up temporary files for a session"""
        import shutil
        
        # Remove frames
        frames_dir = f"frames/{session_id}"
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        
        # Remove audio
        audio_path = f"audio/{session_id}_audio.wav"
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Optionally remove video
        if not keep_video:
            # Find and remove uploaded video
            uploads_dir = "uploads"
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    if filename.startswith(session_id):
                        os.remove(os.path.join(uploads_dir, filename))
