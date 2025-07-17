# 🚀 Team Tools Calculator - Project Setup Guide

This guide will help you set up the Team Tools Calculator project on a new computer or after a fresh install.

## 📋 What You'll Need

Before starting, make sure you have:
- A computer with internet connection
- Basic knowledge of using Terminal/Command Prompt
- About 15-20 minutes of time

## 🏗️ Step-by-Step Setup

### Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Download Python 3.9 or higher
3. Install Python (make sure to check "Add Python to PATH" during installation)
4. Test installation by opening Terminal/Command Prompt and typing:
   ```
   python --version
   ```
   You should see something like "Python 3.9.6"

### Step 2: Get the Project Files
1. Download or copy the entire `team-tools` folder to your new computer
2. Place it in a location you'll remember (like your Desktop or Documents folder)

### Step 3: Open Terminal/Command Prompt
- **Windows**: Press `Windows + R`, type `cmd`, press Enter
- **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 4: Navigate to Project Folder
In the terminal, type:
```bash
cd /path/to/your/team-tools
```

For example, if you put the folder on your Desktop:
- **Windows**: `cd C:\Users\YourUsername\Desktop\team-tools`
- **Mac**: `cd ~/Desktop/team-tools`
- **Linux**: `cd ~/Desktop/team-tools`

### Step 5: Run the Automated Setup
Type this command and press Enter:
```bash
python setup.py
```

This will automatically:
- Create a virtual environment
- Install all required packages
- Set up the testing framework
- Run a quick test to make sure everything works

**Wait for it to complete** - this might take 2-3 minutes.

### Step 6: Test Your Installation
After setup completes, run:
```bash
python quick_test.py
```

You should see:
```
✅ Fixed horizon calculator works
✅ mSPRT calculator works  
✅ Standard deviation calculator works
✅ Flask app home page works
✅ Flask app calculation works
```

If you see all green checkmarks (✅), your setup is complete!

## 🎯 How to Use Your Calculator

### To Start the Calculator:
1. Open Terminal/Command Prompt
2. Navigate to your project folder (Step 4 above)
3. Type: `python run_app.py`
4. Open your web browser and go to: http://localhost:5000

### To Stop the Calculator:
- Press `Ctrl + C` in the terminal

## 📁 Project Structure

Here's what each important file does:

```
team-tools/
├── app.py                 # Main application (the calculator)
├── setup.py              # Automated setup script
├── run_app.py            # Easy way to start the calculator
├── quick_test.py         # Test if everything works
├── requirements.txt      # List of needed packages
├── calculations/         # Calculator logic
│   ├── fixed_horizon.py  # Sample size calculator
│   ├── msprt.py         # Sequential testing calculator
│   └── std_calculator.py # Standard deviation calculator
├── templates/            # Web pages
└── tests/               # Automated tests
```

## 🔧 Troubleshooting

### Problem: "python: command not found"
**Solution**: Python is not installed or not in your PATH
- Reinstall Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Problem: "No module named 'flask'"
**Solution**: Virtual environment not activated
- Run: `python setup.py` again
- Or manually activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)

### Problem: Calculator won't start
**Solution**: Check if port 5000 is busy
- Try: `python run_app.py --port 5001`
- Or find and close any other programs using port 5000

### Problem: Tests fail
**Solution**: Run setup again
- Type: `python setup.py`
- If still fails, delete the `venv` folder and run setup again

## 🆘 Need Help?

If you encounter any issues:

1. **First**: Try running `python setup.py` again
2. **Second**: Check the troubleshooting section above
3. **Third**: Look at the error message carefully - it often tells you what's wrong

## 📝 Daily Usage

### To start working:
1. Open Terminal
2. Go to project folder: `cd /path/to/team-tools`
3. Start calculator: `python run_app.py`
4. Open browser to: http://localhost:5000

### To test after making changes:
1. Run: `python quick_test.py`
2. All tests should show ✅

### To run full tests:
1. Run: `python run_tests.py`

## 🎉 You're Ready!

Once you see all green checkmarks from the quick test, your Team Tools Calculator is ready to use!

The calculator includes:
- **Sample Size Calculator**: Calculate how many participants you need for A/B tests
- **Sequential Testing**: Advanced testing with early stopping
- **Standard Deviation Calculator**: Estimate variability in your data

Enjoy using your calculator! 🎯