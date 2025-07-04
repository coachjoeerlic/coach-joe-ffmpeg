# 🚀 GitHub to Cloud Deployment Guide

## 📋 **Prerequisites**

1. ✅ GitHub account
2. ✅ Cloud platform account (RunPod/Replicate/Modal)
3. ✅ Supabase credentials
4. ✅ FFmpeg processor files ready

## 🔧 **Step 1: Setup GitHub Repository**

### **1.1 Create Repository**
```bash
# Create new repository on GitHub
# OR clone existing repository
git clone https://github.com/your-username/coach-joe-ffmpeg.git
cd coach-joe-ffmpeg
```

### **1.2 Add Files to Repository**
```bash
# Add all the deployment files
git add .
git commit -m "Initial commit: Coach Joe FFmpeg Processor"
git push origin main
```

### **1.3 Enable GitHub Actions**
- Go to your repository → Settings → Actions → General
- Enable "Allow all actions and reusable workflows"
- Enable "Read and write permissions" for GITHUB_TOKEN

## 🐳 **Step 2: Automatic Docker Build**

GitHub Actions will automatically:
1. ✅ Build Docker image on push to main
2. ✅ Run tests (Python imports, FFmpeg version)
3. ✅ Push to GitHub Container Registry
4. ✅ Create deployment summary

**Container Image**: `ghcr.io/your-username/coach-joe-ffmpeg:latest`

## 🏆 **Step 3: Deploy to RunPod**

### **3.1 Create RunPod Account**
1. Visit [runpod.io](https://runpod.io)
2. Sign up and verify account
3. Get API key from dashboard

### **3.2 Create Serverless Endpoint**
1. Go to **RunPod Console** → **Serverless**
2. Click **"+ New Endpoint"**
3. Configure:
   - **Name**: `coach-joe-ffmpeg`
   - **Container Image**: `ghcr.io/your-username/coach-joe-ffmpeg:latest`
   - **Container Start Command**: `python runpod_handler.py`
   - **Container Disk**: 10GB
   - **CPU**: 4 vCPUs
   - **Memory**: 8GB
   - **GPU**: None (CPU only)
   - **Execution Timeout**: 300 seconds

### **3.3 Environment Variables**
Add these environment variables in RunPod:
```bash
SUPABASE_URL=https://wbrlglamhecvkcbifzls.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

### **3.4 Test Deployment**
```bash
# Test the endpoint
curl -X POST https://api.runpod.ai/v2/YOUR-ENDPOINT-ID/run \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "audio_url": "https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/coach-joe-audio/sample.mp3",
      "video_urls": ["https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-vids/sample.mp4"],
      "image_urls": ["https://wbrlglamhecvkcbifzls.supabase.co/storage/v1/object/public/jump-strength-short-pics/sample.jpg"]
    }
  }'
```

## 🥈 **Alternative: Deploy to Replicate**

### **4.1 Setup Replicate**
```bash
# Install Cog
pip install cog

# Login to Replicate
cog login

# Push model
cog push r8.im/your-username/coach-joe-ffmpeg
```

### **4.2 Test Replicate API**
```python
import replicate

output = replicate.run(
    "your-username/coach-joe-ffmpeg:latest",
    input={
        "audio_url": "https://your-audio-url.mp3",
        "video_urls": "https://video1.mp4,https://video2.mp4",
        "image_urls": "https://image1.jpg"
    }
)
```

## 🥉 **Alternative: Deploy to Modal**

### **5.1 Setup Modal**
```bash
# Install Modal
pip install modal

# Login
modal token set

# Deploy
modal deploy modal_handler.py
```

### **5.2 Test Modal API**
```python
import modal

f = modal.Function.lookup("coach-joe-ffmpeg", "process_coach_joe_video")
result = f.remote({
    "audio_url": "https://your-audio-url.mp3",
    "video_urls": ["https://your-video-url.mp4"],
    "image_urls": ["https://your-image-url.jpg"]
})
```

## 🔧 **Step 4: Update N8N Workflow**

### **4.1 Replace Shotstack Node**
Replace your existing Shotstack node with **HTTP Request** node:

```json
{
  "method": "POST",
  "url": "https://api.runpod.ai/v2/YOUR-ENDPOINT-ID/run",
  "headers": {
    "Authorization": "Bearer YOUR-RUNPOD-API-KEY",
    "Content-Type": "application/json"
  },
  "body": {
    "input": {
      "audio_url": "{{ $('ElevenLabs Voice Generator').first().json.audio_url }}",
      "video_urls": ["{{ $('Select Best Media').first().json.selected_videos[0].url }}"],
      "image_urls": ["{{ $('Select Best Media').first().json.selected_images[0].url }}"],
      "video_volume_reduction": 90,
      "output_duration_extra": 1
    }
  }
}
```

### **4.2 Handle Response**
The response will include:
- `video_url`: Direct URL to processed video
- `video_data`: Base64 encoded video data
- `upload_ready`: Boolean indicating if ready for upload
- `duration`: Video duration in seconds
- `specs`: Video specifications

## 📊 **Step 5: Monitor and Scale**

### **5.1 Monitor Performance**
- RunPod Dashboard → Endpoint Analytics
- Check processing times, success rates
- Monitor costs per execution

### **5.2 Scale if Needed**
- Increase CPU/Memory allocation
- Enable auto-scaling
- Add multiple endpoints for load balancing

## 🐛 **Troubleshooting**

### **Common Issues**
1. **Container fails to start**: Check logs in RunPod console
2. **Audio/video not found**: Verify Supabase URLs and permissions
3. **FFmpeg errors**: Check input file formats
4. **Timeout errors**: Increase execution timeout

### **Debug Commands**
```bash
# Local testing
docker run -p 8080:8080 ghcr.io/your-username/coach-joe-ffmpeg:latest

# Test health endpoint
curl http://localhost:8080/health

# Test processing
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

## 🎉 **Success Checklist**

- [ ] GitHub repository created
- [ ] Docker image built automatically
- [ ] RunPod endpoint deployed
- [ ] Test API call successful
- [ ] N8N workflow updated
- [ ] First video processed with audio
- [ ] Monitoring setup complete

## 📈 **Expected Results**

✅ **Processing Time**: 20-30 seconds per video  
✅ **Success Rate**: 95%+ with proper inputs  
✅ **Cost**: ~$0.03-0.05 per video  
✅ **Quality**: 720x1280, 30fps, perfect audio  
✅ **Scalability**: Handle 10+ concurrent videos  

---

**🎬 Your Coach Joe videos will now have perfect audio! 🎵** 
