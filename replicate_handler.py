#!/usr/bin/env python3
"""
Replicate.com Handler for Coach Joe FFmpeg Processor
"""

import cog
from coach_joe_ffmpeg_processor import CoachJoeVideoProcessor

class Predictor(cog.Predictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        self.processor = CoachJoeVideoProcessor()
    
    def predict(
        self,
        audio_url: str = cog.Input(description="URL to Coach Joe audio file from ElevenLabs"),
        video_urls: str = cog.Input(description="Comma-separated video URLs from Supabase"),
        image_urls: str = cog.Input(description="Comma-separated image URLs from Supabase", default=""),
        video_volume_reduction: int = cog.Input(description="Video volume reduction percentage (0-100)", default=90, ge=0, le=100),
        output_duration_extra: int = cog.Input(description="Extra seconds to add to audio duration", default=1, ge=0, le=10)
    ) -> dict:
        """
        Process Coach Joe video with FFmpeg combining audio, video, and images
        
        Returns processed video with:
        - Coach Joe voice at 100% volume
        - Background video at reduced volume (default 10%)
        - Image overlays at 3-6 second timestamps
        - Total duration = audio duration + extra seconds
        """
        
        config = {
            "audio_url": audio_url,
            "video_urls": video_urls.split(",") if video_urls else [],
            "image_urls": image_urls.split(",") if image_urls else [],
            "video_volume_reduction": video_volume_reduction,
            "output_duration_extra": output_duration_extra
        }
        
        try:
            result = self.processor.process_video(config)
            return result
        finally:
            self.processor.cleanup() 
