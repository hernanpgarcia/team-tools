"""
Statistical functions for A/B testing calculations
"""
import math


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


def calculate_effect_size(baseline_mean, test_mean, baseline_std):
    """Calculate Cohen's d effect size"""
    return abs(test_mean - baseline_mean) / baseline_std


def estimate_std_dev(baseline_mean, method="conservative"):
    """Estimate standard deviation when unknown"""
    if method == "conservative":
        return abs(baseline_mean) * 0.5  # 50% CV
    elif method == "moderate":
        return abs(baseline_mean) * 0.3  # 30% CV
    else:
        return abs(baseline_mean) * 0.2  # 20% CV
