"""
Unit tests for mSPRT (Mixed Sequential Probability Ratio Test) calculations
"""

import math

import pytest

from calculations.msprt import calculate_msprt_plan


class TestMSPRTCalculator:
    """Test suite for mSPRT calculations"""

    def test_valid_known_std(self):
        """Test mSPRT calculation with known standard deviation"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert result is not None
        assert result["baseline_mean"] == 100
        assert (
            abs(result["baseline_std"] - 20 * math.sqrt(1.5)) < 0.01
        )  # Inflated by 1.5x
        assert (
            result["std_method"]
            == "Known standard deviation (inflated by 1.5x for clustering/temporal effects)"
        )
        assert result["use_t_test"] == False
        assert result["test_mean"] == 105
        assert result["absolute_improvement"] == 5
        assert result["relative_improvement"] == 5
        assert result["alpha"] == 0.05
        assert result["beta"] == 0.2
        assert result["power"] == 0.8  # 1 - beta
        assert result["max_n"] == 1000
        assert result["min_n"] == 100

    def test_valid_estimated_std(self):
        """Test mSPRT calculation with estimated standard deviation"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="estimated",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert result is not None
        assert (
            result["std_method"]
            == "Estimated standard deviation (use Welch's t-test) (inflated by 1.5x for clustering/temporal effects)"
        )
        assert result["use_t_test"] == True

    def test_unknown_std(self):
        """Test mSPRT calculation with unknown standard deviation"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="unknown",
            baseline_std=None,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert result is not None
        assert (
            result["std_method"]
            == "Unknown standard deviation (robust estimation) (inflated by 1.5x for clustering/temporal effects)"
        )
        assert result["use_t_test"] == True
        assert (
            abs(result["baseline_std"] - 50 * math.sqrt(1.5)) < 0.01
        )  # Conservative estimate inflated by 1.5x

    def test_absolute_improvement(self):
        """Test mSPRT calculation with absolute improvement"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="absolute",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert result is not None
        assert result["test_mean"] == 105
        assert result["absolute_improvement"] == 5
        assert result["relative_improvement"] == 5  # 5/100 * 100 = 5%

    def test_thresholds_calculation(self):
        """Test that A and B thresholds are calculated correctly"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        # A = (1 - beta) / alpha
        expected_A = (1 - 0.2) / 0.05
        assert abs(result["A"] - expected_A) < 0.001

        # B = beta / (1 - alpha)
        expected_B = 0.2 / (1 - 0.05)
        assert abs(result["B"] - expected_B) < 0.001

    def test_monitoring_points_generated(self):
        """Test that monitoring points are generated"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert "monitoring_points" in result
        assert len(result["monitoring_points"]) > 0

        # Check first monitoring point
        first_point = result["monitoring_points"][0]
        assert "n" in first_point
        assert "se" in first_point
        assert "boundary_upper" in first_point
        assert "boundary_lower" in first_point
        assert "ci_lower" in first_point
        assert "ci_upper" in first_point

    def test_expected_sample_sizes(self):
        """Test that expected sample sizes are calculated"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert "expected_n_h0" in result
        assert "expected_n_h1" in result
        assert result["expected_n_h0"] >= result["min_n"]
        assert result["expected_n_h1"] >= result["min_n"]
        assert result["expected_n_h0"] <= result["max_n"]
        assert result["expected_n_h1"] <= result["max_n"]

    def test_efficiency_gain_calculation(self):
        """Test that efficiency gain is calculated"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        assert "efficiency_gain" in result
        expected_gain = (
            (result["max_n"] - result["expected_n_h1"]) / result["max_n"] * 100
        )
        assert abs(result["efficiency_gain"] - expected_gain) < 0.001

    def test_monitoring_points_order(self):
        """Test that monitoring points are in ascending order"""
        result = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        sample_sizes = [point["n"] for point in result["monitoring_points"]]
        assert sample_sizes == sorted(sample_sizes)
        assert sample_sizes[0] >= result["min_n"]
        assert sample_sizes[-1] <= result["max_n"]

    def test_different_alpha_beta_combinations(self):
        """Test different alpha and beta combinations"""
        result1 = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.1,  # Lower beta (higher power)
            max_n=1000,
            min_n=100,
        )

        result2 = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            alpha=0.05,
            beta=0.3,  # Higher beta (lower power)
            max_n=1000,
            min_n=100,
        )

        # Higher power should generally require more samples
        assert result1["power"] > result2["power"]

    def test_large_vs_small_effect_size(self):
        """Test behavior with large vs small effect sizes"""
        result_large = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=20,  # Large effect
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        result_small = calculate_msprt_plan(
            baseline_mean=100,
            std_known="known",
            baseline_std=20,
            improvement_type="relative",
            improvement_value=1,  # Small effect
            alpha=0.05,
            beta=0.2,
            max_n=1000,
            min_n=100,
        )

        # Large effect should generally require fewer samples
        assert result_large["expected_n_h1"] < result_small["expected_n_h1"]

    def test_reproducibility(self):
        """Test that calculations are reproducible"""
        params = {
            "baseline_mean": 100,
            "std_known": "known",
            "baseline_std": 20,
            "improvement_type": "relative",
            "improvement_value": 5,
            "alpha": 0.05,
            "beta": 0.2,
            "max_n": 1000,
            "min_n": 100,
        }

        result1 = calculate_msprt_plan(**params)
        result2 = calculate_msprt_plan(**params)

        assert result1["A"] == result2["A"]
        assert result1["B"] == result2["B"]
        assert result1["expected_n_h0"] == result2["expected_n_h0"]
        assert result1["expected_n_h1"] == result2["expected_n_h1"]

    @pytest.mark.parametrize(
        "baseline_mean,std_known,baseline_std,improvement_type,improvement_value,alpha,beta,max_n,min_n",
        [
            (50, "known", 10, "relative", 10, 0.05, 0.2, 500, 50),
            (200, "estimated", 40, "absolute", 15, 0.01, 0.1, 2000, 200),
            (1000, "unknown", None, "relative", 2, 0.10, 0.3, 1000, 100),
        ],
    )
    def test_various_parameter_combinations(
        self,
        baseline_mean,
        std_known,
        baseline_std,
        improvement_type,
        improvement_value,
        alpha,
        beta,
        max_n,
        min_n,
    ):
        """Test various parameter combinations"""
        result = calculate_msprt_plan(
            baseline_mean=baseline_mean,
            std_known=std_known,
            baseline_std=baseline_std,
            improvement_type=improvement_type,
            improvement_value=improvement_value,
            alpha=alpha,
            beta=beta,
            max_n=max_n,
            min_n=min_n,
        )

        assert result is not None
        assert result["baseline_mean"] == baseline_mean
        assert result["alpha"] == alpha
        assert result["beta"] == beta
        assert result["max_n"] == max_n
        assert result["min_n"] == min_n
        assert result["power"] == 1 - beta
        assert len(result["monitoring_points"]) > 0
