#!/usr/bin/env python3
"""
Wrapper script to run integration tests only if dependencies are available
"""
import subprocess
import sys


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import bs4  # noqa: F401
        import flask  # noqa: F401
        import pytest  # noqa: F401

        return True
    except ImportError as e:
        print(f"Dependencies not available ({e}), skipping integration tests")
        return False


def main():
    if not check_dependencies():
        return 0

    try:
        # nosec: B603 - subprocess call with trusted input (sys.executable and fixed args)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
            check=True,
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        return e.returncode
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
