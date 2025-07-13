"""
Standard Deviation Calculator for A/B Testing Metrics
"""
import math
from .statistics import norm_ppf

def calculate_std_from_data(data_points):
    """
    Calculate standard deviation from a list of data points
    
    Args:
        data_points: List of numeric values
    
    Returns:
        Dictionary with statistical measures
    """
    n = len(data_points)
    if n < 2:
        raise ValueError("Need at least 2 data points")
    
    # Basic statistics
    mean = sum(data_points) / n
    variance = sum((x - mean) ** 2 for x in data_points) / (n - 1)  # Sample variance
    std_dev = math.sqrt(variance)
    
    # Additional useful statistics
    median = sorted(data_points)[n // 2] if n % 2 == 1 else sum(sorted(data_points)[n//2-1:n//2+1]) / 2
    min_val = min(data_points)
    max_val = max(data_points)
    
    # Coefficient of variation
    cv = (std_dev / mean) * 100 if mean != 0 else 0
    
    # Standard error of the mean
    sem = std_dev / math.sqrt(n)
    
    # 95% confidence interval for the mean
    t_critical = 1.96 if n >= 30 else norm_ppf(0.975)  # Approximate for small samples
    ci_margin = t_critical * sem
    ci_lower = mean - ci_margin
    ci_upper = mean + ci_margin
    
    return {
        'n': n,
        'mean': mean,
        'median': median,
        'std_dev': std_dev,
        'variance': variance,
        'min': min_val,
        'max': max_val,
        'cv': cv,
        'sem': sem,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'ci_margin': ci_margin
    }

def estimate_std_from_range(min_val, max_val, method='range_rule'):
    """
    Estimate standard deviation from min/max values
    
    Args:
        min_val: Minimum observed value
        max_val: Maximum observed value
        method: Estimation method ('range_rule', 'six_sigma')
    
    Returns:
        Dictionary with estimated standard deviation
    """
    range_val = max_val - min_val
    
    if method == 'range_rule':
        # Rule of thumb: range ≈ 4 * std_dev
        estimated_std = range_val / 4
        method_name = "Range Rule (Range ÷ 4)"
        accuracy = "Rough estimate"
    elif method == 'six_sigma':
        # Six sigma rule: range ≈ 6 * std_dev
        estimated_std = range_val / 6
        method_name = "Six Sigma Rule (Range ÷ 6)"
        accuracy = "Conservative estimate"
    else:
        raise ValueError("Unknown method")
    
    mean_estimate = (min_val + max_val) / 2
    cv_estimate = (estimated_std / mean_estimate) * 100 if mean_estimate != 0 else 0
    
    return {
        'estimated_std': estimated_std,
        'min_val': min_val,
        'max_val': max_val,
        'range': range_val,
        'method': method_name,
        'accuracy': accuracy,
        'mean_estimate': mean_estimate,
        'cv_estimate': cv_estimate
    }

def estimate_std_from_percentiles(p25, p50, p75):
    """
    Estimate standard deviation from quartiles (more accurate)
    
    Args:
        p25: 25th percentile (Q1)
        p50: 50th percentile (median, Q2)
        p75: 75th percentile (Q3)
    
    Returns:
        Dictionary with estimated standard deviation
    """
    # IQR method: std ≈ IQR / 1.35 (for normal distribution)
    iqr = p75 - p25
    estimated_std = iqr / 1.35
    
    # Alternative: use median absolute deviation approximation
    # Assuming roughly normal, MAD ≈ 0.6745 * std
    mad_based_std = (p75 - p25) / (2 * 0.6745)  # Approximation
    
    return {
        'estimated_std_iqr': estimated_std,
        'estimated_std_mad': mad_based_std,
        'iqr': iqr,
        'q1': p25,
        'median': p50,
        'q3': p75,
        'method': "Interquartile Range (IQR ÷ 1.35)",
        'accuracy': "Good estimate for normal data"
    }

def calculate_std_from_conversion_data(conversions, visitors):
    """
    Calculate standard deviation for conversion rate data
    
    Args:
        conversions: List of conversion counts
        visitors: List of visitor counts (corresponding to conversions)
    
    Returns:
        Dictionary with conversion rate statistics
    """
    if len(conversions) != len(visitors):
        raise ValueError("Conversions and visitors lists must have the same length")
    
    if len(conversions) < 2:
        raise ValueError("Need at least 2 data points")
    
    # Calculate conversion rates for each period
    conversion_rates = []
    for conv, vis in zip(conversions, visitors):
        if vis == 0:
            raise ValueError("Visitor count cannot be zero")
        conversion_rates.append(conv / vis)
    
    # Calculate standard statistics on conversion rates
    n = len(conversion_rates)
    mean_rate = sum(conversion_rates) / n
    
    # Sample standard deviation of conversion rates
    variance = sum((rate - mean_rate) ** 2 for rate in conversion_rates) / (n - 1)
    std_dev = math.sqrt(variance)
    
    # Theoretical standard deviation for a single conversion rate
    # σ = √(p × (1-p) / n) where p is the mean conversion rate and n is average sample size
    avg_visitors = sum(visitors) / len(visitors)
    theoretical_std = math.sqrt(mean_rate * (1 - mean_rate) / avg_visitors)
    
    # Additional statistics
    total_conversions = sum(conversions)
    total_visitors = sum(visitors)
    pooled_rate = total_conversions / total_visitors
    
    # Confidence interval for pooled rate
    pooled_std = math.sqrt(pooled_rate * (1 - pooled_rate) / total_visitors)
    z_critical = 1.96  # 95% CI
    ci_margin = z_critical * pooled_std
    ci_lower = max(0, pooled_rate - ci_margin)
    ci_upper = min(1, pooled_rate + ci_margin)
    
    return {
        'n_periods': n,
        'conversion_rates': conversion_rates,
        'mean_rate': mean_rate,
        'std_dev_observed': std_dev,
        'theoretical_std': theoretical_std,
        'total_conversions': total_conversions,
        'total_visitors': total_visitors,
        'pooled_rate': pooled_rate,
        'pooled_std': pooled_std,
        'avg_visitors_per_period': avg_visitors,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'ci_margin': ci_margin
    }

def estimate_conversion_rate_std(baseline_rate, sample_size):
    """
    Calculate theoretical standard deviation for a conversion rate
    
    Args:
        baseline_rate: Expected conversion rate (as decimal, e.g., 0.05 for 5%)
        sample_size: Number of visitors per group
    
    Returns:
        Dictionary with standard deviation and related metrics
    """
    if baseline_rate <= 0 or baseline_rate >= 1:
        raise ValueError("Conversion rate must be between 0 and 1")
    
    if sample_size <= 0:
        raise ValueError("Sample size must be positive")
    
    # Standard deviation for a conversion rate
    std_dev = math.sqrt(baseline_rate * (1 - baseline_rate) / sample_size)
    
    # Standard error (same as std_dev for conversion rates)
    standard_error = std_dev
    
    # 95% confidence interval
    z_critical = 1.96
    ci_margin = z_critical * standard_error
    ci_lower = max(0, baseline_rate - ci_margin)
    ci_upper = min(1, baseline_rate + ci_margin)
    
    # Minimum detectable effect (MDE) - what change you can reliably detect
    # For 80% power, 5% significance
    z_alpha = 1.96  # 5% significance
    z_beta = 0.84   # 80% power
    
    # MDE for conversion rates (absolute)
    mde_absolute = (z_alpha + z_beta) * math.sqrt(2 * baseline_rate * (1 - baseline_rate) / sample_size)
    mde_relative = (mde_absolute / baseline_rate) * 100
    
    # Sample size needed for different effect sizes
    effect_sizes = [0.05, 0.10, 0.15, 0.20, 0.25]  # 5%, 10%, 15%, 20%, 25% relative
    sample_sizes_needed = []
    
    for effect in effect_sizes:
        delta = baseline_rate * effect  # Absolute effect size
        n_needed = 2 * ((z_alpha + z_beta) ** 2) * baseline_rate * (1 - baseline_rate) / (delta ** 2)
        sample_sizes_needed.append({
            'relative_effect': effect * 100,
            'absolute_effect': delta,
            'sample_size_needed': math.ceil(n_needed)
        })
    
    return {
        'baseline_rate': baseline_rate,
        'sample_size': sample_size,
        'std_dev': std_dev,
        'standard_error': standard_error,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'ci_margin': ci_margin,
        'mde_absolute': mde_absolute,
        'mde_relative': mde_relative,
        'sample_sizes_for_effects': sample_sizes_needed
    }

def sample_size_for_std_estimation(target_precision, confidence_level=0.95):
    """
    Calculate how many samples needed to estimate standard deviation with given precision
    
    Args:
        target_precision: Desired relative precision (e.g., 0.1 for 10% precision)
        confidence_level: Confidence level (default 95%)
    
    Returns:
        Required sample size
    """
    alpha = 1 - confidence_level
    z = norm_ppf(1 - alpha/2)
    
    # Approximation: CV of sample std dev ≈ 1/sqrt(2n)
    # For relative precision p: p = z * (1/sqrt(2n))
    # Solving for n: n = (z/(p*sqrt(2)))^2
    
    n_required = ((z / (target_precision * math.sqrt(2))) ** 2)
    
    return {
        'n_required': math.ceil(n_required),
        'target_precision': target_precision * 100,  # Convert to percentage
        'confidence_level': confidence_level * 100,
        'interpretation': f"With {math.ceil(n_required)} samples, you can estimate the standard deviation within ±{target_precision*100:.1f}% with {confidence_level*100:.0f}% confidence"
    }