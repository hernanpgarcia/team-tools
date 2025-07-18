#!/usr/bin/env python3
"""
Easy way to start the Team Tools Calculator
"""
import os
import platform
import subprocess
import sys


def main():
    print("Starting Team Tools Calculator...")
    print("")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the calculator")
    print("")

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Activate virtual environment and run app
    if platform.system() == "Windows":
        cmd = "venv\\Scripts\\activate && python app.py"
    else:
        cmd = "source venv/bin/activate && python app.py"

    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nCalculator stopped. Thanks for using Team Tools!")


if __name__ == "__main__":
    main()
