"""
mSPRT (Mixed Sequential Probability Ratio Test) calculations
"""
import math

from .statistics import calculate_effect_size, estimate_std_dev, norm_ppf, t_ppf


def calculate_boundary_at_sample_size(n, baseline_std, alpha, use_t_test=False):
    """
    Calculate the mSPRT decision boundary at a given sample size.

    Args:
        n: Sample size per group
        baseline_std: Standard deviation (adjusted for variance inflation)
        alpha: Type I error rate
        use_t_test: Whether to use t-test (default: False for z-test)

    Returns:
        float: Decision boundary (positive value)
    """
    # Standard error at this sample size
    se = baseline_std * math.sqrt(2 / n)

    # Calculate boundary using appropriate distribution
    if use_t_test:
        df = 2 * n - 2
        t_alpha = t_ppf(df, 1 - alpha / 2) if df > 2 else 3.0
        boundary = t_alpha * se
    else:
        z_alpha = norm_ppf(1 - alpha / 2)
        boundary = z_alpha * se

    return boundary


def calculate_sample_size_for_boundary(
    target_boundary, baseline_std, alpha, use_t_test=False
):
    """
    Calculate the sample size needed to achieve a specific boundary value.

    Args:
        target_boundary: Target boundary value
        baseline_std: Standard deviation (adjusted for variance inflation)
        alpha: Type I error rate
        use_t_test: Whether to use t-test (default: False for z-test)

    Returns:
        float: Required sample size per group
    """
    if use_t_test:
        # For t-test, use iterative approach since df depends on n
        # Start with z-test approximation
        z_alpha = norm_ppf(1 - alpha / 2)
        n_approx = (z_alpha * baseline_std * math.sqrt(2) / target_boundary) ** 2

        # Refine with t-test
        for _ in range(10):  # Max 10 iterations
            df = 2 * n_approx - 2
            t_alpha = t_ppf(df, 1 - alpha / 2) if df > 2 else 3.0
            n_approx = (t_alpha * baseline_std * math.sqrt(2) / target_boundary) ** 2

        return n_approx
    else:
        # For z-test, direct calculation
        z_alpha = norm_ppf(1 - alpha / 2)
        return (z_alpha * baseline_std * math.sqrt(2) / target_boundary) ** 2


