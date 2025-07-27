# Development Setup

## Requirements

### Production Requirements
```bash
pip install -r requirements.txt
```

### Development/Testing Requirements (Optional)
```bash
pip install -r requirements-test.txt
```

## Pre-commit Hooks

The project uses pre-commit hooks for code quality. The hooks are designed to gracefully handle missing dependencies:

- **Unit tests**: Always run if pytest is available
- **Integration tests**: Only run if Flask and BeautifulSoup4 are available
- **Template tests**: Only run if Flask and BeautifulSoup4 are available

### Setup Pre-commit (Optional)
```bash
pip install pre-commit
pre-commit install
```

## Running Tests

### All Tests (if dependencies available)
```bash
python3 -m pytest
```

### Unit Tests Only
```bash
python3 -m pytest tests/unit/
```

### Individual Test Scripts
```bash
python3 scripts/run_unit_tests.py
python3 scripts/run_integration_tests.py
python3 scripts/run_template_tests.py
```

## Dependencies

- **Flask**: Web framework (required)
- **pytest**: Testing framework (testing only)
- **beautifulsoup4**: HTML parsing for integration tests (testing only)
- **hypothesis**: Property-based testing (testing only)
