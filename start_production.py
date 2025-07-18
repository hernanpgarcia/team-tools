#!/usr/bin/env python3
"""
Production startup script for Team Tools Calculator
Uses gunicorn WSGI server instead of Flask development server
"""
import os
import subprocess
import sys


def main():
    """Start the application using gunicorn for production"""
    port = os.environ.get("PORT", "8080")

    # Set production environment
    os.environ["FLASK_ENV"] = "production"

    # Gunicorn command with WARNING level logging for pristine production logs
    cmd = [
        "gunicorn",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        "4",
        "--timeout",
        "120",
        "--keep-alive",
        "2",
        "--max-requests",
        "1000",
        "--max-requests-jitter",
        "50",
        "--log-level",
        "warning",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "app:app",
    ]

    print(f"Starting production server on port {port}")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: gunicorn not found. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "gunicorn==21.2.0"], check=True
        )
        print("Retrying with gunicorn...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        print("Falling back to Flask development server...")
        # Fallback to Flask dev server
        os.system("python app.py")  # nosec: B605 - Fallback only, controlled input
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()
