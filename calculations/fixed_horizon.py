"""
Fixed horizon sample size calculations
"""
import logging
import math

from .statistics import calculate_effect_size, estimate_std_dev, norm_ppf

logger = logging.getLogger(__name__)


def calculate_sample_size(
    baseline_mean,
    baseline_std,
    improvement_type,
    improvement_value,
    power,
    alpha,
    test_type="two-sided",
):
    """
    Calculate sample size for fixed horizon testing

    Args:
        baseline_mean: Baseline metric mean
        baseline_std: Baseline metric standard deviation (or None)
        improvement_type: 'absolute' or 'relative'
        improvement_value: Expected improvement value
        power: Statistical power (0.8, 0.9, etc.)
        alpha: Significance level (0.05, 0.01, etc.)
        test_type: 'two-sided' or 'one-sided'

    Returns:
        Dictionary with calculation results
    """

    try:
        logger.debug(
            f"Starting sample size calculation with baseline_mean={baseline_mean}, improvement_type={improvement_type}"
        )

        # Validate inputs
        if baseline_mean <= 0:
            raise ValueError("Baseline mean must be positive")
        if baseline_std is not None and baseline_std <= 0:
            raise ValueError("Baseline standard deviation must be positive")
        if not 0 < power < 1:
            raise ValueError("Power must be between 0 and 1")
        if not 0 < alpha < 1:
            raise ValueError("Alpha must be between 0 and 1")

        # Handle unknown standard deviation
        if baseline_std is None:
            baseline_std = estimate_std_dev(baseline_mean, "conservative")
            std_estimated = True
            logger.debug(f"Estimated standard deviation: {baseline_std}")
        else:
            std_estimated = False

        # Calculate expected test mean
        if improvement_type == "absolute":
            absolute_improvement = improvement_value
            test_mean = baseline_mean + absolute_improvement
            relative_improvement = (absolute_improvement / baseline_mean) * 100
        else:  # relative
            relative_improvement = improvement_value
            absolute_improvement = baseline_mean * (relative_improvement / 100)
            test_mean = baseline_mean + absolute_improvement

        logger.debug(
            f"Calculated test_mean={test_mean}, absolute_improvement={absolute_improvement}"
        )

        # Effect size
        effect_size = calculate_effect_size(baseline_mean, test_mean, baseline_std)

        if effect_size == 0:
            raise ValueError(
                "Effect size cannot be zero - improvement value must be non-zero"
            )

        # Critical values
        if test_type == "two-sided":
            z_alpha = norm_ppf(1 - alpha / 2)
        else:
            z_alpha = norm_ppf(1 - alpha)

        z_beta = norm_ppf(power)

        logger.debug(
            f"Critical values: z_alpha={z_alpha}, z_beta={z_beta}, effect_size={effect_size}"
        )

        # Sample size calculation
        sample_size_per_group = 2 * ((z_alpha + z_beta) ** 2) / (effect_size**2)
        sample_size_per_group = math.ceil(sample_size_per_group)
        total_sample_size = sample_size_per_group * 2

        # Confidence intervals
        effect_size_se = math.sqrt(2 / sample_size_per_group)
        effect_size_ci_lower = effect_size - z_alpha * effect_size_se
        effect_size_ci_upper = effect_size + z_alpha * effect_size_se

        logger.debug(
            f"Final calculation: sample_size_per_group={sample_size_per_group}"
        )

        return {
            "baseline_mean": baseline_mean,
            "baseline_std": baseline_std,
            "test_mean": test_mean,
            "absolute_improvement": absolute_improvement,
            "relative_improvement": relative_improvement,
            "effect_size": effect_size,
            "effect_size_ci_lower": effect_size_ci_lower,
            "effect_size_ci_upper": effect_size_ci_upper,
            "sample_size_per_group": sample_size_per_group,
            "total_sample_size": total_sample_size,
            "power": power,
            "alpha": alpha,
            "test_type": test_type,
            "std_estimated": std_estimated,
        }

    except Exception as e:
        logger.error(f"Error in calculate_sample_size: {str(e)}")
        raise
