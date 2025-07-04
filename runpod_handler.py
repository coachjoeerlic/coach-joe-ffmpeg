#!/usr/bin/env python3
"""
RunPod Serverless Handler for Coach Joe FFmpeg Processor
"""

import runpod
import json
import logging
from datetime import datetime
from coach_joe_ffmpeg_processor import CoachJoeVideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """
    RunPod serverless handler for video processing
    
    Expected input format:
    {
        "audio_url": "https://...",
        "video_urls": ["https://...", "https://..."],
        "image_urls": ["https://...", "https://..."],
        "video_volume_reduction": 90,
        "output_duration_extra": 1
    }
    """
    
    logger.info("Starting RunPod FFmpeg processing...")
    logger.info(f"Event: {json.dumps(event, indent=2)}")
    
    # Handle health check requests
    if event.get('input', {}).get('health_check'):
        logger.info("Health check request received")
        return {
            'success': True,
            'status': 'healthy',
            'service': 'coach-joe-ffmpeg',
            'timestamp': datetime.now().isoformat()
        }
    
    processor = CoachJoeVideoProcessor()
    
    try:
        # Validate required input
        input_data = event.get('input', {})
        if not input_data.get('audio_url'):
            raise ValueError("audio_url is required")
        
        # Process the video
        result = processor.process_video(input_data)
        
        logger.info("Processing completed successfully")
        logger.info(f"Result: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    
    finally:
        # Clean up temporary files
        processor.cleanup()

# Health check endpoint for container
def health_check():
    """Simple health check"""
    return {"status": "healthy", "service": "coach-joe-ffmpeg"}

if __name__ == "__main__":
    # Check if running in RunPod environment
    import os
    if os.getenv("RUNPOD_ENDPOINT_ID"):
        logger.info("Starting RunPod serverless handler...")
        runpod.serverless.start({"handler": handler})
    else:
        # Run as Flask app for local testing
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify(health_check())
        
        @app.route('/process', methods=['POST'])
        def process():
            try:
                data = request.json
                event = {"input": data}
                result = handler(event)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        logger.info("Starting Flask app for local testing...")
        app.run(host='0.0.0.0', port=8080, debug=True) 
