#!/usr/bin/env python3
"""
Coach Joe Video Processor - Cloud FFmpeg Solution
Handles video processing with audio, video, and image integration
"""

import os
import json
import subprocess
import tempfile
import requests
from datetime import datetime, timedelta
from pathlib import Path
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoachJoeVideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.supported_video_formats = ['.mp4', '.mov', '.avi', '.mkv']
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif']
        self.supported_audio_formats = ['.mp3', '.wav', '.m4a', '.aac']
        
    def download_file(self, url, filename=None):
        """Download file from URL to temp directory"""
        if not filename:
            filename = url.split('/')[-1]
        
        filepath = os.path.join(self.temp_dir, filename)
        
        logger.info(f"Downloading {url} to {filepath}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            raise
    
    def get_audio_duration(self, audio_file):
        """Get audio duration in seconds using FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            logger.info(f"Audio duration: {duration} seconds")
            return duration
        except Exception as e:
            logger.error(f"Failed to get audio duration: {str(e)}")
            return 15.0  # Default fallback
    
    def process_video(self, config):
        """
        Main video processing function
        
        Args:
            config (dict): Processing configuration
                - audio_url: URL to audio file
                - video_urls: List of video URLs
                - image_urls: List of image URLs  
                - video_volume_reduction: Volume reduction percentage (default: 90)
                - output_duration_extra: Extra seconds to add to audio duration (default: 1)
        """
        try:
            # Extract configuration
            audio_url = config.get('audio_url')
            video_urls = config.get('video_urls', [])
            image_urls = config.get('image_urls', [])
            video_volume_reduction = config.get('video_volume_reduction', 90)
            duration_extra = config.get('output_duration_extra', 1)
            
            logger.info("Starting Coach Joe video processing...")
            logger.info(f"Audio URL: {audio_url}")
            logger.info(f"Video URLs: {len(video_urls)} videos")
            logger.info(f"Image URLs: {len(image_urls)} images")
            
            # Download audio file
            audio_file = self.download_file(audio_url, 'coach_joe_audio.mp3')
            audio_duration = self.get_audio_duration(audio_file)
            total_duration = audio_duration + duration_extra
            
            # Download video files
            video_files = []
            for i, url in enumerate(video_urls[:3]):  # Limit to 3 videos
                video_file = self.download_file(url, f'video_{i}.mp4')
                video_files.append(video_file)
            
            # Download image files
            image_files = []
            for i, url in enumerate(image_urls[:2]):  # Limit to 2 images
                image_file = self.download_file(url, f'image_{i}.jpg')
                image_files.append(image_file)
            
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.temp_dir, f'coach_joe_video_{timestamp}.mp4')
            
            # Build and execute FFmpeg command
            ffmpeg_cmd = self.build_ffmpeg_command(
                audio_file=audio_file,
                video_files=video_files,
                image_files=image_files,
                output_file=output_file,
                total_duration=total_duration,
                video_volume_reduction=video_volume_reduction
            )
            
            logger.info("Executing FFmpeg command...")
            logger.info(f"Command: {' '.join(ffmpeg_cmd)}")
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                raise Exception(f"FFmpeg processing failed: {result.stderr}")
            
            logger.info("FFmpeg processing completed successfully")
            
            # Upload to Supabase (or return file path for upload)
            upload_result = self.upload_to_supabase(output_file)
            
            if isinstance(upload_result, dict):
                final_url = upload_result.get('video_url')
                video_data = upload_result.get('video_data')
                upload_ready = upload_result.get('upload_ready', False)
            else:
                final_url = upload_result
                video_data = None
                upload_ready = False
            
            return {
                'success': True,
                'video_url': final_url,
                'video_data': video_data,
                'upload_ready': upload_ready,
                'duration': total_duration,
                'processing_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(output_file),
                'specs': {
                    'resolution': '720x1280',
                    'fps': 30,
                    'format': 'mp4',
                    'audio_codec': 'aac',
                    'video_codec': 'libx264'
                }
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def build_ffmpeg_command(self, audio_file, video_files, image_files, output_file, 
                           total_duration, video_volume_reduction):
        """Build complex FFmpeg command for Coach Joe video processing"""
        
        # Calculate video volume (90% reduction = 10% volume)
        video_volume = (100 - video_volume_reduction) / 100
        
        cmd = ['ffmpeg', '-y']  # -y to overwrite output
        
        # Add inputs
        cmd.extend(['-i', audio_file])  # Input 0: Audio
        
        if video_files:
            cmd.extend(['-i', video_files[0]])  # Input 1: Main video
        
        if image_files:
            cmd.extend(['-i', image_files[0]])  # Input 2: First image
        
        # Build filter complex
        filter_parts = []
        
        # Video processing
        if video_files:
            # Scale and crop video to 9:16 aspect ratio
            filter_parts.append(
                "[1:v]scale=720:1280:force_original_aspect_ratio=increase,"
                "crop=720:1280,setsar=1[bg_video]"
            )
            
            # Add image overlay if available
            if image_files:
                filter_parts.append(
                    "[2:v]scale=200:200[overlay_img]"
                )
                filter_parts.append(
                    "[bg_video][overlay_img]overlay=W-w-20:20:enable='between(t,3,6)'[final_video]"
                )
                video_output = "[final_video]"
            else:
                video_output = "[bg_video]"
        else:
            # No video input - create colored background
            filter_parts.append(
                f"color=black:size=720x1280:duration={total_duration}[final_video]"
            )
            video_output = "[final_video]"
        
        # Audio processing
        if video_files:
            # Mix audio: original voice + reduced video audio
            filter_parts.append(f"[1:a]volume={video_volume}[bg_audio]")
            filter_parts.append(
                "[0:a][bg_audio]amix=inputs=2:duration=first:dropout_transition=0[final_audio]"
            )
            audio_output = "[final_audio]"
        else:
            # Only voice audio
            audio_output = "[0:a]"
        
        # Combine filter parts
        if filter_parts:
            cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # Map outputs
        cmd.extend(['-map', video_output])
        cmd.extend(['-map', audio_output])
        
        # Output settings
        cmd.extend([
            '-t', str(total_duration),  # Duration
            '-c:v', 'libx264',         # Video codec
            '-preset', 'fast',         # Encoding speed
            '-crf', '23',              # Quality (lower = better)
            '-c:a', 'aac',             # Audio codec
            '-b:a', '128k',            # Audio bitrate
            '-r', '30',                # Frame rate
            '-pix_fmt', 'yuv420p',     # Pixel format (compatibility)
            '-movflags', '+faststart', # Web optimization
            output_file
        ])
        
        return cmd
    
    def upload_to_supabase(self, file_path):
        """Upload processed video to Supabase storage"""
        try:
            # Read the processed video file
            with open(file_path, 'rb') as f:
                video_data = f.read()
            
            filename = os.path.basename(file_path)
            
            # For RunPod deployment, we'll return the file data as base64
            # so it can be uploaded by the N8N workflow
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            supabase_url = f"https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/coach-joe-videos/{filename}"
            
            logger.info(f"Video processed successfully: {filename}")
            logger.info(f"File size: {len(video_data)} bytes")
            logger.info(f"Target Supabase URL: {supabase_url}")
            
            return {
                "video_url": supabase_url,
                "video_data": video_base64,
                "filename": filename,
                "file_size": len(video_data),
                "upload_ready": True
            }
            
        except Exception as e:
            logger.error(f"Upload preparation failed: {str(e)}")
            return {
                "video_url": file_path,
                "error": str(e),
                "upload_ready": False
            }
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

# API endpoint function for cloud deployment
def handler(event, context=None):
    """
    Cloud function handler (AWS Lambda, Google Cloud Functions, etc.)
    
    Expected event structure:
    {
        "audio_url": "https://...",
        "video_urls": ["https://..."],
        "image_urls": ["https://..."],
        "video_volume_reduction": 90,
        "output_duration_extra": 1
    }
    """
    processor = CoachJoeVideoProcessor()
    
    try:
        # Process the video
        result = processor.process_video(event)
        
        # Return response
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    finally:
        processor.cleanup()

# Example usage
if __name__ == "__main__":
    # Test configuration
    test_config = {
        "audio_url": "https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/coach-joe-audio/coach-joe-voice-temp.mp3",
        "video_urls": [
            "https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-vids/jump_elastic_1.MP4"
        ],
        "image_urls": [
            "https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-pics/basketball-programs.png"
        ],
        "video_volume_reduction": 90,
        "output_duration_extra": 1
    }
    
    # Process video
    processor = CoachJoeVideoProcessor()
    result = processor.process_video(test_config)
    
    print(json.dumps(result, indent=2))
    
    # Cleanup
    processor.cleanup() 
