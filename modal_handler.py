#!/usr/bin/env python3
"""
Modal.com Handler for Coach Joe FFmpeg Processor
"""

import modal
import json
from datetime import datetime

# Create Modal app
app = modal.App("coach-joe-ffmpeg")

# Define the image with FFmpeg and Python dependencies
image = (
    modal.Image.debian_slim()
    .apt_install("ffmpeg", "curl")
    .pip_install("requests==2.31.0")
    .copy_local_file("coach_joe_ffmpeg_processor.py", "/app/coach_joe_ffmpeg_processor.py")
)

@app.function(
    image=image,
    cpu=4,
    memory=8192,
    timeout=300,  # 5 minutes
    allow_concurrent_inputs=10
)
def process_coach_joe_video(config):
    """
    Modal function for Coach Joe video processing
    
    Args:
        config (dict): Processing configuration
            - audio_url: URL to audio file
            - video_urls: List of video URLs
            - image_urls: List of image URLs
            - video_volume_reduction: Volume reduction percentage (default: 90)
            - output_duration_extra: Extra seconds to add to audio duration (default: 1)
    
    Returns:
        dict: Processing result with video URL and metadata
    """
    
    import sys
    sys.path.append("/app")
    
    from coach_joe_ffmpeg_processor import CoachJoeVideoProcessor
    
    processor = CoachJoeVideoProcessor()
    
    try:
        result = processor.process_video(config)
        return result
    finally:
        processor.cleanup()

# Web endpoint for HTTP requests
@app.function(
    image=image,
    cpu=2,
    memory=4096
)
@modal.web_endpoint(method="POST")
def process_video_endpoint(request):
    """
    HTTP endpoint for video processing
    """
    import json
    
    try:
        # Parse JSON body
        config = json.loads(request.body)
        
        # Process the video
        result = process_coach_joe_video.remote(config)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

# Health check endpoint
@app.function(image=image)
@modal.web_endpoint(method="GET")
def health_check():
    """Health check endpoint"""
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "healthy",
            "service": "coach-joe-ffmpeg",
            "timestamp": datetime.now().isoformat()
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }

if __name__ == "__main__":
    # For local development
    print("Modal app defined. Deploy with: modal deploy modal_handler.py") 
