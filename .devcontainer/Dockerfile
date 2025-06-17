# Use official Essentia Docker image as base
FROM ghcr.io/mtg/essentia:nightly

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install development dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    git \
    vim \
    nano \
    sudo \
    zsh \
    wget \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv package manager
RUN python3 -m pip install uv

# Create symlink for Essentia to be accessible from Python 3.10
RUN ln -sf /usr/local/lib/python3/dist-packages/essentia /usr/local/lib/python3.10/dist-packages/essentia

# Install Python development dependencies directly to system Python
RUN PYTHONPATH="/usr/local/lib/python3/dist-packages" python3 -m pip install \
    fastapi \
    sqlalchemy \
    pytest \
    pyright \
    ruff \
    pytest-cov \
    httpx \
    "uvicorn[standard]" \
    python-multipart \
    anyio \
    numpy \
    pydantic \
    ipython \
    jupyter \
    black \
    isort

# Create directory for audio files
RUN mkdir -p /app/audio_files

# Set the Python path to include Essentia location
ENV PYTHONPATH="/app:/usr/local/lib/python3/dist-packages"

# Expose port for FastAPI
EXPOSE 8000

# Keep container running for development
CMD ["sleep", "infinity"]