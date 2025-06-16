# 🏗️ CLAUDE.md - Claude Code Global Configuration

This file provides guidance to Claude Code (claude.ai/code) when working across all projects.

## 📋 Overview

This is my global Claude Code configuration directory (`~/.claude`) that sets up:

- Professional development standards and workflows
- Language-specific best practices (Python, Bash)
- Permission rules for tool usage
- Environment variables for development
- Session history and todo management

## Project Overview

UtaReco (歌レコ) is a music recognition/matching service using audio fingerprinting technology. The service analyzes audio recordings using Harmonic Pitch Class Profile (HPCP) features extracted with the Essentia library to match query audio against a database of known recordings.

## Development Commands

### Project Initialization (Phase 1)

```bash
# Initialize Python project with uv
uv init

# Add dependencies
uv add essentia fastapi "sqlalchemy[sqlite]" pytest pyright ruff pytest-cov httpx

# Add development dependencies
uv add --dev pytest-asyncio pytest-mock
```

### Code Quality Commands

```bash
# Format code
uv run --frozen ruff format .

# Lint code
uv run --frozen ruff check . --fix

# Type check
uv run --frozen pyright

# Run tests with coverage
uv run --frozen pytest --cov

# Run all quality checks (use before committing)
uv run --frozen ruff format . && uv run --frozen ruff check . && uv run --frozen pyright && uv run --frozen pytest --cov
```

### Development Server

```bash
# Run FastAPI development server
uv run --frozen uvicorn app.main:app --reload

# Run with specific host/port
uv run --frozen uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations

```bash
# Initialize database
uv run --frozen python -m app.cli.init_db

# Import audio files to database
uv run --frozen python -m app.cli.import_audio --directory /path/to/audio/files
```

## Architecture Overview

### Project Structure

```
utareco-server/
├── app/
│   ├── api/              # FastAPI endpoints
│   │   └── v1/          # API version 1
│   ├── core/            # Core business logic
│   │   ├── audio/       # Audio processing (HPCP extraction)
│   │   └── matching/    # Similarity calculation logic
│   ├── db/              # Database models and operations
│   │   ├── models.py    # SQLAlchemy models
│   │   └── crud.py      # Database operations
│   ├── schemas/         # Pydantic models for API
│   ├── cli/             # Command-line interfaces
│   └── main.py          # FastAPI application entry point
├── tests/               # Test files (mirror app structure)
├── pyproject.toml       # Project configuration
└── docker-compose.yml   # Docker configuration
```

### Key Components

1. **Audio Processing Pipeline**

   - Audio file loading and validation
   - Resampling to consistent sample rate (44.1kHz)
   - HPCP feature extraction using Essentia
   - Feature vector storage in SQLite database

2. **Matching System**

   - Query audio HPCP extraction
   - Similarity calculation using ChromaCrossSimilarity or CoverSongSimilarity
   - Optimal transposition index (OTI) for key-invariant matching
   - Threshold-based match determination (default: 0.8)

3. **API Design**

   - RESTful API with FastAPI
   - File upload endpoint for query audio
   - Asynchronous processing support
   - Comprehensive error handling and validation

4. **Database Schema**
   - `recordings`: Stores original audio file metadata
   - `hpcp_features`: Stores extracted HPCP feature vectors as BLOB/JSON

## Development Workflow

### Test-Driven Development (TDD)

Always write tests first:

```python
# 1. Write failing test
def test_extract_hpcp_returns_expected_shape():
    audio = generate_test_audio()
    hpcp = extract_hpcp(audio)
    assert hpcp.shape[1] == 12  # 12 pitch classes

# 2. Implement minimal code to pass
def extract_hpcp(audio):
    # Implementation
```

### Phase-Based Development

Follow the README.md phases strictly:

1. **Phase 1**: Environment setup and project structure
2. **Phase 2**: Audio fingerprint database registration
3. **Phase 3**: Query audio processing API
4. **Phase 4**: Matching logic implementation
5. **Phase 5**: Results presentation and deployment

### API Endpoint Patterns

```python
# Standard endpoint structure
@router.post("/query", response_model=QueryResponse)
async def query_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> QueryResponse:
    # Validation
    # Processing
    # Response
