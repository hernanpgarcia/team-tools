"""
Team Tools Dashboard - Modular Flask Application
"""
from flask import Flask, render_template, request
from calculations.fixed_horizon import calculate_sample_size
from calculations.msprt import calculate_msprt_plan
from calculations.std_calculator import (calculate_std_from_data, estimate_std_from_range, 
                                       estimate_std_from_percentiles, sample_size_for_std_estimation,
                                       calculate_std_from_conversion_data, estimate_conversion_rate_std)

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

@app.route('/std-calculator')
def std_calculator():
    return render_template('std_calculator_form.html')

@app.route('/calculate-std-from-data', methods=['POST'])
def calculate_std_from_data_route():
    try:
        # Parse data points from textarea
        data_input = request.form['data_points'].strip()
        
        # Handle different input formats
        if ',' in data_input:
            data_points = [float(x.strip()) for x in data_input.split(',') if x.strip()]
        elif '\n' in data_input:
            data_points = [float(x.strip()) for x in data_input.split('\n') if x.strip()]
        else:
            data_points = [float(x.strip()) for x in data_input.split() if x.strip()]
        
        results = calculate_std_from_data(data_points)
        return render_template('std_calculator_results.html', method='data', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/std-calculator')

@app.route('/calculate-std-from-range', methods=['POST'])
def calculate_std_from_range_route():
    try:
        min_val = float(request.form['min_val'])
        max_val = float(request.form['max_val'])
        method = request.form['estimation_method']
        
        results = estimate_std_from_range(min_val, max_val, method)
        return render_template('std_calculator_results.html', method='range', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/std-calculator')

@app.route('/calculate-std-from-percentiles', methods=['POST'])
def calculate_std_from_percentiles_route():
    try:
        p25 = float(request.form['p25'])
        p50 = float(request.form['p50'])
        p75 = float(request.form['p75'])
        
        results = estimate_std_from_percentiles(p25, p50, p75)
        return render_template('std_calculator_results.html', method='percentiles', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/std-calculator')

@app.route('/calculate-conversion-rate-std', methods=['POST'])
def calculate_conversion_rate_std_route():
    try:
        calc_type = request.form['calc_type']
        
        if calc_type == 'historical_data':
            # Parse historical conversion data
            conversions_input = request.form['conversions'].strip()
            visitors_input = request.form['visitors'].strip()
            
            # Parse conversions
            if ',' in conversions_input:
                conversions = [int(x.strip()) for x in conversions_input.split(',') if x.strip()]
            else:
                conversions = [int(x.strip()) for x in conversions_input.split() if x.strip()]
            
            # Parse visitors
            if ',' in visitors_input:
                visitors = [int(x.strip()) for x in visitors_input.split(',') if x.strip()]
            else:
                visitors = [int(x.strip()) for x in visitors_input.split() if x.strip()]
            
            results = calculate_std_from_conversion_data(conversions, visitors)
            return render_template('std_calculator_results.html', method='conversion_data', **results)
            
        elif calc_type == 'theoretical':
            baseline_rate = float(request.form['baseline_rate']) / 100  # Convert percentage to decimal
            sample_size = int(request.form['sample_size'])
            
      
            results = estimate_conversion_rate_std(baseline_rate, sample_size)
            return render_template('std_calculator_results.html', method='conversion_theoretical', **results)
        
    except Exception as e:
        return render_template('error.html', 
                             error_message=str(e),
                             back_url='/std-calculator')

if __name__ == '__main__':
    app.run(debug=True)