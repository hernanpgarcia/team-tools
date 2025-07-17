"""
mSPRT (Mixed Sequential Probability Ratio Test) calculations
"""
import math

from .statistics import calculate_effect_size, estimate_std_dev, norm_ppf, t_ppf


def calculate_msprt_plan(
    baseline_mean,
    std_known,
    baseline_std,
    improvement_type,
    improvement_value,
    alpha,
    beta,
    max_n,
    min_n,
    weekly_visitors=None,
    max_weeks=None,
):
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
        weekly_visitors: Visitors per group per week (optional)
        max_weeks: Maximum test duration in weeks (optional)

    Returns:
        Dictionary with mSPRT plan and weekly monitoring table
    """

    # Handle standard deviation scenarios
    if std_known == "known":
        std_method = "Known standard deviation"
        use_t_test = False
    elif std_known == "estimated":
        if baseline_std is None:
            baseline_std = estimate_std_dev(baseline_mean, "moderate")
        std_method = "Estimated standard deviation (use Welch's t-test)"
        use_t_test = True
    else:  # unknown
        baseline_std = estimate_std_dev(baseline_mean, "conservative")
        std_method = "Unknown standard deviation (robust estimation)"
        use_t_test = True

    # Calculate expected test mean
    if improvement_type == "absolute":
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
        expected_n_h1 = (log_A * (1 - beta) + log_B * beta) / (
            effect_size * delta / (baseline_std**2)
        )
        expected_n_h0 = (log_A * alpha + log_B * (1 - alpha)) / (
            -(effect_size * delta) / (baseline_std**2)
        )
    else:
        expected_n_h1 = max_n
        expected_n_h0 = max_n

    expected_n_h1 = max(min_n, min(abs(expected_n_h1), max_n))
    expected_n_h0 = max(min_n, min(abs(expected_n_h0), max_n))

    # Generate monitoring points
    if weekly_visitors and max_weeks:
        monitoring_points = _generate_weekly_monitoring_table(
            baseline_std,
            absolute_improvement,
            baseline_mean,
            alpha,
            weekly_visitors,
            max_weeks,
            use_t_test,
        )
    else:
        monitoring_points = _generate_monitoring_table(
            baseline_std,
            absolute_improvement,
            baseline_mean,
            alpha,
            min_n,
            max_n,
            use_t_test,
        )

    # Calculate expected timeline for 50% of the effect
    half_effect = absolute_improvement / 2
    half_effect_size = calculate_effect_size(baseline_mean, baseline_mean + half_effect, baseline_std)
    
    if abs(half_effect_size) > 0.001:
        expected_n_half_effect = (log_A * (1 - beta) + log_B * beta) / (
            half_effect_size * half_effect / (baseline_std**2)
        )
        expected_n_half_effect = max(min_n, min(abs(expected_n_half_effect), max_n))
    else:
        expected_n_half_effect = max_n

    return {
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "std_method": std_method,
        "test_mean": test_mean,
        "absolute_improvement": absolute_improvement,
        "relative_improvement": relative_improvement,
        "effect_size": effect_size,
        "use_t_test": use_t_test,
        "alpha": alpha,
        "beta": beta,
        "power": 1 - beta,
        "A": A,
        "B": B,
        "expected_n_h0": expected_n_h0,
        "expected_n_h1": expected_n_h1,
        "expected_n_half_effect": expected_n_half_effect,
        "max_n": max_n,
        "min_n": min_n,
        "monitoring_points": monitoring_points,
        "efficiency_gain": ((max_n - expected_n_h1) / max_n * 100),
        "weekly_visitors": weekly_visitors,
        "max_weeks": max_weeks,
    }


def _generate_monitoring_table(
    baseline_std, absolute_improvement, baseline_mean, alpha, min_n, max_n, use_t_test
):
    """Generate monitoring table for different sample sizes"""
    monitoring_points = []
    sample_sizes = [min_n] + [
        int(x)
        for x in [
            min_n * 1.5,
            min_n * 2,
            min_n * 3,
            min_n * 5,
            max_n * 0.25,
            max_n * 0.5,
            max_n * 0.75,
            max_n,
        ]
    ]
    sample_sizes = sorted(list(set([n for n in sample_sizes if min_n <= n <= max_n])))

    for n in sample_sizes:
        # Standard error at this sample size
        se = baseline_std * math.sqrt(2 / n)

        # Calculate boundaries
        if use_t_test:
            df = 2 * n - 2
            t_alpha = t_ppf(df, 1 - alpha / 2) if df > 2 else 3.0
            boundary_upper = t_alpha * se
        else:
            z_alpha = norm_ppf(1 - alpha / 2)
            boundary_upper = z_alpha * se

        # Confidence intervals
        ci_margin = abs(boundary_upper)
        ci_lower = absolute_improvement - ci_margin
        ci_upper = absolute_improvement + ci_margin

        rel_ci_lower = (ci_lower / baseline_mean) * 100
        rel_ci_upper = (ci_upper / baseline_mean) * 100

        monitoring_points.append(
            {
                "n": n,
                "se": se,
                "boundary_upper": boundary_upper,
                "boundary_lower": -boundary_upper,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "rel_ci_lower": rel_ci_lower,
                "rel_ci_upper": rel_ci_upper,
            }
        )

    return monitoring_points


def _generate_weekly_monitoring_table(
    baseline_std, absolute_improvement, baseline_mean, alpha, weekly_visitors, max_weeks, use_t_test
):
    """Generate weekly monitoring table with simple status explanations"""
    monitoring_points = []
    
    for week in range(1, max_weeks + 1):
        n = weekly_visitors * week
        
        # Standard error at this sample size
        se = baseline_std * math.sqrt(2 / n)
        
        # Calculate boundaries
        if use_t_test:
            df = 2 * n - 2
            t_alpha = t_ppf(df, 1 - alpha / 2) if df > 2 else 3.0
            boundary_upper = t_alpha * se
        else:
            z_alpha = norm_ppf(1 - alpha / 2)
            boundary_upper = z_alpha * se
        
        # Confidence intervals
        ci_margin = abs(boundary_upper)
        ci_lower = absolute_improvement - ci_margin
        ci_upper = absolute_improvement + ci_margin
        
        rel_ci_lower = (ci_lower / baseline_mean) * 100
        rel_ci_upper = (ci_upper / baseline_mean) * 100
        
        # mSPRT decision logic - compare absolute improvement against boundaries
        # For positive improvements, we need the observed difference to exceed the boundary
        observed_effect = absolute_improvement  # This is what we expect to observe if the effect is real
        
        # Decision boundary represents the minimum detectable difference at this sample size
        min_detectable_effect = boundary_upper
        
        # Status based on mSPRT logic
        if abs(observed_effect) >= min_detectable_effect:
            if observed_effect > 0:
                status = "✅ Significant Improvement"
                if abs(observed_effect) > min_detectable_effect * 1.1:  # 10% buffer for "clearly detectable"
                    explanation = f"The {observed_effect:.3f} improvement is clearly detectable. You can confidently implement this change."
                else:
                    explanation = f"The {observed_effect:.3f} improvement is just detectable. This is the minimum reliable improvement we can confirm."
            else:
                status = "❌ Significant Decline"
                if abs(observed_effect) > min_detectable_effect * 1.1:
                    explanation = f"The {abs(observed_effect):.3f} decline is clearly detectable. You should keep the current version."
                else:
                    explanation = f"The {abs(observed_effect):.3f} decline is just detectable. This is the minimum reliable decline we can confirm."
        else:
            status = "⏳ Keep Testing"
            # Convert to relative percentage for easier understanding
            min_detectable_percent = (min_detectable_effect / baseline_mean) * 100
            expected_percent = (abs(observed_effect) / baseline_mean) * 100
            explanation = f"Can detect effects ≥{min_detectable_percent:.1f}%, but expecting {expected_percent:.1f}%. Need more data to detect smaller effects."
        
        monitoring_points.append({
            "week": week,
            "n": n,
            "se": se,
            "boundary_upper": boundary_upper,
            "boundary_lower": -boundary_upper,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "rel_ci_lower": rel_ci_lower,
            "rel_ci_upper": rel_ci_upper,
            "status": status,
            "explanation": explanation,
        })
    
    return monitoring_points