```

## Important Technical Details

### Audio Processing

- **Sample Rate**: Always resample to 44.1kHz for consistency
- **HPCP Parameters**: Use Essentia defaults with `oti=True` for key invariance
- **Feature Storage**: Store as numpy arrays serialized to BLOB

### Performance Considerations

- Consider parallel processing for large database comparisons
- Implement caching for frequently queried audio
- Use database indices on recording metadata

### Error Handling

- Always validate audio file formats (WAV, MP3)
- Handle Essentia processing errors gracefully
- Provide meaningful error messages in API responses

### Testing Strategy

- Unit tests for each component
- Integration tests for API endpoints
- Mock external dependencies (file system, database)
- Use pytest fixtures for test data

## CI/CD Configuration

GitHub Actions workflow should include:

```yaml
- ruff format --check
- ruff check
- pyright
- pytest --cov --cov-report=xml
- docker build test
```

## 🧠 Proactive AI Assistance

### YOU MUST: Always Suggest Improvements

**Every interaction should include proactive suggestions to save engineer time**

1. **Pattern Recognition**

   - Identify repeated code patterns and suggest abstractions
   - Detect potential performance bottlenecks before they matter
   - Recognize missing error handling and suggest additions
   - Spot opportunities for parallelization or caching

2. **Code Quality Improvements**

   - Suggest more idiomatic approaches for the language
   - Recommend better library choices based on project needs
   - Propose architectural improvements when patterns emerge
   - Identify technical debt and suggest refactoring plans

3. **Time-Saving Automations**

   - Create scripts for repetitive tasks observed
   - Generate boilerplate code with full documentation
   - Set up GitHub Actions for common workflows
   - Build custom CLI tools for project-specific needs

4. **Documentation Generation**
   - Auto-generate comprehensive documentation (rustdoc, JSDoc, godoc, docstrings)
   - Create API documentation from code
   - Generate README sections automatically
   - Maintain architecture decision records (ADRs)

### Proactive Suggestion Format

```
💡 **Improvement Suggestion**: [Brief title]
**Time saved**: ~X minutes per occurrence
**Implementation**: [Quick command or code snippet]
**Benefits**: [Why this improves the codebase]
```

## 🎯 Development Philosophy

### Core Principles

- **Engineer time is precious** - Automate everything possible
- **Quality without bureaucracy** - Smart defaults over process
- **Proactive assistance** - Suggest improvements before asked
- **Self-documenting code** - Generate docs automatically
- **Continuous improvement** - Learn from patterns and optimize

## 📚 AI Assistant Guidelines

### Efficient Professional Workflow

**Smart Explore-Plan-Code-Commit with time-saving automation**

#### 1. EXPLORE Phase (Automated)

- **Use AI to quickly scan and summarize codebase**
- **Auto-identify dependencies and impact areas**
- **Generate dependency graphs automatically**
- **Present findings concisely with actionable insights**

#### 2. PLAN Phase (AI-Assisted)

- **Generate multiple implementation approaches**
- **Auto-create test scenarios from requirements**
- **Predict potential issues using pattern analysis**
- **Provide time estimates for each approach**

#### 3. CODE Phase (Accelerated)

- **Generate boilerplate with full documentation**
- **Auto-complete repetitive patterns**
- **Real-time error detection and fixes**
- **Parallel implementation of independent components**
- **Auto-generate comprehensive comments explaining complex logic**

#### 4. COMMIT Phase (Automated)

```bash
# Language-specific quality checks
cargo fmt && cargo clippy && cargo test  # Rust
go fmt ./... && golangci-lint run && go test ./...  # Go
npm run precommit  # TypeScript
uv run --frozen ruff format . && uv run --frozen ruff check . && uv run --frozen pytest  # Python
```

### Documentation & Code Quality Requirements

- **YOU MUST: Generate comprehensive documentation for every function**
- **YOU MUST: Add clear comments explaining business logic**
- **YOU MUST: Create examples in documentation**
- **YOU MUST: Auto-fix all linting/formatting issues**
- **YOU MUST: Generate unit tests for new code**

## 🐍 Python Development

### Core Rules

- **Package Manager**: ONLY use `uv`, NEVER `pip`
- **Type Hints**: Required for all functions
- **Async**: Use `anyio` for testing, not `asyncio`
- **Line Length**: 88 characters maximum

### Code Quality Tools

```bash
# Format code
uv run --frozen ruff format .

# Lint code
uv run --frozen ruff check . --fix

# Type check
uv run --frozen pyright

# Run tests
uv run --frozen pytest --cov

# Security check
uv run --frozen bandit -r .
```

### Documentation Template (Python)

```python
def function_name(param: ParamType) -> ReturnType:
    """Brief description of the function.

    Detailed explanation of what the function does and why.

    Args:
        param: Description of the parameter and its purpose.

    Returns:
        Description of what is returned and its structure.

    Raises:
        ErrorType: When this specific error condition occurs.

    Example:
        >>> result = function_name("input")
        >>> print(result)
        'expected output'

    Note:
        Any important notes about usage or limitations.
    """
    # Implementation
