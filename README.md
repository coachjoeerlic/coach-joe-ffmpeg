# 🎬 Coach Joe FFmpeg Processor

A cloud-native video processing service for Coach Joe fitness videos with ElevenLabs audio integration, designed to replace Shotstack due to audio URL restrictions.

## 🚀 **Features**

✅ **ElevenLabs Integration**: Process MP3 audio from ElevenLabs  
✅ **Supabase Storage**: Direct access to video/image buckets  
✅ **Audio Ducking**: Reduce background video volume by 90%  
✅ **Smart Timing**: Match video duration to audio + 1 second  
✅ **Image Overlays**: Add images at 3-6 second timestamps  
✅ **Multi-Platform**: Deploy to RunPod, Replicate, Modal, or Docker  
✅ **Cost Effective**: ~$0.03-0.05 per video processing  

## 📦 **Quick Start**

### 1. **Local Development**
```bash
# Clone repository
git clone https://github.com/your-username/coach-joe-ffmpeg.git
cd coach-joe-ffmpeg

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS

# Run locally
python runpod_handler.py
```

### 2. **Docker Development**
```bash
# Build and run
docker-compose up --build

# Test endpoint
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://your-audio-file.mp3",
    "video_urls": ["https://your-video-file.mp4"],
    "image_urls": ["https://your-image-file.jpg"]
  }'
```

## 🎯 **Deployment Options**

### **🏆 Option 1: RunPod (Recommended)**

1. **Create RunPod Account**: [runpod.io](https://runpod.io)
2. **Deploy Container**:
   ```bash
   # Use pre-built image
   ghcr.io/your-username/coach-joe-ffmpeg:latest
   
   # Or build from source
   docker build -t coach-joe-ffmpeg .
   docker tag coach-joe-ffmpeg your-registry/coach-joe-ffmpeg
   docker push your-registry/coach-joe-ffmpeg
   ```

3. **Create Serverless Endpoint**:
   - Go to RunPod Console → Serverless
   - Create new endpoint
   - Use container image: `ghcr.io/your-username/coach-joe-ffmpeg:latest`
   - Set handler: `runpod_handler.py`
   - Configure: 4 CPUs, 8GB RAM

4. **Test Deployment**:
   ```bash
   curl -X POST https://api.runpod.ai/v2/your-endpoint-id/run \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "input": {
         "audio_url": "https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/coach-joe-audio/sample.mp3",
         "video_urls": ["https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-vids/sample.mp4"],
         "image_urls": ["https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-pics/sample.jpg"]
       }
     }'
   ```

### **🥈 Option 2: Replicate**

1. **Install Cog**: `pip install cog`
2. **Deploy**: `cog push r8.im/your-username/coach-joe-ffmpeg`
3. **Use API**:
   ```python
   import replicate
   
   output = replicate.run(
       "your-username/coach-joe-ffmpeg",
       input={
           "audio_url": "https://your-audio-file.mp3",
           "video_urls": "https://video1.mp4,https://video2.mp4",
           "image_urls": "https://image1.jpg"
       }
   )
   ```

### **🥉 Option 3: Modal**

1. **Install Modal**: `pip install modal`
2. **Deploy**: `modal deploy modal_handler.py`
3. **Use Function**:
   ```python
   import modal
   
   f = modal.Function.lookup("coach-joe-ffmpeg", "process_coach_joe_video")
   result = f.remote({
       "audio_url": "https://your-audio-file.mp3",
       "video_urls": ["https://your-video-file.mp4"],
       "image_urls": ["https://your-image-file.jpg"]
   })
   ```

## 🔧 **N8N Integration**

Replace your Shotstack node with this HTTP Request configuration:

```json
{
  "method": "POST",
  "url": "https://api.runpod.ai/v2/your-endpoint-id/run",
  "headers": {
    "Authorization": "Bearer YOUR_RUNPOD_API_KEY",
    "Content-Type": "application/json"
  },
  "body": {
    "input": {
      "audio_url": "{{ $('ElevenLabs Voice').first().json.audio_url }}",
      "video_urls": ["{{ $('Select Media').first().json.selected_videos[0].url }}"],
      "image_urls": ["{{ $('Select Media').first().json.selected_images[0].url }}"],
      "video_volume_reduction": 90,
      "output_duration_extra": 1
    }
  }
}
```

## 🎵 **Processing Pipeline**

1. **Download Assets**: Audio (MP3), Videos (MP4), Images (JPG/PNG)
2. **Get Audio Duration**: Using FFprobe
3. **Calculate Timeline**: Audio duration + 1 second
4. **FFmpeg Processing**:
   - Scale video to 720x1280 (9:16 aspect ratio)
   - Reduce background video volume by 90%
   - Add image overlays at 3-6 seconds
   - Mix audio tracks (Coach Joe + background)
   - Export at 30fps, H.264 codec

## 📊 **API Response Format**

```json
{
  "success": true,
  "video_url": "https://supabase.co/storage/.../processed_video.mp4",
  "video_data": "base64_encoded_video_data",
  "upload_ready": true,
  "duration": 16.5,
  "processing_time": "2023-12-01T12:30:45Z",
  "file_size": 2048576,
  "specs": {
    "resolution": "720x1280",
    "fps": 30,
    "format": "mp4",
    "audio_codec": "aac",
    "video_codec": "libx264"
  }
}
```

## 🛠️ **Environment Variables**

```bash
# Required for Supabase integration
SUPABASE_URL=https://wbrlglamhecvkcbifzls.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Optional for RunPod
RUNPOD_ENDPOINT_ID=your-endpoint-id
RUNPOD_API_KEY=your-api-key
```

## 📈 **Performance & Costs**

| Platform | Cost per Video | Processing Time | Concurrent |
|----------|---------------|-----------------|------------|
| RunPod   | ~$0.03-0.05   | 20-30 seconds   | 10+        |
| Replicate| ~$0.02-0.04   | 25-35 seconds   | 5+         |
| Modal    | ~$0.04-0.06   | 15-25 seconds   | 10+        |

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Audio not found**: Check Supabase URL and permissions
2. **FFmpeg error**: Verify video/image formats are supported
3. **Memory issues**: Increase container memory allocation
4. **Timeout**: Increase processing timeout for longer videos

### **Debug Mode**

```bash
# Run with debug logging
PYTHON_LOG_LEVEL=DEBUG python runpod_handler.py
```

### **Test Endpoints**

```bash
# Health check
curl http://localhost:8080/health

# Process test video
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

## 🚀 **GitHub Actions Deployment**

This repository includes automated deployment via GitHub Actions:

1. **Push to main** → Auto-build Docker image
2. **Container Registry** → `ghcr.io/your-username/coach-joe-ffmpeg`
3. **Deploy** → Ready for RunPod/Replicate/Modal

## 🎉 **Success Migration from Shotstack**

✅ **Problem Solved**: No more 403 audio errors  
✅ **Cost Reduced**: From $29/month to $0.05/video  
✅ **Full Control**: Custom effects, timing, overlays  
✅ **Scalable**: Handle multiple videos concurrently  
✅ **Reliable**: Direct Supabase integration  

## 📚 **Additional Resources**

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [RunPod Serverless Guide](https://docs.runpod.io/serverless/overview)
- [N8N HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Supabase Storage API](https://supabase.com/docs/reference/javascript/storage)

---

**Ready to process Coach Joe videos with perfect audio! 🎬🎵**
