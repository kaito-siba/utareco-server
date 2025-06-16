# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UtaReco is a music recognition system that analyzes audio fingerprints to identify songs. The system uses HPCP (Harmonic Pitch Class Profiles) features and Essentia for audio processing, with a FastAPI backend for serving queries.

## Development Commands

### Environment Setup
```bash
# Initialize project with uv
uv init

# Install dependencies
uv add essentia fastapi sqlalchemy[sqlite] pytest pyright ruff

# All Python commands must be run through uv
uv run python <script>
uv run pytest
```

### Quality Checks
```bash
# Linting and formatting
ruff check
ruff format

# Type checking
pyright

# Run tests with coverage
uv run pytest --cov
```

### Development Workflow
- **Test First**: Always write failing tests before implementation (TDD)
- **Incremental**: Complete one feature phase before moving to the next
- **Quality**: Run linting, type checking, and tests before commits

## Architecture Overview

### Core Components
1. **Audio Processing Pipeline**: Essentia-based HPCP feature extraction
2. **Database Layer**: SQLAlchemy with SQLite for recordings and features
3. **API Layer**: FastAPI with Pydantic models for audio queries
4. **Matching Engine**: Chromatic similarity algorithms with transposition tolerance

### Database Schema
- `recordings`: Audio file metadata and storage paths
- `hpcp_features`: Extracted HPCP feature vectors (BLOB/JSON storage)

### Development Phases (from README.md)
1. **Database & Import CLI**: File import and HPCP extraction
2. **Query API**: FastAPI endpoints for audio upload and processing  
3. **Matching Logic**: Similarity calculation and candidate ranking
4. **Results & Operations**: Response formatting and monitoring

## Coding Standards

### Python Style
- Use single quotes for strings (except docstrings)
- Python 3.11+ features and built-in types for type hints
- `snake_case` for variables, `UpperCamelCase` for classes/functions
- `lowerCamelCase` for methods
- Trailing commas in multi-line collections
- Exception variable naming: `ex` for logging with `exc_info=ex`
- Use `pathlib` instead of `os.path`
- Empty line after docstrings

### FastAPI Conventions
- Endpoint functions: `UpperCamelCase`
- Endpoint naming: `NounVerbAPI` (e.g., `UserUpdateAPI`)
- Pydantic models for request/response validation

### Testing (TDD Required)
- Write failing tests first, then minimal implementation
- Focus on business behavior, not implementation details
- Test granularity: User/system behavior level
- Example: "When user uploads audio file, HPCP features are extracted and stored"

### Code Quality
- Extensive commenting for readability
- Preserve existing comments unless they contradict changes  
- English-only log messages to prevent encoding issues
- Half-width spaces between English words and Japanese text
- Comprehensive type hints with return types

### Error Handling
- Use `logging` with `exc_info=ex` for detailed error context
- Fallback to `traceback.print_exc()` when logging unavailable
- Web search for similar issues when debugging

## Important Constraints

- **No unauthorized changes**: Get approval before modifying technology stack versions
- **No UI/UX changes**: Must get explicit approval for design modifications  
- **Preserve comments**: Keep existing comments unless they become incorrect
- **Python execution**: Always use `uv run python` instead of direct `python`
- **Directory structure**: Follow planned architecture from README phases

## File Organization

Currently project contains only documentation. Expected structure:
```
/
├── src/utareco/          # Main application code
├── tests/                # Test files (mirrors src structure)
├── data/                 # Sample audio files and test data
├── migrations/           # Database schema migrations
└── docs/                 # API documentation
```

## Technology Stack

- **Audio Processing**: Essentia (HPCP extraction, preprocessing)
- **Backend**: FastAPI + Pydantic (API layer)
- **Database**: SQLAlchemy + SQLite (recordings, features)
- **Testing**: pytest + coverage
- **Code Quality**: ruff (lint/format) + pyright (types)
- **Package Management**: uv (replaces pip/poetry)
- **Deployment**: Docker + GitHub Actions (planned)

## Development Notes

- Follow the 5-phase development plan outlined in README.md
- Each phase should be completed with full test coverage before proceeding
- Panako integration is deferred to later phases
- All audio processing should handle WAV/MP3 formats
- Consider parallel processing and caching for similarity calculations