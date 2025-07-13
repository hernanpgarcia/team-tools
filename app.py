"""
Team Tools Dashboard - Modular Flask Application
"""
from flask import Flask, render_template, request
from calculations.fixed_horizon import calculate_sample_size
from calculations.msprt import calculate_msprt_plan

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sample-size-calculator')
def sample_size_calculator():
    return render_template('fixed_horizon_form.html')

@app.route('/calculate-sample-size', methods=['POST'])
def calculate_sample_size_route():
    try:
        # Extract form data
        baseline_mean = float(request.form['baseline_mean'])
        baseline_std = float(request.form.get('baseline_std', '')) if request.form.get('baseline_std') else None
        power = float(request.form['power'])
        alpha = float(request.form['alpha'])
        test_type = request.form['test_type']
        improvement_type = request.form['improvement_type']
        
        # Get improvement value
        if improvement_type == 'absolute':
            improvement_value = float(request.form['absolute_improvement'])
        else:
            improvement_value = float(request.form['relative_improvement'])
        
        # Calculate results
        results = calculate_sample_size(
            baseline_mean, baseline_std, improvement_type, 
            improvement_value, power, alpha, test_type
        )
        
        return render_template('fixed_horizon_results.html', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/sample-size-calculator')

@app.route('/sequential-calculator')
def sequential_calculator():
    return render_template('msprt_form.html')

@app.route('/calculate-msprt', methods=['POST'])
def calculate_msprt_route():
    try:
        # Extract form data
        baseline_mean = float(request.form['baseline_mean'])
        alpha = float(request.form['alpha'])
        beta = float(request.form['beta'])
        max_n = int(request.form['max_n'])
        min_n = int(request.form['min_n'])
        std_known = request.form['std_known']
        improvement_type = request.form['improvement_type']
        
        # Get standard deviation if provided
        baseline_std = None
        if std_known == 'known' or std_known == 'estimated':
            baseline_std = float(request.form.get('baseline_std', '')) if request.form.get('baseline_std') else None
        
        # Get improvement value
        if improvement_type == 'absolute':
            improvement_value = float(request.form['absolute_improvement'])
        else:
            improvement_value = float(request.form['relative_improvement'])
        
        # Calculate mSPRT plan
        results = calculate_msprt_plan(
            baseline_mean, std_known, baseline_std, improvement_type,
            improvement_value, alpha, beta, max_n, min_n
        )
        
        return render_template('msprt_results.html', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/sequential-calculator')

if __name__ == '__main__':
    app.run(debug=True)