```

### Best Practices

- **Virtual Environments**: Always use venv or uv
- **Dependencies**: Pin versions in requirements
- **Testing**: Use pytest with fixtures
- **Type Narrowing**: Explicit None checks for Optional

## 🐚 Bash Development

### Core Rules

- **Shebang**: Always `#!/usr/bin/env bash`
- **Set Options**: Use `set -euo pipefail`
- **Quoting**: Always quote variables `"${var}"`
- **Functions**: Use local variables

### Best Practices

```bash
#!/usr/bin/env bash
set -euo pipefail

# Global variables in UPPERCASE
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Function documentation
# Usage: function_name <arg1> <arg2>
# Description: What this function does
# Returns: 0 on success, 1 on error
function_name() {
    local arg1="${1:?Error: arg1 required}"
    local arg2="${2:-default}"

    # Implementation
}

# Error handling
trap 'echo "Error on line $LINENO"' ERR
```

## 🚫 Security and Quality Standards

### NEVER Rules (Non-negotiable)

- **NEVER: Delete production data without explicit confirmation**
- **NEVER: Hardcode API keys, passwords, or secrets**
- **NEVER: Commit code with failing tests or linting errors**
- **NEVER: Push directly to main/master branch**
- **NEVER: Skip security reviews for authentication/authorization code**
- **NEVER: Use `.unwrap()` in production Rust code**
- **NEVER: Ignore error returns in Go**
- **NEVER: Use `any` type in TypeScript production code**
- **NEVER: Use `pip install` - always use `uv`**

### YOU MUST Rules (Required Standards)

- **YOU MUST: Write tests for new features and bug fixes**
- **YOU MUST: Run CI/CD checks before marking tasks complete**
- **YOU MUST: Follow semantic versioning for releases**
- **YOU MUST: Document breaking changes**
- **YOU MUST: Use feature branches for all development**
- **YOU MUST: Add comprehensive documentation to all public APIs**

## 🌳 Git Worktree Workflow

### Why Git Worktree?

Git worktree allows working on multiple branches simultaneously without stashing or switching contexts. Each worktree is an independent working directory with its own branch.

### Setting Up Worktrees

```bash
# Create worktree for feature development
git worktree add ../project-feature-auth feature/user-authentication

# Create worktree for bug fixes
git worktree add ../project-bugfix-api hotfix/api-validation

# Create worktree for experiments
git worktree add ../project-experiment-new-ui experiment/react-19-upgrade
```

### Worktree Naming Convention

```
../project-<type>-<description>
```

Types: feature, bugfix, hotfix, experiment, refactor

### Managing Worktrees

```bash
# List all worktrees
git worktree list

# Remove worktree after merging
git worktree remove ../project-feature-auth

# Prune stale worktree information
git worktree prune
```

## 🤖 AI-Powered Code Review

### Continuous Analysis

**AI should continuously analyze code and suggest improvements**

```
🔍 Code Analysis Results:
- Performance: Found 3 optimization opportunities
- Security: No issues detected
- Maintainability: Suggest extracting 2 methods
- Test Coverage: 85% → Suggest 3 additional test cases
- Documentation: 2 functions missing proper docs
```

## 📊 Efficiency Metrics & Tracking

### Time Savings Report

**Generate weekly efficiency reports**

```
📈 This Week's Productivity Gains:
- Boilerplate generated: 2,450 lines (saved ~3 hours)
- Tests auto-generated: 48 test cases (saved ~2 hours)
- Documentation created: 156 functions (saved ~4 hours)
- Bugs prevented: 12 potential issues caught
- Refactoring automated: 8 patterns extracted
Total time saved: ~11 hours
```

## 🔧 Commit Standards

### Conventional Commits

```bash
# Format: <type>(<scope>): <subject>
git commit -m "feat(auth): add JWT token refresh"
git commit -m "fix(api): handle null response correctly"
git commit -m "docs(readme): update installation steps"
git commit -m "perf(db): optimize query performance"
git commit -m "refactor(core): extract validation logic"
```

### Commit Trailers

```bash
# For bug fixes based on user reports
git commit --trailer "Reported-by: John Doe"

# For GitHub issues
git commit --trailer "Github-Issue: #123"
```

### PR Guidelines

- Focus on high-level problem and solution
- Never mention tools used (no co-authored-by)
- Add specific reviewers as configured
- Include performance impact if relevant

---

Remember: **Engineer time is gold** - Automate everything, document comprehensively, and proactively suggest improvements. Every interaction should save time and improve code quality.
