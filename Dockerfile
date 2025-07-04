FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Create temp directory for processing
RUN mkdir -p /tmp/ffmpeg_processing

# Set environment variables
ENV PYTHONPATH=/app
ENV TEMP_DIR=/tmp/ffmpeg_processing
ENV RUNPOD_ENDPOINT_ID=coach-joe-ffmpeg

# Expose port for HTTP endpoints
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Create startup script for RunPod
RUN echo '#!/bin/bash\n\
echo "Starting Coach Joe FFmpeg Processor..."\n\
echo "Python path: $PYTHONPATH"\n\
echo "Working directory: $(pwd)"\n\
echo "Files in /app: $(ls -la /app)"\n\
echo "RunPod Endpoint ID: $RUNPOD_ENDPOINT_ID"\n\
python runpod_handler.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Use the startup script as the default command
CMD ["/app/start.sh"] 
