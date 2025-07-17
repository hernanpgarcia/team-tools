# Makefile for Team Tools Calculator

.PHONY: help install test test-unit test-integration test-templates test-performance test-regression clean lint security coverage report ci

help:
	@echo "Team Tools Calculator - Available Commands:"
	@echo ""
	@echo "  make install      - Install all dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-templates - Run template tests only"
	@echo "  make test-performance - Run performance tests only"
	@echo "  make test-regression - Run regression tests only"
	@echo "  make lint         - Run code linting"
	@echo "  make security     - Run security checks"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make report       - Generate comprehensive test report"
	@echo "  make ci           - Run full CI pipeline"
	@echo "  make clean        - Clean up generated files"
	@echo "  make dev          - Set up development environment"
	@echo ""

install:
	pip install -r requirements-test.txt

dev: install
	@echo "Development environment ready!"
	@echo "Run 'make test' to run all tests"

test:
	python run_tests.py --all

test-unit:
	python run_tests.py --unit

test-integration:
	python run_tests.py --integration

test-templates:
	python run_tests.py --templates

test-performance:
	python run_tests.py --performance

test-regression:
	python run_tests.py --regression

lint:
	python run_tests.py --lint

security:
	python run_tests.py --security

coverage:
	python -m pytest tests/ --cov=calculations --cov=app --cov-report=html --cov-report=term-missing

report:
	python -m pytest tests/ --html=reports/test_report.html --self-contained-html --junitxml=reports/junit.xml

ci:
	python run_tests.py --ci

quick:
	python run_tests.py --quick

clean:
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf tests/unit/__pycache__/
	rm -rf tests/integration/__pycache__/
	rm -rf tests/templates/__pycache__/
	rm -rf calculations/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .coverage
	rm -rf *.pyc
	rm -rf team_tools_debug.log

# Development helpers
run:
	FLASK_DEBUG=True python app.py

test-debug:
	python test_debug.py

format:
	@echo "Code formatting would go here (black, isort, etc.)"

check-deps:
	@echo "Checking dependencies..."
	python -c "import flask, jinja2, pytest; print('All dependencies available')"

# Git hooks
install-hooks:
	@echo "Installing git hooks..."
	@echo "#!/bin/bash" > .git/hooks/pre-commit
	@echo "make test-quick" >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed!"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Open DEBUG_GUIDE.md for debugging information"
	@echo "Open FIXES_SUMMARY.md for recent fixes"

# Utility targets
check-logs:
	@if [ -f team_tools_debug.log ]; then echo "Recent log entries:"; tail -20 team_tools_debug.log; else echo "No log file found"; fi

monitor-tests:
	@echo "Monitoring test execution..."
	python -m pytest tests/ --tb=short -v --no-header --quiet

# Release preparation
pre-release: clean ci
	@echo "Running pre-release checks..."
	python -c "import app; print('App imports successfully')"
	python -c "from calculations import fixed_horizon, msprt, std_calculator; print('All calculators import successfully')"
	@echo "Pre-release checks passed!"

# Docker support (if needed)
docker-build:
	@echo "Docker build would go here"

docker-test:
	@echo "Docker test would go here"

# Continuous integration helpers
ci-install:
	pip install -r requirements-test.txt
	pip install bandit flake8

ci-test:
	python run_tests.py --ci

# Performance monitoring
benchmark:
	python -m pytest tests/test_performance.py -v -m performance

profile:
	python -m pytest tests/test_performance.py -v -m performance --profile

# Database/migration helpers (if needed in future)
migrate:
	@echo "No migrations needed for this application"

# Deployment helpers
deploy-check:
	@echo "Checking deployment readiness..."
	python -c "import app; print('App ready for deployment')"

# Environment-specific targets
test-prod:
	FLASK_ENV=production python run_tests.py --all

test-dev:
	FLASK_ENV=development python run_tests.py --all

# Reporting
test-report-html:
	python -m pytest tests/ --html=reports/detailed_report.html --self-contained-html

test-report-xml:
	python -m pytest tests/ --junitxml=reports/junit.xml

test-report-json:
	python -m pytest tests/ --json-report --json-report-file=reports/report.json

# Multi-environment testing
test-all-envs:
	@echo "Testing in multiple environments..."
	FLASK_ENV=development python run_tests.py --quick
	FLASK_ENV=testing python run_tests.py --quick
	FLASK_ENV=production python run_tests.py --quick

# Stress testing
stress-test:
	python -m pytest tests/test_performance.py -v -k "stress or performance" --count=10

# Watchdog for continuous testing
watch:
	@echo "Watching for changes and running tests..."
	@echo "Use 'pip install pytest-watch' and run 'ptw' for file watching"

# Help for common issues
troubleshoot:
	@echo "Common troubleshooting steps:"
	@echo "1. Check Python version: python --version"
	@echo "2. Install dependencies: make install"
	@echo "3. Run quick test: make quick"
	@echo "4. Check logs: make check-logs"
	@echo "5. Clean and retry: make clean && make test"

# Default target
.DEFAULT_GOAL := help