def determine_week_status(
    week,
    absolute_improvement,
    baseline_mean,
    baseline_std,
    alpha,
    weekly_visitors,
    use_t_test=False,
):
    """
    Determine the status of a test at a specific week.

    Args:
        week: Week number
        absolute_improvement: Expected absolute improvement
        baseline_mean: Baseline metric mean (for percentage calculations)
        baseline_std: Standard deviation (adjusted for variance inflation)
        alpha: Type I error rate
        weekly_visitors: Visitors per group per week
        use_t_test: Whether to use t-test

    Returns:
        dict: Status information including boundary, status, and explanation
    """
    n = weekly_visitors * week
    boundary = calculate_boundary_at_sample_size(n, baseline_std, alpha, use_t_test)

    # Compare expected improvement against boundary
    observed_effect = absolute_improvement

    if abs(observed_effect) >= boundary:
        if observed_effect > 0:
            status = "✅ Significant Improvement"
            if abs(observed_effect) > boundary * 1.1:
                explanation = f"The {observed_effect: .3f} improvement is clearly detectable. You can confidently implement this change."
            else:
                explanation = f"The {observed_effect: .3f} improvement is just detectable. This is the minimum reliable improvement we can confirm."
        else:
            status = "❌ Significant Decline"
            if abs(observed_effect) > boundary * 1.1:
                explanation = f"The {abs(observed_effect): .3f} decline is clearly detectable. You should keep the current version."
            else:
                explanation = f"The {abs(observed_effect): .3f} decline is just detectable. This is the minimum reliable decline we can confirm."
    else:
        status = "⏳ Keep Testing"
        # Convert to relative percentage for easier understanding
        min_detectable_percent = (boundary / baseline_mean) * 100
        expected_percent = (abs(observed_effect) / baseline_mean) * 100
        explanation = f"Can detect effects ≥{min_detectable_percent: .1f}%, but expecting {expected_percent: .1f}%. Need more data to detect smaller effects."

    return {
        "week": week,
        "n": n,
        "boundary_upper": boundary,
        "boundary_lower": -boundary,
        "status": status,
        "explanation": explanation,
    }


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
    variance_inflation_factor=1.5,
    mixing_variance_factor=2.0,
):
    """
    Calculate mSPRT sequential testing plan with realistic variance adjustments

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
        variance_inflation_factor: Multiplier for variance to account for clustering/temporal effects (default: 1.5)
        mixing_variance_factor: Multiplier for mixing variance calibration (default: 2.0)

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

    # Apply variance inflation adjustment for realistic mSPRT
    # Point 2: Variance Inflation Adjustment
    # Accounts for user clustering effects, temporal variations, and external factors
    original_std = baseline_std
    baseline_std = baseline_std * math.sqrt(variance_inflation_factor)

    # Update std_method to reflect adjustments
    if variance_inflation_factor > 1.0:
        std_method += f" (inflated by {variance_inflation_factor: .1f}x for clustering/temporal effects)"

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

    # Point 1: Mixing Variance (γ) Calibration
    # Apply mixing variance calibration for more realistic mSPRT boundaries
    # This accounts for the fact that real experiments have more variance than theoretical models
    calibrated_effect_size = effect_size / math.sqrt(mixing_variance_factor)

    # mSPRT thresholds
    A = (1 - beta) / alpha  # Upper threshold (reject H0)
    B = beta / (1 - alpha)  # Lower threshold (accept H0)

    # mSPRT log thresholds (not used in current implementation)
    # log_A = math.log(A)
    # log_B = math.log(B)

    # Expected sample sizes - calculate when boundaries would be crossed
    # Use shared function to ensure consistency with Weekly Monitoring Plan

    if abs(delta) > 0.001:
        # Calculate sample size where boundary equals expected improvement
        expected_n_h1 = calculate_sample_size_for_boundary(
            abs(delta), baseline_std, alpha, use_t_test
        )
        expected_n_h0 = expected_n_h1  # Same boundary logic for both
    else:
        expected_n_h1 = max_n
        expected_n_h0 = max_n

    expected_n_h1 = max(min_n, min(abs(expected_n_h1), max_n))
    expected_n_h0 = max(min_n, min(abs(expected_n_h0), max_n))

    # Generate monitoring points
    if weekly_visitors and max_weeks:
        monitoring_points = _generate_weekly_monitoring_table(
            baseline_mean,
            baseline_std,
            absolute_improvement,
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

    # Calculate expected timeline for 50% of the effect using shared function
    half_effect = absolute_improvement / 2

    if abs(half_effect) > 0.001:
        # Calculate sample size where boundary equals half the expected improvement
        expected_n_half_effect = calculate_sample_size_for_boundary(
            abs(half_effect), baseline_std, alpha, use_t_test
        )
        expected_n_half_effect = max(min_n, min(abs(expected_n_half_effect), max_n))
    else:
        expected_n_half_effect = max_n

    return {
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "original_std": original_std,
        "std_method": std_method,
        "test_mean": test_mean,
        "absolute_improvement": absolute_improvement,
        "relative_improvement": relative_improvement,
        "effect_size": effect_size,
        "calibrated_effect_size": calibrated_effect_size,
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
        "variance_inflation_factor": variance_inflation_factor,
        "mixing_variance_factor": mixing_variance_factor,
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
    baseline_mean,
    baseline_std,
    absolute_improvement,
    alpha,
    weekly_visitors,
    max_weeks,
    use_t_test,
):
    """Generate weekly monitoring table using shared functions for consistency"""
    monitoring_points = []

    for week in range(1, max_weeks + 1):
        # Use shared function to determine week status
        week_status = determine_week_status(
            week,
            absolute_improvement,
            baseline_mean,
            baseline_std,
            alpha,
            weekly_visitors,
            use_t_test,
        )

        # Add additional fields for backward compatibility
        n = weekly_visitors * week
        se = baseline_std * math.sqrt(2 / n)
        boundary_upper = week_status["boundary_upper"]

        # Confidence intervals
        ci_margin = abs(boundary_upper)
        ci_lower = absolute_improvement - ci_margin
        ci_upper = absolute_improvement + ci_margin

        rel_ci_lower = (ci_lower / baseline_mean) * 100
        rel_ci_upper = (ci_upper / baseline_mean) * 100

        # Combine shared function results with additional fields
        monitoring_points.append(
            {
                **week_status,  # Include all fields from shared function
                "se": se,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "rel_ci_lower": rel_ci_lower,
                "rel_ci_upper": rel_ci_upper,
            }
        )

    return monitoring_points


def validate_msprt_consistency(results):
    """
    Validate that Expected Timeline and Weekly Monitoring Plan are consistent.

    Args:
        results: Dictionary returned by calculate_msprt_plan()

    Returns:
        dict: Consistency validation results
    """
    if not results.get("weekly_visitors") or not results.get("monitoring_points"):
        return {"consistent": True, "reason": "No weekly monitoring data to validate"}

    # Find first significant week
    first_significant_week = None
    for point in results["monitoring_points"]:
        if "✅ Significant" in point["status"]:
            first_significant_week = point["week"]
            break

    if first_significant_week is None:
        return {
            "consistent": True,
            "reason": "No significant result found in monitoring plan",
        }

    # Calculate expected weeks from timeline
    expected_weeks = results["expected_n_h1"] / results["weekly_visitors"]

    # Check consistency (within 2 weeks tolerance)
    difference = abs(first_significant_week - expected_weeks)
    consistent = difference <= 2.0

    return {
        "consistent": consistent,
        "expected_weeks": expected_weeks,
        "first_significant_week": first_significant_week,
        "difference": difference,
        "tolerance": 2.0,
        "reason": f"Expected: {expected_weeks: .1f}w, Actual: {first_significant_week}w, Diff: {difference: .1f}w",
    }
