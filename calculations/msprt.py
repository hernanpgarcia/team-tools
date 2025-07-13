"""
mSPRT (Mixed Sequential Probability Ratio Test) calculations
"""
import math
from .statistics import norm_ppf, t_ppf, calculate_effect_size, estimate_std_dev

def calculate_msprt_plan(baseline_mean, std_known, baseline_std, improvement_type,
                        improvement_value, alpha, beta, max_n, min_n):
    """
    Calculate mSPRT sequential testing plan
    
    Args:
        baseline_mean: Baseline metric mean
        std_known: 'known', 'estimated', or 'unknown'
        baseline_std: Standard deviation value (if known/estimated)
        improvement_type: 'absolute' or 'relative'
        improvement_value: Expected improvement value
        alpha: Type I error rate
        beta: Type II error rate
        max_n: Maximum sample size per group
        min_n: Minimum sample size per group
    
    Returns:
        Dictionary with mSPRT plan and monitoring table
    """
    
    # Handle standard deviation scenarios
    if std_known == 'known':
        std_method = "Known standard deviation"
        use_t_test = False
    elif std_known == 'estimated':
        if baseline_std is None:
            baseline_std = estimate_std_dev(baseline_mean, 'moderate')
        std_method = "Estimated standard deviation (use Welch's t-test)"
        use_t_test = True
    else:  # unknown
        baseline_std = estimate_std_dev(baseline_mean, 'conservative')
        std_method = "Unknown standard deviation (robust estimation)"
        use_t_test = True
    
    # Calculate expected test mean
    if improvement_type == 'absolute':
        absolute_improvement = improvement_value
        test_mean = baseline_mean + absolute_improvement
        relative_improvement = (absolute_improvement / baseline_mean) * 100
    else:  # relative
        relative_improvement = improvement_value
        absolute_improvement = baseline_mean * (relative_improvement / 100)
        test_mean = baseline_mean + absolute_improvement
    
    # Effect size and mSPRT parameters
    delta = absolute_improvement
    effect_size = calculate_effect_size(baseline_mean, test_mean, baseline_std)
    
    # mSPRT thresholds
    A = (1 - beta) / alpha  # Upper threshold (reject H0)
    B = beta / (1 - alpha)  # Lower threshold (accept H0)
    
    log_A = math.log(A)
    log_B = math.log(B)
    
    # Expected sample sizes
    if abs(effect_size) > 0.001:
        expected_n_h1 = (log_A * (1 - beta) + log_B * beta) / (effect_size * delta / (baseline_std**2))
        expected_n_h0 = (log_A * alpha + log_B * (1 - alpha)) / (-(effect_size * delta) / (baseline_std**2))
    else:
        expected_n_h1 = max_n
        expected_n_h0 = max_n
    
    expected_n_h1 = max(min_n, min(abs(expected_n_h1), max_n))
    expected_n_h0 = max(min_n, min(abs(expected_n_h0), max_n))
    
    # Generate monitoring points
    monitoring_points = _generate_monitoring_table(
        baseline_std, absolute_improvement, baseline_mean, alpha, 
        min_n, max_n, use_t_test
    )
    
    return {
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'std_method': std_method,
        'test_mean': test_mean,
        'absolute_improvement': absolute_improvement,
        'relative_improvement': relative_improvement,
        'effect_size': effect_size,
        'use_t_test': use_t_test,
        'alpha': alpha,
        'beta': beta,
        'power': 1 - beta,
        'A': A,
        'B': B,
        'expected_n_h0': expected_n_h0,
        'expected_n_h1': expected_n_h1,
        'max_n': max_n,
        'min_n': min_n,
        'monitoring_points': monitoring_points,
        'efficiency_gain': ((max_n - expected_n_h1) / max_n * 100)
    }

def _generate_monitoring_table(baseline_std, absolute_improvement, baseline_mean, 
                              alpha, min_n, max_n, use_t_test):
    """Generate monitoring table for different sample sizes"""
    monitoring_points = []
    sample_sizes = [min_n] + [int(x) for x in [min_n * 1.5, min_n * 2, min_n * 3, min_n * 5, 
                              max_n * 0.25, max_n * 0.5, max_n * 0.75, max_n]]
    sample_sizes = sorted(list(set([n for n in sample_sizes if min_n <= n <= max_n])))
    
    for n in sample_sizes:
        # Standard error at this sample size
        se = baseline_std * math.sqrt(2/n)
        
        # Calculate boundaries
        if use_t_test:
            df = 2 * n - 2
            t_alpha = t_ppf(df, 1 - alpha/2) if df > 2 else 3.0
            boundary_upper = t_alpha * se
        else:
            z_alpha = norm_ppf(1 - alpha/2)
            boundary_upper = z_alpha * se
        
        # Confidence intervals
        ci_margin = abs(boundary_upper)
        ci_lower = absolute_improvement - ci_margin
        ci_upper = absolute_improvement + ci_margin
        
        rel_ci_lower = (ci_lower / baseline_mean) * 100
        rel_ci_upper = (ci_upper / baseline_mean) * 100
        
        monitoring_points.append({
            'n': n,
            'se': se,
            'boundary_upper': boundary_upper,
            'boundary_lower': -boundary_upper,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'rel_ci_lower': rel_ci_lower,
            'rel_ci_upper': rel_ci_upper
        })
    
    return monitoring_points