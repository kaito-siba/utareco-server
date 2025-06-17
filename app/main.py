"""FastAPI application entry point for UtaReco server."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title="UtaReco API",
    description="Music recognition service using audio fingerprinting",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("DEBUG") else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "UtaReco API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker container monitoring."""
    try:
        # Test Essentia import and basic functionality
        import essentia
        import essentia.standard as es

        # Test basic algorithm instantiation
        windowing = es.Windowing(type="hann")

        return {
            "status": "healthy",
            "essentia_version": essentia.__version__,
            "message": "Essentia operational - windowing algorithm loaded",
        }
    except ImportError as e:
        return {
            "status": "unhealthy",
            "message": f"Essentia library not available: {str(e)}",
        }
    except Exception as e:
        return {"status": "unhealthy", "message": f"Essentia error: {str(e)}"}


@app.get("/info")
async def info() -> dict[str, str]:
    """System information endpoint."""
    return {
        "name": "UtaReco",
        "description": "Music recognition service using audio fingerprinting",
        "version": "0.1.0",
        "python_version": os.sys.version,
        "environment": "development" if os.getenv("DEBUG") else "production",
    }


@app.get("/test-essentia")
async def test_essentia() -> dict[str, str]:
    """Test Essentia algorithms with sample data."""
    try:
        import essentia.standard as es
        import numpy as np

        # Create sample audio data (1 second of 440Hz sine wave)
        sample_rate = 44100
        frequency = 440.0
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)

        # Test windowing
        windowing = es.Windowing(type="hann")
        windowed_frame = windowing(audio_data[:1024])

        # Test spectrum
        spectrum = es.Spectrum()
        spectrum_result = spectrum(windowed_frame)

        # Test spectral centroid
        spectral_centroid = es.SpectralCentroidTime()
        centroid = spectral_centroid(audio_data)

        return {
            "status": "success",
            "message": "Essentia algorithms working correctly",
            "sample_rate": str(sample_rate),
            "test_frequency": str(frequency),
            "spectral_centroid": str(float(centroid)),
            "audio_length": str(len(audio_data)),
            "spectrum_length": str(len(spectrum_result)),
        }
    except Exception as e:
        return {"status": "error", "message": f"Essentia test failed: {str(e)}"}
