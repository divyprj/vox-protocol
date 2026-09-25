# ==============================================================================
# VOX//PROTOCOL — Production Container Image
# Multi-stage optimized Python 3.11 runtime for Cloud & On-Premise Voice Studio
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered standard I/O
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies (curl for healthchecks, ffmpeg for audio codecs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source tree
COPY . .

# Ensure storage directories exist with appropriate write permissions
RUN mkdir -p /app/output /app/data /app/data/previews

# Expose default HTTP port
EXPOSE 8000

# Container healthcheck for cloud orchestrators (Railway, Render, ECS, K8s)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Launch production server via unified runner (dynamically binds to $PORT)
CMD ["sh", "-c", "python run_server.py"]
