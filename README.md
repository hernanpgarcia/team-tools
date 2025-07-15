# Team Tools Dashboard

A Flask-based web application providing statistical tools for A/B testing and data analysis. This toolkit offers comprehensive solutions for sample size calculations, sequential testing, and standard deviation estimation.

## Features

### 🧮 Sample Size Calculator (Fixed Horizon)
Calculate required sample sizes for traditional A/B tests with fixed endpoints.
- Supports both absolute and relative improvement scenarios
- Configurable statistical power (80%, 90%, etc.) and significance levels
- Handles unknown standard deviation with robust estimation
- Provides confidence intervals for effect sizes
- Uses Welch's T-test framework for reliable results

### 🔄 Sequential Testing (mSPRT)
Plan experiments that can be stopped early when results become conclusive.
- Mixed Sequential Probability Ratio Test (mSPRT) framework
- Continuous monitoring without alpha inflation issues
- Efficiency gains through early stopping
- Robust variance handling for unknown standard deviations
- Generates monitoring plans with decision boundaries

### 📊 Standard Deviation Calculator
Comprehensive tools for estimating and calculating standard deviations when data is limited.
- Calculate from raw data points
- Estimate from min/max ranges using multiple methods
- Derive from percentiles (quartiles) for better accuracy
- Specialized conversion rate standard deviation calculations
- Sample size requirements for standard deviation estimation

## Project Structure

### Core Application Files
- **`app.py`** - Main Flask application with all routes and request handling
- **`app_old.py`** - Previous version of the application (backup)

### Calculation Modules (`calculations/`)
- **`__init__.py`** - Package initialization (currently empty)
- **`fixed_horizon.py`** - Sample size calculations for traditional A/B tests
- **`msprt.py`** - Sequential testing calculations and monitoring plans  
- **`statistics.py`** - Core statistical functions (normal/t-distributions, effect sizes)
- **`std_calculator.py`** - Standard deviation estimation and calculation utilities

### Frontend (`templates/`)
- **`base.html`** - Base template with common layout and navigation
- **`home.html`** - Landing page with tool descriptions and navigation
- **`error.html`** - Error page template for handling exceptions
- **`fixed_horizon_form.html`** - Input form for sample size calculator
- **`msprt_form.html`** - Input form for sequential testing planner
- **`msprt_results.html`** - Results display for sequential testing
- **`std_calculator_form.html`** - Input form for standard deviation tools
- **`std_calculator_results.html`** - Results display for standard deviation calculations

### Styling (`static/`)
- **`style.css`** - Complete stylesheet with modern, responsive design

### Environment
- **`venv/`** - Python virtual environment (development dependencies)

## Key Mathematical Capabilities

### Sample Size Calculations
- Power analysis using normal and t-distributions
- Effect size calculations (Cohen's d)
- Two-sided and one-sided test support
- Confidence interval estimation

### Sequential Testing
- mSPRT boundary calculations
- Expected sample size under null and alternative hypotheses
- Monitoring tables with decision points
- Type I and Type II error control

### Standard Deviation Estimation
- Sample standard deviation from raw data
- Range-based estimation (Range Rule, Six Sigma Rule)
- Quartile-based estimation (IQR method)
- Binomial proportion standard deviations
- Theoretical vs. observed variance analysis

## Installation & Usage

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install flask
   ```

2. **Run Application**
   ```bash
   python app.py
   ```

3. **Access Tools**
   - Navigate to `http://localhost:5000`
   - Choose from available calculators on the home page

## Use Cases

- **Product Teams**: A/B test planning and analysis
- **Data Scientists**: Statistical power analysis and sample size determination
- **Researchers**: Sequential experiment design and monitoring
- **Analysts**: Standard deviation estimation from limited data

## Technical Implementation

The application uses a modular architecture with separated concerns:
- Flask handles web routing and user interface
- Mathematical calculations are isolated in dedicated modules
- Templates provide a clean, responsive user experience
- Error handling ensures robust user feedback

All statistical calculations are implemented from scratch using fundamental mathematical principles, ensuring transparency and customizability for specific use cases.