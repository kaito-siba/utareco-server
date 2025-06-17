# Use official Essentia Docker image as base
FROM ghcr.io/mtg/essentia:nightly

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install additional system dependencies for FastAPI and Python pip
RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv package manager
RUN python3 -m pip install uv

# Copy Python project configuration
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Create directory for audio files
RUN mkdir -p /app/audio_files

# Expose port for FastAPI
EXPOSE 8000

# Set the Python path to include Essentia location
ENV PYTHONPATH="/app:/usr/local/lib/python3/dist-packages"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD PYTHONPATH="/app:/usr/local/lib/python3/dist-packages" curl -f http://localhost:8000/health || exit 1

# Create symlink for Essentia to be accessible from Python 3.10
RUN ln -sf /usr/local/lib/python3/dist-packages/essentia /usr/local/lib/python3.10/dist-packages/essentia

# Install dependencies directly to system Python
RUN PYTHONPATH="/usr/local/lib/python3/dist-packages" python3 -m pip install fastapi sqlalchemy pytest pyright ruff pytest-cov httpx "uvicorn[standard]" python-multipart anyio numpy pydantic

# Run the application using system Python with correct path
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]