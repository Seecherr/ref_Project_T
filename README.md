# 📚 Library Management System

[![CI Pipeline](https://github.com/your-username/library-management-system/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/your-username/library-management-system/actions/workflows/ci-pipeline.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=your-project-key&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=your-project-key)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=your-project-key&metric=coverage)](https://sonarcloud.io/summary/new_code?id=your-project-key)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=your-project-key&metric=bugs)](https://sonarcloud.io/summary/new_code?id=your-project-key)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=your-project-key&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=your-project-key)

An in-memory Library Management System built with Python, implementing SOLID principles and GoF design patterns (Strategy, Observer). Features comprehensive test coverage (200+ tests) and CI/CD integration with SonarCloud.

## 🏗️ Architecture

The system follows a **3-layer architecture** with dependency injection:

```
Services Layer   →  Business logic (CatalogService, LoanService, FineService, etc.)
Storage Layer    →  Abstract repositories + In-Memory implementations
Models Layer     →  Domain entities (Book, Member, Loan, Fine, Reservation, Notification)
```

### Design Patterns

| Pattern | Usage | Location |
|---------|-------|----------|
| **Strategy** | Fine calculation algorithms (Standard, Progressive, NoFine) | `src/utils/fine_strategy.py` |
| **Observer** | Event-driven notifications on book return | `src/utils/event_manager.py` |
| **Repository** | Abstract data access behind interfaces | `src/storage/interfaces.py` |

### SOLID Principles

- **S**: Each service has single responsibility
- **O**: New fine strategies without modifying existing code
- **L**: Reader/Librarian substitutable for Member
- **I**: Focused repository interfaces
- **D**: Services depend on abstract repositories, not implementations

## 📂 Project Structure

```
├── src/
│   ├── models/           # Domain entities (Book, Member, Loan, Fine, etc.)
│   ├── services/         # Business logic services
│   ├── storage/          # Repository interfaces + In-Memory implementations
│   └── utils/            # Patterns (Strategy, Observer), validators, exceptions
├── tests/
│   ├── unit/             # Unit tests (~230 tests)
│   └── integration/      # Integration tests (~30 tests)
├── docs/
│   └── diagrams/         # UML diagrams (Use Case, Domain Model, Class Diagram)
├── .cursor/rules/        # AI assistant rules
├── .github/workflows/    # CI/CD pipeline
├── Dockerfile            # Containerized test execution
├── pyproject.toml        # Project configuration
└── sonar-project.properties
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/library-management-system.git
cd library-management-system

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html:htmlcov -v

# Run only unit tests
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Full CI command (XML + HTML reports)
pytest --cov=src --cov-report=xml:coverage.xml --cov-report=html:htmlcov --junitxml=reports/junit.xml -v
```

### Docker

```bash
# Build the image
docker build -t library-management-system .

# Run tests in container
docker run library-management-system
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline runs on every push/PR and:

1. ✅ Installs dependencies
2. ✅ Runs 200+ tests with coverage
3. ✅ Generates HTML/XML reports
4. ✅ Uploads test artifacts (downloadable ZIP)
5. ✅ Sends results to SonarCloud
6. ✅ Fails if coverage < 70%

### SonarCloud Quality Gate

- **Code Coverage**: ≥ 70%
- **Bugs**: 0
- **Vulnerabilities**: 0
- **Code Smells**: Rating A or B

## 📊 UML Diagrams

- [Use Case Diagram](docs/diagrams/use_case_diagram.md)
- [Domain Model](docs/diagrams/domain_model.md)
- [Class Diagram](docs/diagrams/class_diagram.md)

## 👥 Actors & Use Cases

| Actor | Capabilities |
|-------|-------------|
| **Reader** | Borrow/return books, search catalog, place reservations, pay fines, receive notifications |
| **Librarian** | All reader actions + manage catalog, block/unblock members |

### Key Scenarios

1. **Borrow Book** — Validates member status, loan limits, book availability
2. **Return Book** — Calculates overdue fines, triggers reservation notifications
3. **Reserve Book** — FIFO priority queue for unavailable books
4. **Pay Fine** — Partial/full payment with auto-unblock
5. **Block/Unblock** — Auto-block at fine threshold, auto-unblock after payment

## 📝 License

This project is for educational purposes.
