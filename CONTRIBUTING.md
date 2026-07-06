# Contributing to Personalized Networking Assistant

Thank you for your interest in contributing! This document provides guidelines
to make the contribution process smooth for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Message Convention](#commit-message-convention)

---

## Code of Conduct

By participating in this project you agree to abide by our Code of Conduct.
Be respectful, inclusive, and constructive in all interactions.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- (Optional) Docker + Docker Compose

### Local Setup

```bash
git clone https://github.com/your-org/networking-assistant.git
cd networking-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Create data directory
mkdir -p data
echo '[]' > data/history.json
echo '[]' > data/profiles.json
```

---

## Development Workflow

1. Fork the repository on GitHub.
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Start the development servers:
   ```bash
   # Terminal 1: FastAPI backend
   uvicorn app.main:app --reload

   # Terminal 2: Streamlit frontend
   streamlit run frontend/streamlit_app.py
   ```
4. Make your changes following the [Coding Standards](#coding-standards).
5. Run tests and ensure they pass:
   ```bash
   pytest tests/ -v --cov=app --cov-report=term-missing
   ```
6. Commit and push your branch.
7. Open a Pull Request against `main`.

---

## Pull Request Process

1. **Title**: Use the format `type(scope): short description`
   - Example: `feat(nlp): add multi-label classification support`
2. **Description**: Explain *what* changed and *why*.
3. **Tests**: All new features must include tests. Bug fixes should add a
   regression test.
4. **Coverage**: Maintain ≥ 80% test coverage. Aim for 90%+.
5. **Docs**: Update README and docstrings for any public API changes.
6. **Review**: At least one maintainer approval is required before merging.

---

## Coding Standards

- **Python 3.11+** features are encouraged.
- **Type hints** on all function signatures.
- **Docstrings** (Google style) on all public functions, classes, and modules.
- **PEP 8** compliance; use `ruff` for linting:
  ```bash
  ruff check app/ tests/ frontend/
  ```
- Follow **SOLID** design principles:
  - Single Responsibility: each module/service has one job.
  - Open/Closed: extend via new services, not modifying existing ones.
  - Dependency Injection via function parameters (not global singletons in tests).
- No `print()` statements — use `logging`.
- No bare `except:` — catch specific exceptions.

---

## Testing Requirements

- Use `pytest` with `pytest-asyncio` for async endpoint tests.
- Mock all external calls (Hugging Face, Wikipedia) using `unittest.mock`.
- Each PR must:
  - Not reduce overall coverage below 80%.
  - Include tests for success paths, validation errors, and edge cases.
- Run the full suite before submitting:
  ```bash
  pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
  ```

---

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

| Type     | Description                       |
|----------|-----------------------------------|
| `feat`   | New feature                       |
| `fix`    | Bug fix                           |
| `docs`   | Documentation only                |
| `test`   | Adding or fixing tests            |
| `refactor` | Code change (no feature/fix)   |
| `chore`  | Build, CI, or tooling changes     |
| `perf`   | Performance improvement           |

**Examples:**
```
feat(api): add /export/csv endpoint for history download
fix(nlp): handle empty event_description gracefully
test(feedback): add regression test for unknown session ID
```

---

Thank you for helping make Personalized Networking Assistant better! 🤝
