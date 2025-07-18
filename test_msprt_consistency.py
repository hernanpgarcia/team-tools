"""
Comprehensive tests to verify consistency between Expected Timeline and Weekly Monitoring Plan
"""
from calculations.msprt import (
    calculate_boundary_at_sample_size,
    calculate_msprt_plan,
    calculate_sample_size_for_boundary,
    determine_week_status,
)


def test_boundary_calculation_consistency():
    """Test that boundary calculations are consistent between functions"""
    baseline_std = 0.05
    alpha = 0.05

    # Test z-test (use_t_test=False)
    n = 1000
    boundary = calculate_boundary_at_sample_size(
        n, baseline_std, alpha, use_t_test=False
    )
    calculated_n = calculate_sample_size_for_boundary(
        boundary, baseline_std, alpha, use_t_test=False
    )

    # Should be very close (within 1%)
    assert abs(calculated_n - n) / n < 0.01, f"Z-test: Expected {n}, got {calculated_n}"

    # Test t-test (use_t_test=True)
    boundary_t = calculate_boundary_at_sample_size(
        n, baseline_std, alpha, use_t_test=True
    )
    calculated_n_t = calculate_sample_size_for_boundary(
        boundary_t, baseline_std, alpha, use_t_test=True
    )

    # Should be very close (within 1%)
    assert (
        abs(calculated_n_t - n) / n < 0.01
    ), f"T-test: Expected {n}, got {calculated_n_t}"


def test_expected_timeline_vs_weekly_monitoring_consistency():
    """Test that Expected Timeline and Weekly Monitoring Plan are consistent"""

    test_scenarios = [
        # (baseline_mean, improvement_value, alpha, beta, weekly_visitors, expected_tolerance)
        (5.0, 1.0, 0.05, 0.2, 1000, 2.0),  # Large effect
        (0.1, 2.0, 0.05, 0.2, 2000, 1.0),  # Small baseline
        (10.0, 0.5, 0.05, 0.05, 1500, 3.0),  # Small effect, high power
        (1.0, 5.0, 0.01, 0.2, 500, 1.5),  # Strict alpha
    ]

    for (
        baseline_mean,
        improvement_value,
        alpha,
        beta,
        weekly_visitors,
        tolerance,
    ) in test_scenarios:
        # Calculate mSPRT plan
        results = calculate_msprt_plan(
            baseline_mean=baseline_mean,
            std_known="unknown",
            baseline_std=None,
            improvement_type="relative",
            improvement_value=improvement_value,
            alpha=alpha,
            beta=beta,
            max_n=100000,
            min_n=1000,
            weekly_visitors=weekly_visitors,
            max_weeks=50,
            variance_inflation_factor=1.5,
            mixing_variance_factor=2.0,
        )

        # Find first significant week in monitoring plan
        first_significant_week = None
        for point in results["monitoring_points"]:
            if "✅ Significant" in point["status"]:
                first_significant_week = point["week"]
                break

        # Calculate expected weeks from timeline
        expected_weeks_h1 = results["expected_n_h1"] / weekly_visitors

        # Test consistency
        if first_significant_week is not None:
            difference = abs(first_significant_week - expected_weeks_h1)
            assert difference <= tolerance, (
                f"Scenario ({baseline_mean}, {improvement_value}%): "
                f"Expected Timeline: {expected_weeks_h1:.1f} weeks, "
                f"First Significant: {first_significant_week} weeks, "
                f"Difference: {difference:.1f} weeks (tolerance: {tolerance})"
            )

        # Test half-effect consistency
        half_effect_weeks = results["expected_n_half_effect"] / weekly_visitors
        # Half effect should take longer than full effect
        assert (
            half_effect_weeks >= expected_weeks_h1
        ), f"Half effect ({half_effect_weeks:.1f}) should take longer than full effect ({expected_weeks_h1:.1f})"


def test_shared_functions_used_consistently():
    """Test that shared functions produce consistent results"""

    # Test parameters
    baseline_mean = 5.0
    baseline_std = 3.0
    absolute_improvement = 0.25
    alpha = 0.05
    weekly_visitors = 1000

    # Test determine_week_status function
    week_status = determine_week_status(
        week=10,
        absolute_improvement=absolute_improvement,
        baseline_mean=baseline_mean,
        baseline_std=baseline_std,
        alpha=alpha,
        weekly_visitors=weekly_visitors,
        use_t_test=False,
    )

    # Verify boundary calculation matches shared function
    n = weekly_visitors * 10
    expected_boundary = calculate_boundary_at_sample_size(
        n, baseline_std, alpha, use_t_test=False
    )

    assert (
        abs(week_status["boundary_upper"] - expected_boundary) < 0.0001
    ), f"Boundary mismatch: expected {expected_boundary}, got {week_status['boundary_upper']}"

    # Test status determination logic
    if absolute_improvement >= expected_boundary:
        assert "✅ Significant" in week_status["status"]
    else:
        assert "⏳ Keep Testing" in week_status["status"]


def test_variance_adjustments_applied_consistently():
    """Test that variance adjustments are applied consistently"""

    # Test with and without variance adjustments
    base_params = {
        "baseline_mean": 5.0,
        "std_known": "unknown",
        "baseline_std": None,
        "improvement_type": "relative",
        "improvement_value": 1.0,
        "alpha": 0.05,
        "beta": 0.2,
        "max_n": 50000,
        "min_n": 1000,
        "weekly_visitors": 1000,
        "max_weeks": 20,
    }

    # No adjustments
    results_no_adj = calculate_msprt_plan(
        **base_params, variance_inflation_factor=1.0, mixing_variance_factor=1.0
    )

    # With adjustments
    results_with_adj = calculate_msprt_plan(
        **base_params, variance_inflation_factor=1.5, mixing_variance_factor=2.0
    )

    # With adjustments should require more time
    assert (
        results_with_adj["expected_n_h1"] > results_no_adj["expected_n_h1"]
    ), "Variance adjustments should increase expected sample size"

    # First significant week should be later with adjustments
    first_sig_no_adj = None
    first_sig_with_adj = None

    for point in results_no_adj["monitoring_points"]:
        if "✅ Significant" in point["status"]:
            first_sig_no_adj = point["week"]
            break

    for point in results_with_adj["monitoring_points"]:
        if "✅ Significant" in point["status"]:
            first_sig_with_adj = point["week"]
            break

    if first_sig_no_adj and first_sig_with_adj:
        assert (
            first_sig_with_adj >= first_sig_no_adj
        ), "Variance adjustments should delay or maintain significance timing"


if __name__ == "__main__":
    # Run tests
    test_boundary_calculation_consistency()
    print("✅ Boundary calculation consistency test passed")

    test_expected_timeline_vs_weekly_monitoring_consistency()
    print("✅ Expected Timeline vs Weekly Monitoring consistency test passed")

    test_shared_functions_used_consistently()
    print("✅ Shared functions consistency test passed")

    test_variance_adjustments_applied_consistently()
    print("✅ Variance adjustments consistency test passed")

    print("\n🎉 All consistency tests passed!")
    print("✅ Expected Timeline and Weekly Monitoring Plan are now consistent")
    print("✅ Shared functions prevent future inconsistencies")
