# Library Management System - Claude Rules

Persistent guidelines, commands, and project context for Claude.

## 📝 Project Context
An in-memory Library Management System implementing domain entities (Book, Member, Loan, Fine, etc.) with SOLID principles and GoF design patterns (Strategy, Observer, Repository).

## 🛠️ Tech Stack & Architecture
- **Language**: Python 3.10+
- **Framework**: Flask (used for API in `app.py`)
- **Key Patterns**:
  - **Strategy**: Fine calculation strategies (`src/utils/fine_strategy.py`).
  - **Observer**: Event management & notifications (`src/utils/event_manager.py`).
  - **Repository**: Data access abstractions (`src/storage/interfaces.py`).

## 🚀 Common Commands

### Running & Testing
- **Run CLI App**: `python main.py`
- **Run Web/API App**: `python app.py`
- **Run Tests**: `python -m pytest`
- **Run Tests with Coverage**: `python -m pytest --cov=src --cov-report=term-missing`

### Linting & Formatting
- **Lint Check**: `python -m ruff check src/ app.py main.py tests/ --output-format=github`
- **Format Check**: `python -m ruff format --check src/ app.py main.py tests/`
- **Auto-format**: `python -m ruff format src/ app.py main.py tests/`

### Static Analysis & Type Checking
- **Type Check**: `python -m mypy src/ app.py main.py --ignore-missing-imports`
- **Security Scan**: `python -m bandit -r src/ app.py main.py -c pyproject.toml -f txt`

## 📐 Coding Guidelines

### Design & Architecture
- Enforce **SOLID** principles. Depend on abstract repository interfaces in `src/storage/interfaces.py`, not in-memory implementations.
- Strategy pattern for fine calculation must implement `FineStrategy` and be configured in `FineService`.
- Observer pattern triggers must subscribe to and publish through `EventManager`.

### Code Style & Type Safety
- **Type Hints**: Keep code fully typed. Mypy checks must pass cleanly.
- **Dataclass Fields**: If a field defaults to `None` in type signature but is guaranteed to be set in `__post_init__` (e.g. `due_date`), declare it with the concrete type and ignore the default assignment mismatch:
  ```python
  due_date: date = field(default=None)  # type: ignore[assignment]
  ```
- **Docstrings & Comments**: Do not use ambiguous unicode characters like `×` in comments or docstrings. Use the standard ASCII `x` character.
- **Exceptions & Assertions**: Use descriptive error messages.

### Test Guidelines
- Enforce Ruff rule `PT011` for broad exception testing. When using `pytest.raises(ValueError)`, always specify a `match` parameter to check the error message:
  ```python
  with pytest.raises(ValueError, match="cannot be empty"):
  ```

### CI/CD Workflow
- Workflows in `.github/workflows/` run on self-hosted Windows runners. All command steps must be PowerShell-compatible. Avoid using Bash-specific operators like `|| true`. Use GitHub Actions native `continue-on-error: true` to ignore step failures.
