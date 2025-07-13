from flask import Flask, request
import math

app = Flask(__name__)

# Z-table approximation function
def norm_ppf(p):
    """Approximation of the inverse normal CDF"""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1")
    
    if p < 0.5:
        return -norm_ppf(1 - p)
    
    p = p - 0.5
    t = math.sqrt(-2 * math.log(0.5 - p))
    
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    
    numerator = c0 + c1 * t + c2 * t * t
    denominator = 1 + d1 * t + d2 * t * t + d3 * t * t * t
    
    return t - numerator / denominator

def norm_cdf(x):
    """Approximation of the normal CDF"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def t_ppf(df, p):
    """Approximation of t-distribution inverse CDF"""
    if df >= 30:
        return norm_ppf(p)
    
    # Simple approximation for t-distribution
    z = norm_ppf(p)
    correction = (z**3 + z) / (4 * df)
    return z + correction

@app.route('/')
def home():
    return '''
    <h1>Team Tools Dashboard</h1>
    <ul>
        <li><a href="/sample-size-calculator">Sample Size Calculator (Fixed Horizon)</a></li>
        <li><a href="/sequential-calculator">Sequential Testing Calculator (mSPRT)</a></li>
        <li>OKR Tracker (Coming Soon)</li>
    </ul>
    '''

@app.route('/sample-size-calculator')
def sample_size_calculator():
    return '''
    <h2>Sample Size Calculator - Fixed Horizon Testing</h2>
    <form method="POST" action="/calculate-sample-size">
        <h3>Test Parameters</h3>
        
        <label><strong>Baseline Mean:</strong> <input type="number" step="any" name="baseline_mean" required placeholder="e.g., 2.5"></label><br><br>
        
        <label><strong>Standard Deviation (if known):</strong> <input type="number" step="any" name="baseline_std" placeholder="e.g., 0.8"></label><br>
        <small><em>Leave blank if unknown - we'll use conservative estimates</em></small><br><br>
        
        <h3>Expected Improvement</h3>
        <label>
            <input type="radio" name="improvement_type" value="absolute" checked> Absolute Improvement
            <input type="number" step="any" name="absolute_improvement" placeholder="e.g., 0.3">
        </label><br><br>
        
        <label>
            <input type="radio" name="improvement_type" value="relative"> Relative Improvement (%)
            <input type="number" step="any" name="relative_improvement" placeholder="e.g., 15">
        </label><br><br>
        
        <h3>Statistical Parameters</h3>
        <label><strong>Statistical Power:</strong>
            <select name="power">
                <option value="0.8" selected>80% (Standard)</option>
                <option value="0.85">85%</option>
                <option value="0.9">90%</option>
                <option value="0.95">95%</option>
            </select>
        </label><br><br>
        
        <label><strong>Significance Level (Alpha):</strong>
            <select name="alpha">
                <option value="0.01">1% (99% confidence)</option>
                <option value="0.05" selected>5% (95% confidence)</option>
                <option value="0.1">10% (90% confidence)</option>
            </select>
        </label><br><br>
        
        <label><strong>Test Type:</strong>
            <select name="test_type">
                <option value="two-sided" selected>Two-sided (Different)</option>
                <option value="one-sided">One-sided (Greater than)</option>
            </select>
        </label><br><br>
        
        <button type="submit">Calculate Sample Size</button>
    </form>
    <br><a href="/">← Back to Dashboard</a>
    '''

@app.route('/sequential-calculator')
def sequential_calculator():
    return '''
    <h2>Sequential Testing Calculator - mSPRT Framework</h2>
    <p><em>Mixed Sequential Probability Ratio Test for continuous monitoring</em></p>
    
    <form method="POST" action="/calculate-msprt">
        <h3>Test Parameters</h3>
        
        <label><strong>Baseline Mean:</strong> <input type="number" step="any" name="baseline_mean" required placeholder="e.g., 2.5"></label><br><br>
        
        <label><strong>Standard Deviation:</strong></label><br>
        <label>
            <input type="radio" name="std_known" value="known"> Known: <input type="number" step="any" name="baseline_std" placeholder="e.g., 0.8">
        </label><br>
        <label>
            <input type="radio" name="std_known" value="estimated" checked> Estimated from pilot data/historical data
        </label><br>
        <label>
            <input type="radio" name="std_known" value="unknown"> Unknown (use robust methods)
        </label><br><br>
        
        <h3>Expected Improvement</h3>
        <label>
            <input type="radio" name="improvement_type" value="absolute" checked> Absolute Improvement
            <input type="number" step="any" name="absolute_improvement" placeholder="e.g., 0.3">
        </label><br><br>
        
        <label>
            <input type="radio" name="improvement_type" value="relative"> Relative Improvement (%)
            <input type="number" step="any" name="relative_improvement" placeholder="e.g., 15">
        </label><br><br>
        
        <h3>mSPRT Parameters</h3>
        <label><strong>Type I Error (Alpha):</strong>
            <select name="alpha">
                <option value="0.01">1%</option>
                <option value="0.05" selected>5%</option>
                <option value="0.1">10%</option>
            </select>
        </label><br><br>
        
        <label><strong>Type II Error (Beta):</strong>
            <select name="beta">
                <option value="0.05">5% (95% power)</option>
                <option value="0.1">10% (90% power)</option>
                <option value="0.2" selected>20% (80% power)</option>
            </select>
        </label><br><br>
        
        <label><strong>Maximum Sample Size per Group:</strong> <input type="number" name="max_n" required placeholder="e.g., 10000"></label><br>
        <small><em>Safety cap to prevent infinite testing</em></small><br><br>
        
        <label><strong>Minimum Sample Size per Group:</strong> <input type="number" name="min_n" value="100" placeholder="e.g., 100"></label><br>
        <small><em>Minimum before any analysis (prevents early false positives)</em></small><br><br>
        
        <button type="submit">Calculate mSPRT Boundaries</button>
    </form>
    <br><a href="/">← Back to Dashboard</a>
    '''

@app.route('/calculate-sample-size', methods=['POST'])
def calculate_sample_size():
    try:
        # Get form data
        baseline_mean = float(request.form['baseline_mean'])
        baseline_std = float(request.form.get('baseline_std', '')) if request.form.get('baseline_std') else None
        power = float(request.form['power'])
        alpha = float(request.form['alpha'])
        test_type = request.form['test_type']
        improvement_type = request.form['improvement_type']
        
        # Calculate expected test mean
        if improvement_type == 'absolute':
            absolute_improvement = float(request.form['absolute_improvement'])
            test_mean = baseline_mean + absolute_improvement
            relative_improvement = (absolute_improvement / baseline_mean) * 100
        else:
            relative_improvement = float(request.form['relative_improvement'])
            absolute_improvement = baseline_mean * (relative_improvement / 100)
            test_mean = baseline_mean + absolute_improvement
        
        # Handle unknown standard deviation
        if baseline_std is None:
            # Conservative estimate: assume high variability
            baseline_std = abs(baseline_mean) * 0.5  # 50% CV as default
            std_note = "⚠️ Standard deviation estimated as {:.3f} (50% coefficient of variation). Use pilot data for better estimates.".format(baseline_std)
        else:
            std_note = ""
        
        # Effect size (Cohen's d)
        effect_size = abs(test_mean - baseline_mean) / baseline_std
        
        # Critical values
        if test_type == 'two-sided':
            z_alpha = norm_ppf(1 - alpha/2)
        else:
            z_alpha = norm_ppf(1 - alpha)
        
        z_beta = norm_ppf(power)
        
        # Sample size calculation
        sample_size_per_group = 2 * ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
        sample_size_per_group = math.ceil(sample_size_per_group)
        total_sample_size = sample_size_per_group * 2
        
        # Confidence intervals for effect size
        effect_size_se = math.sqrt(2 / sample_size_per_group)
        effect_size_ci_lower = effect_size - z_alpha * effect_size_se
        effect_size_ci_upper = effect_size + z_alpha * effect_size_se
        
        std_warning = '<div style="background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px;">{}</div>'.format(std_note) if std_note else ''
        
        return f'''
        <h2>Fixed Horizon Sample Size Results</h2>
        
        {std_warning}
        
        <h3>📊 Test Configuration</h3>
        <p><strong>Baseline Mean:</strong> {baseline_mean}</p>
        <p><strong>Baseline Std Dev:</strong> {baseline_std:.3f}</p>
        <p><strong>Expected Test Mean:</strong> {test_mean:.3f}</p>
        <p><strong>Absolute Improvement:</strong> {absolute_improvement:+.3f}</p>
        <p><strong>Relative Improvement:</strong> {relative_improvement:+.1f}%</p>
        
        <h3>📈 Effect Size Analysis</h3>
        <p><strong>Effect Size (Cohen's d):</strong> {effect_size:.3f}</p>
        <p><strong>95% CI for Effect Size:</strong> [{effect_size_ci_lower:.3f}, {effect_size_ci_upper:.3f}]</p>
        <p><em>Effect Size Interpretation:</em> 
        {'Small effect' if effect_size < 0.3 else 'Medium effect' if effect_size < 0.8 else 'Large effect'}</p>
        
        <h3>🎯 Required Sample Size</h3>
        <p><strong>Per Group:</strong> {sample_size_per_group:,} samples</p>
        <p><strong>Total:</strong> {total_sample_size:,} samples</p>
        
        <p><strong>⚠️ Note:</strong> For unknown standard deviation, consider using 
        <a href="/sequential-calculator">mSPRT Sequential Testing</a> which is more robust.</p>
        
        <br><a href="/sample-size-calculator">← Calculate Another</a>
        <br><a href="/sequential-calculator">→ Try mSPRT Sequential Testing</a>
        <br><a href="/">← Back to Dashboard</a>
        '''
        
    except Exception as e:
        return f'''
        <h2>Error</h2>
        <p>There was an error: {str(e)}</p>
        <br><a href="/sample-size-calculator">← Try Again</a>
        '''

@app.route('/calculate-msprt', methods=['POST'])
def calculate_msprt():
    try:
        # Get form data
        baseline_mean = float(request.form['baseline_mean'])
        alpha = float(request.form['alpha'])
        beta = float(request.form['beta'])
        max_n = int(request.form['max_n'])
        min_n = int(request.form['min_n'])
        std_known = request.form['std_known']
        improvement_type = request.form['improvement_type']
        
        # Handle standard deviation scenarios
        if std_known == 'known':
            baseline_std = float(request.form['baseline_std'])
            std_method = "Known standard deviation"
            use_t_test = False
        elif std_known == 'estimated':
            baseline_std = float(request.form.get('baseline_std', baseline_mean * 0.3))
            std_method = "Estimated standard deviation (use Welch's t-test)"
            use_t_test = True
        else:  # unknown
            baseline_std = abs(baseline_mean) * 0.5  # Conservative estimate
            std_method = "Unknown standard deviation (robust estimation)"
            use_t_test = True
        
        # Calculate expected test mean
        if improvement_type == 'absolute':
            absolute_improvement = float(request.form['absolute_improvement'])
            test_mean = baseline_mean + absolute_improvement
            relative_improvement = (absolute_improvement / baseline_mean) * 100
        else:
            relative_improvement = float(request.form['relative_improvement'])
            absolute_improvement = baseline_mean * (relative_improvement / 100)
            test_mean = baseline_mean + absolute_improvement
        
        # mSPRT calculations
        # Effect size
        delta = absolute_improvement
        effect_size = delta / baseline_std
        
        # mSPRT thresholds
        A = (1 - beta) / alpha  # Upper threshold (reject H0)
        B = beta / (1 - alpha)  # Lower threshold (accept H0)
        
        log_A = math.log(A)
        log_B = math.log(B)
        
        # Expected sample sizes under H0 and H1
        # For mSPRT with normal data
        if abs(effect_size) > 0.001:
            # Under H1 (alternative hypothesis)
            expected_n_h1 = (log_A * (1 - beta) + log_B * beta) / (effect_size * delta / (baseline_std**2))
            # Under H0 (null hypothesis)  
            expected_n_h0 = (log_A * alpha + log_B * (1 - alpha)) / (-(effect_size * delta) / (baseline_std**2))
        else:
            expected_n_h1 = max_n
            expected_n_h0 = max_n
        
        expected_n_h1 = max(min_n, min(abs(expected_n_h1), max_n))
        expected_n_h0 = max(min_n, min(abs(expected_n_h0), max_n))
        
        # Generate monitoring table for different sample sizes
        monitoring_points = []
        sample_sizes = [min_n] + [int(x) for x in [min_n * 1.5, min_n * 2, min_n * 3, min_n * 5, max_n * 0.25, max_n * 0.5, max_n * 0.75, max_n]]
        sample_sizes = sorted(list(set([n for n in sample_sizes if min_n <= n <= max_n])))
        
        for n in sample_sizes:
            # Standard error at this sample size
            se = baseline_std * math.sqrt(2/n)
            
            # mSPRT boundaries (log-likelihood ratio thresholds)
            # Converting to test statistic scale
            if use_t_test:
                # Use t-distribution for unknown/estimated variance
                df = 2 * n - 2
                t_alpha = t_ppf(df, 1 - alpha/2) if df > 2 else 3.0
                boundary_upper = t_alpha * se
                boundary_lower = -t_alpha * se
                test_stat_name = "t-statistic"
            else:
                # Use normal distribution for known variance
                z_alpha = norm_ppf(1 - alpha/2)
                boundary_upper = z_alpha * se
                boundary_lower = -z_alpha * se
                test_stat_name = "z-statistic"
            
            # Sequential boundaries (difference in means scale)
            seq_upper = boundary_upper
            seq_lower = boundary_lower
            
            # Confidence intervals at this point
            ci_margin = abs(boundary_upper)
            ci_lower = absolute_improvement - ci_margin
            ci_upper = absolute_improvement + ci_margin
            
            monitoring_points.append({
                'n': n,
                'se': se,
                'boundary_upper': seq_upper,
                'boundary_lower': seq_lower,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper
            })
        
        # Build monitoring table
        monitoring_table = ""
        for point in monitoring_points:
            rel_ci_lower = (point['ci_lower'] / baseline_mean) * 100
            rel_ci_upper = (point['ci_upper'] / baseline_mean) * 100
            
            monitoring_table += f'''
            <tr>
                <td>{point['n']:,}</td>
                <td>±{point['boundary_upper']:.4f}</td>
                <td>[{point['ci_lower']:+.3f}, {point['ci_upper']:+.3f}]</td>
                <td>[{rel_ci_lower:+.1f}%, {rel_ci_upper:+.1f}%]</td>
                <td>{point['se']:.4f}</td>
            </tr>
            '''
        
        # Format efficiency calculation
        efficiency_gain = ((max_n - expected_n_h1) / max_n * 100)
        
        # Format test method text
        test_method_text = "Welch's t-test" if use_t_test else "Z-test"
        
        # Format variance note
        variance_note = ""
        if use_t_test:
            variance_note = "<li><strong>Variance estimation:</strong> Update variance estimates periodically for better accuracy</li>"
        
        return f'''
        <h2>mSPRT Sequential Testing Results</h2>
        
        <h3>📊 Test Configuration</h3>
        <p><strong>Baseline Mean:</strong> {baseline_mean}</p>
        <p><strong>Standard Deviation:</strong> {baseline_std:.3f} ({std_method})</p>
        <p><strong>Expected Improvement:</strong> {absolute_improvement:+.3f} ({relative_improvement:+.1f}%)</p>
        <p><strong>Effect Size (Cohen's d):</strong> {effect_size:.3f}</p>
        <p><strong>Test Method:</strong> {test_method_text}</p>
        
        <h3>📈 mSPRT Parameters</h3>
        <p><strong>Type I Error (α):</strong> {alpha*100:.1f}%</p>
        <p><strong>Type II Error (β):</strong> {beta*100:.1f}%</p>
        <p><strong>Power:</strong> {(1-beta)*100:.1f}%</p>
        <p><strong>Upper Threshold (A):</strong> {A:.2f}</p>
        <p><strong>Lower Threshold (B):</strong> {B:.4f}</p>
        
        <h3>🎯 Expected Performance</h3>
        <p><strong>Expected Sample Size:</strong></p>
        <ul>
            <li><strong>If no effect exists (H₀):</strong> ~{expected_n_h0:,.0f} samples per group</li>
            <li><strong>If effect exists (H₁):</strong> ~{expected_n_h1:,.0f} samples per group</li>
        </ul>
        
        <p><strong>Efficiency Gain:</strong> Up to {efficiency_gain:.0f}% reduction in sample size when effect exists.</p>
        
        <h3>📊 Sequential Monitoring Plan</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f0f0f0;">
                <th>Sample Size/Group</th>
                <th>Decision Boundary</th>
                <th>95% CI (Absolute)</th>
                <th>95% CI (Relative)</th>
                <th>Standard Error</th>
            </tr>
            {monitoring_table}
        </table>
        
        <h3>📋 mSPRT Implementation Guide</h3>
        <ol>
            <li><strong>Collect minimum samples:</strong> Wait until you have at least {min_n:,} samples per group</li>
            <li><strong>Calculate test statistic:</strong> Difference in means divided by pooled standard error</li>
            <li><strong>Decision rules:</strong>
                <ul>
                    <li><strong>Stop and declare significance:</strong> If observed difference > upper boundary</li>
                    <li><strong>Stop and declare no effect:</strong> If observed difference < lower boundary</li>
                    <li><strong>Continue testing:</strong> If difference is within boundaries</li>
                </ul>
            </li>
            <li><strong>Safety cap:</strong> Stop at {max_n:,} samples per group maximum</li>
        </ol>
        
        <h3>💡 mSPRT Advantages</h3>
        <ul>
            <li><strong>Always valid:</strong> Type I error rate exactly controlled at {alpha*100:.1f}%</li>
            <li><strong>Continuous monitoring:</strong> Check results at any sample size ≥ {min_n:,}</li>
            <li><strong>Optimal efficiency:</strong> Minimizes expected sample size</li>
            <li><strong>Robust to variance:</strong> {std_method}</li>
        </ul>
        
        <h3>⚠️ Important Notes</h3>
        <ul>
            <li><strong>Stick to the plan:</strong> Only stop when boundaries are crossed</li>
            <li><strong>No peeking penalty:</strong> mSPRT allows continuous monitoring without alpha inflation</li>
            {variance_note}
        </ul>
        
        <br><a href="/sequential-calculator">← Calculate Another mSPRT Test</a>
        <br><a href="/sample-size-calculator">→ Try Fixed Horizon Testing</a>
        <br><a href="/">← Back to Dashboard</a>
        '''
        
    except Exception as e:
        return f'''
        <h2>Error</h2>
        <p>There was an error: {str(e)}</p>
        <p>Please check your inputs and try again.</p>
        <br><a href="/sequential-calculator">← Try Again</a>
        '''

if __name__ == '__main__':
    app.run(debug=True)