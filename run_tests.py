#!/usr/bin/env python3
"""
Comprehensive test runner for Team Tools Calculator
"""

import argparse
import os
import subprocess  # nosec: B404 - subprocess used for legitimate test script
import sys


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print("=" * 60)

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed!")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def install_dependencies():
    """Install testing dependencies"""
    print("Installing testing dependencies...")
    return run_command(
        "pip install -r requirements-test.txt", "Installing test dependencies"
    )


def run_unit_tests():
    """Run unit tests"""
    return run_command("python -m pytest tests/unit/ -v --tb=short", "Unit tests")


def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "python -m pytest tests/integration/ -v --tb=short", "Integration tests"
    )


def run_template_tests():
    """Run template tests"""
    return run_command(
        "python -m pytest tests/templates/ -v --tb=short", "Template tests"
    )


def run_all_tests():
    """Run all tests with coverage"""
    return run_command(
        "python -m pytest tests/ -v --tb=short --cov=calculations --cov=app --cov-report=html --cov-report=term-missing",
        "All tests with coverage",
    )


def run_performance_tests():
    """Run performance tests"""
    return run_command(
        "python -m pytest tests/ -v -m performance --tb=short", "Performance tests"
    )


def run_regression_tests():
    """Run regression tests"""
    return run_command(
        "python -m pytest tests/ -v -m regression --tb=short", "Regression tests"
    )


def run_linting():
    """Run code linting"""
    success = True

    # Check if flake8 is available
    try:
        subprocess.run(["flake8", "--version"], capture_output=True, check=True)
        success &= run_command(
            "flake8 app.py calculations/ --max-line-length=88 --ignore=E501,W503",
            "Linting with flake8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("flake8 not available, skipping linting")

    return success


def run_security_check():
    """Run security checks"""
    try:
        subprocess.run(["bandit", "--version"], capture_output=True, check=True)
        return run_command(
            "bandit -r app.py calculations/ -f json -o reports/security_report.json",
            "Security check with bandit",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("bandit not available, skipping security check")
        return True


def generate_test_report():
    """Generate comprehensive test report"""
    return run_command(
        "python -m pytest tests/ --html=reports/test_report.html --self-contained-html --junitxml=reports/junit.xml",
        "Generating test report",
    )


def validate_environment():
    """Validate that the environment is set up correctly"""
    print("Validating environment...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return False

    # Check that required files exist
    required_files = [
        "app.py",
        "calculations/__init__.py",
        "calculations/fixed_horizon.py",
        "calculations/msprt.py",
        "calculations/std_calculator.py",
        "calculations/statistics.py",
        "requirements-test.txt",
        "pytest.ini",
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"ERROR: Required file {file_path} not found")
            return False

    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    print("Environment validation passed!")
    return True


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Team Tools Calculator Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument(
        "--templates", action="store_true", help="Run template tests only"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests only"
    )
    parser.add_argument(
        "--regression", action="store_true", help="Run regression tests only"
    )
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument(
        "--security", action="store_true", help="Run security checks only"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install test dependencies"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run quick tests (unit + integration)"
    )
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run CI pipeline (all tests + linting + security)",
    )

    args = parser.parse_args()

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    success = True

    # Install dependencies if requested
    if args.install_deps:
        success &= install_dependencies()

    # Run specific test types
    if args.unit:
        success &= run_unit_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.templates:
        success &= run_template_tests()
    elif args.performance:
        success &= run_performance_tests()
    elif args.regression:
        success &= run_regression_tests()
    elif args.lint:
        success &= run_linting()
    elif args.security:
        success &= run_security_check()
    elif args.quick:
        success &= run_unit_tests()
        success &= run_integration_tests()
    elif args.all:
        success &= run_all_tests()
        success &= run_linting()
        success &= generate_test_report()
    elif args.ci:
        success &= run_all_tests()
        success &= run_linting()
        success &= run_security_check()
        success &= generate_test_report()
    else:
        # Default: run all tests
        success &= run_all_tests()

    # Print summary
    print("\\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Your calculator application is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for details.")
    print("=" * 60)

    # Generate final report
    if success:
        print("\\n📊 Test reports generated in 'reports/' directory:")
        print("  - reports/test_report.html - Comprehensive test report")
        print("  - htmlcov/index.html - Coverage report")
        print("  - reports/junit.xml - JUnit XML report")

        if os.path.exists("reports/security_report.json"):
            print("  - reports/security_report.json - Security analysis")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
