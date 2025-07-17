#!/usr/bin/env python3
"""
Team Tools Calculator - Automated Setup Script
This script sets up everything you need to run the calculator.
"""

import os
import sys
import subprocess
import platform
import time

def print_step(step, message):
    """Print a formatted step message"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print('='*60)

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def run_command(command, description):
    """Run a command and handle errors"""
    print_info(f"Running: {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print_success(f"{description} - Complete")
            return True
        else:
            print_error(f"{description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"{description} - Exception: {str(e)}")
        return False

def check_python():
    """Check if Python is available"""
    print_step(1, "Checking Python Installation")
    
    try:
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print_success(f"Python {version.major}.{version.minor}.{version.micro} is installed")
            return True
        else:
            print_error(f"Python {version.major}.{version.minor} is too old. Need Python 3.8+")
            return False
    except Exception as e:
        print_error(f"Python check failed: {str(e)}")
        return False

def setup_virtual_environment():
    """Create and setup virtual environment"""
    print_step(2, "Setting Up Virtual Environment")
    
    # Remove existing venv if it exists
    if os.path.exists('venv'):
        print_info("Removing existing virtual environment")
        if platform.system() == "Windows":
            run_command('rmdir /S /Q venv', "Remove old venv")
        else:
            run_command('rm -rf venv', "Remove old venv")
    
    # Find the correct Python command
    python_cmd = sys.executable
    if not python_cmd:
        python_cmd = 'python3' if subprocess.run(['which', 'python3'], capture_output=True).returncode == 0 else 'python'
    
    # Create new virtual environment
    if not run_command(f'{python_cmd} -m venv venv', "Create virtual environment"):
        return False
    
    # Activate virtual environment and install packages
    if platform.system() == "Windows":
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    # Upgrade pip
    if not run_command(f'{activate_cmd}python -m pip install --upgrade pip', "Upgrade pip"):
        return False
    
    # Install requirements
    if not run_command(f'{activate_cmd}pip install -r requirements.txt', "Install main requirements"):
        return False
    
    # Install test requirements
    if not run_command(f'{activate_cmd}pip install -r requirements-test.txt', "Install test requirements"):
        return False
    
    print_success("Virtual environment setup complete")
    return True

def setup_pre_commit_hooks():
    """Setup pre-commit hooks"""
    print_step(3, "Setting Up Code Quality Hooks")
    
    if platform.system() == "Windows":
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    if not run_command(f'{activate_cmd}pre-commit install', "Install pre-commit hooks"):
        print_info("Pre-commit hooks setup failed, but continuing...")
    else:
        print_success("Pre-commit hooks installed")
    
    return True

def run_tests():
    """Run tests to verify setup"""
    print_step(4, "Running Tests to Verify Setup")
    
    if platform.system() == "Windows":
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    # Run quick test
    if not run_command(f'{activate_cmd}python quick_test.py', "Run quick functionality test"):
        return False
    
    print_success("All tests passed!")
    return True

def create_run_script():
    """Create easy run script"""
    print_step(5, "Creating Easy Run Script")
    
    if platform.system() == "Windows":
        script_content = '''@echo off
echo Starting Team Tools Calculator...
echo.
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the calculator
echo.
cd /d "%~dp0"
call venv\\Scripts\\activate
python app.py
pause
'''
        with open('run_app.bat', 'w') as f:
            f.write(script_content)
        print_success("Created run_app.bat - Double-click to start calculator")
    else:
        script_content = '''#!/bin/bash
echo "Starting Team Tools Calculator..."
echo ""
echo "Open your browser to: http://localhost:5000"
echo "Press Ctrl+C to stop the calculator"
echo ""
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
'''
        with open('run_app.sh', 'w') as f:
            f.write(script_content)
        os.chmod('run_app.sh', 0o755)
        print_success("Created run_app.sh - Run with ./run_app.sh")
    
    # Also create a Python run script that works everywhere
    python_script = '''#!/usr/bin/env python3
"""
Easy way to start the Team Tools Calculator
"""
import os
import sys
import subprocess
import platform

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
        cmd = 'venv\\\\Scripts\\\\activate && python app.py'
    else:
        cmd = 'source venv/bin/activate && python app.py'
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\\nCalculator stopped. Thanks for using Team Tools!")

if __name__ == "__main__":
    main()
'''
    
    with open('run_app.py', 'w') as f:
        f.write(python_script)
    
    print_success("Created run_app.py - Run with: python run_app.py")
    return True

def main():
    """Main setup function"""
    print("🚀 Team Tools Calculator - Automated Setup")
    print("This will set up everything you need to run the calculator.")
    print("Please wait while we install and configure everything...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print_error("Please run this script from the team-tools directory")
        print_info("Navigate to the team-tools folder and run: python setup.py")
        sys.exit(1)
    
    # Run setup steps
    success = True
    
    if not check_python():
        success = False
    
    if success and not setup_virtual_environment():
        success = False
    
    if success:
        setup_pre_commit_hooks()  # This can fail without breaking setup
    
    if success and not run_tests():
        success = False
    
    if success:
        create_run_script()
    
    # Final message
    print("\n" + "="*60)
    if success:
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print_success("Your Team Tools Calculator is ready to use!")
        print("")
        print("📋 Next steps:")
        print("1. To start the calculator: python run_app.py")
        print("2. Open your browser to: http://localhost:5000")
        print("3. To test everything: python quick_test.py")
        print("4. To stop the calculator: Press Ctrl+C")
        print("")
        print("📖 For help, read: PROJECT_SETUP.md")
    else:
        print("❌ SETUP FAILED!")
        print("="*60)
        print_error("Something went wrong during setup")
        print("")
        print("🔧 Try these solutions:")
        print("1. Make sure Python 3.8+ is installed")
        print("2. Check your internet connection")
        print("3. Run setup again: python setup.py")
        print("4. Read the troubleshooting section in PROJECT_SETUP.md")
        sys.exit(1)

if __name__ == "__main__":
    main()