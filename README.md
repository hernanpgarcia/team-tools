# 🧮 Team Tools Calculator

A simple, powerful web calculator for A/B testing and statistical analysis. Perfect for product teams, data analysts, and researchers who need reliable statistical tools without complex software.

## 🚀 Quick Start

**New to this project?** Read the **[PROJECT_SETUP.md](PROJECT_SETUP.md)** for complete setup instructions.

**Already set up?** Run: `python run_app.py` and go to http://localhost:5000

## 🛠️ What This Calculator Can Do

### 📊 Sample Size Calculator
Calculate how many participants you need for your A/B test:
- **Input**: Your expected improvement and baseline metrics
- **Output**: Required sample size for reliable results
- **Features**: Handles unknown standard deviation, provides confidence intervals

### 🔄 Sequential Testing Calculator  
Plan experiments that can stop early when results are clear:
- **Input**: Test parameters and monitoring preferences
- **Output**: Monitoring plan with decision boundaries
- **Features**: Reduces sample size needs, continuous monitoring

### 📈 Standard Deviation Calculator
Estimate data variability when you don't have complete data:
- **From data points**: Calculate from your actual data
- **From ranges**: Estimate from min/max values
- **From percentiles**: Use quartiles for better estimates
- **For conversion rates**: Specialized calculations for A/B tests

## 📁 Project Files

```
team-tools/
├── 📖 PROJECT_SETUP.md        # Complete setup guide (READ THIS FIRST!)
├── 🚀 setup.py              # Automated setup script
├── ▶️  run_app.py            # Easy way to start the calculator
├── ✅ quick_test.py          # Test if everything works
├── 🧮 app.py                # Main calculator application
├── 📋 requirements.txt       # Required software packages
├── 🔧 calculations/          # Calculator logic
├── 🎨 templates/            # Web pages
├── 🎯 tests/                # Automated tests
└── 📊 static/               # Styling
```

## 🎯 Common Use Cases

- **Product Managers**: "How many users do I need to test my new feature?"
- **Data Analysts**: "What's the standard deviation of this metric?"
- **Researchers**: "Can I stop this experiment early?"
- **Marketing Teams**: "How long should I run this campaign test?"

## 🔧 Need Help?

1. **Setup Issues**: Read [PROJECT_SETUP.md](PROJECT_SETUP.md) - it has detailed troubleshooting
2. **Calculator Not Working**: Run `python quick_test.py` to check for problems
3. **Want to Update**: Run `python setup.py` to reinstall everything

## 🎉 Features

✅ **No coding required** - Just point, click, and calculate  
✅ **Comprehensive testing** - Over 120 automated tests ensure reliability  
✅ **Error handling** - Clear error messages help you fix input problems  
✅ **Professional results** - Detailed output with explanations  
✅ **Mobile friendly** - Works on phones, tablets, and computers  
✅ **Offline capable** - Runs on your computer, no internet needed  

## 📊 Mathematical Reliability

All calculations use industry-standard statistical methods:
- **Normal and t-distributions** for sample size calculations
- **Cohen's d** for effect size analysis
- **mSPRT framework** for sequential testing
- **Welch's t-test** for unequal variances
- **Conservative estimates** when data is uncertain

## 🚀 Getting Started

1. **First time?** Follow [PROJECT_SETUP.md](PROJECT_SETUP.md) step-by-step
2. **Already set up?** Run `python run_app.py`
3. **Having issues?** Run `python quick_test.py` to check for problems

Your calculator will be available at: **http://localhost:5000**

---

*Built with reliability in mind - over 120 tests ensure your calculations are always correct!* ✅