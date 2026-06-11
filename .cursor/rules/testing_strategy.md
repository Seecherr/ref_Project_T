# Testing Strategy — Library Management System

## Testing Stack

| Tool | Purpose |
|---|---|
| `pytest` | Test runner and framework |
| `pytest-cov` | Code coverage measurement |
| `pytest-html` | HTML test reports |
| `pytest-mock` | Mocking framework |

## Coverage Target

- **Minimum: 70%** (enforced by `--cov-fail-under=70`)
- **Goal: 85%+** for critical business logic

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── models/              # Model unit tests
│   ├── storage/             # Repository unit tests
│   ├── services/            # Service unit tests (with mocked repos)
│   └── utils/               # Utility/pattern unit tests
└── integration/             # Cross-service workflow tests
```

## Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml

# Run with JUnit XML (for CI)
pytest --junitxml=reports/junit.xml

# Full CI command
pytest --cov=src --cov-report=xml:coverage.xml --cov-report=html:htmlcov --junitxml=reports/junit.xml -v
```

## Report Generation

### XML Reports (for SonarQube)
- `coverage.xml` — Coverage data
- `reports/junit.xml` — Test execution results

### HTML Reports (for developers)
- `htmlcov/` — Visual coverage report with highlighted lines

## Test Writing Guidelines

1. **Naming**: `test_<method>_<scenario>` (e.g., `test_borrow_book_member_blocked`)
2. **Structure**: Arrange-Act-Assert pattern
3. **Fixtures**: Use pytest fixtures from conftest.py for common setup
4. **Mocking**: Use `pytest-mock` to isolate service dependencies
5. **Edge Cases**: Test boundaries, nulls, empty collections, error conditions
6. **Integration**: Test full workflows across services with real in-memory repos

## AI Instructions for Test Generation

When generating tests:
- Always import from `src.*` modules
- Use fixtures from `tests/conftest.py`
- Each test class should test one component
- Include both positive and negative test cases
- Test edge cases: empty strings, zero values, None, boundary values
- Integration tests should use real in-memory repos, not mocks
