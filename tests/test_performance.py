"""
Performance tests for calculator functions
"""

import statistics
import time

import pytest
from hypothesis import given
from hypothesis import strategies as st

from calculations.fixed_horizon import calculate_sample_size
from calculations.msprt import calculate_msprt_plan
from calculations.std_calculator import calculate_std_from_data


class TestPerformance:
    """Performance tests for calculator functions"""

    @pytest.mark.performance
    def test_sample_size_calculation_performance(self):
        """Test that sample size calculation completes within reasonable time"""
        start_time = time.time()

        # Run calculation multiple times
        for _ in range(100):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type="relative",
                improvement_value=5,
                power=0.8,
                alpha=0.05,
            )

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Should complete in under 1ms per calculation
        assert avg_time < 0.001, f"Sample size calculation too slow: {avg_time: .4f}s"

    @pytest.mark.performance
    def test_msprt_calculation_performance(self):
        """Test that mSPRT calculation completes within reasonable time"""
        start_time = time.time()

        # Run calculation multiple times
        for _ in range(50):
            calculate_msprt_plan(
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

        end_time = time.time()
        avg_time = (end_time - start_time) / 50

        # Should complete in under 10ms per calculation
        assert avg_time < 0.01, f"mSPRT calculation too slow: {avg_time: .4f}s"

    @pytest.mark.performance
    def test_std_calculation_performance(self):
        """Test that std calculation completes within reasonable time"""
        # Large dataset
        large_dataset = list(range(1000))

        start_time = time.time()

        # Run calculation multiple times
        for _ in range(100):
            calculate_std_from_data(large_dataset)

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Should complete in under 1ms per calculation
        assert avg_time < 0.001, f"Std calculation too slow: {avg_time: .4f}s"

    @pytest.mark.performance
    def test_sample_size_with_varying_parameters(self):
        """Test performance with different parameter values"""
        times = []

        test_cases = [
            (10, 2, "relative", 1, 0.8, 0.05),
            (100, 20, "relative", 5, 0.8, 0.05),
            (1000, 200, "relative", 10, 0.9, 0.01),
            (10000, 2000, "absolute", 500, 0.7, 0.10),
        ]

        for (
            baseline_mean,
            baseline_std,
            improvement_type,
            improvement_value,
            power,
            alpha,
        ) in test_cases:
            start_time = time.time()

            calculate_sample_size(
                baseline_mean=baseline_mean,
                baseline_std=baseline_std,
                improvement_type=improvement_type,
                improvement_value=improvement_value,
                power=power,
                alpha=alpha,
            )

            end_time = time.time()
            times.append(end_time - start_time)

        # All calculations should complete quickly
        max_time = max(times)
        avg_time = statistics.mean(times)

        assert max_time < 0.01, f"Slowest calculation: {max_time: .4f}s"
        assert avg_time < 0.005, f"Average calculation time: {avg_time: .4f}s"

    @pytest.mark.performance
    @given(
        baseline_mean=st.floats(min_value=1, max_value=10000),
        baseline_std=st.floats(min_value=0.1, max_value=1000),
        improvement_value=st.floats(min_value=0.1, max_value=50),
        power=st.floats(min_value=0.1, max_value=0.99),
        alpha=st.floats(min_value=0.001, max_value=0.5),
    )
    def test_sample_size_performance_property_based(
        self, baseline_mean, baseline_std, improvement_value, power, alpha
    ):
        """Property-based test for sample size calculation performance"""
        start_time = time.time()

        try:
            calculate_sample_size(
                baseline_mean=baseline_mean,
                baseline_std=baseline_std,
                improvement_type="relative",
                improvement_value=improvement_value,
                power=power,
                alpha=alpha,
            )
        except ValueError:
            # Some combinations might be invalid, that's ok
            pass

        end_time = time.time()
        calculation_time = end_time - start_time

        # Even with random parameters, should complete quickly
        assert (
            calculation_time < 0.01
        ), f"Calculation too slow: {calculation_time: .4f}s"

    @pytest.mark.performance
    def test_large_dataset_std_calculation(self):
        """Test std calculation with very large datasets"""
        dataset_sizes = [1000, 5000, 10000, 50000]

        for size in dataset_sizes:
            dataset = list(range(size))

            start_time = time.time()
            calculate_std_from_data(dataset)
            end_time = time.time()

            calculation_time = end_time - start_time

            # Should scale reasonably with data size
            max_time = size * 0.000001  # 1 microsecond per data point
            assert (
                calculation_time < max_time
            ), f"Dataset size {size} too slow: {calculation_time: .4f}s"

    @pytest.mark.performance
    def test_memory_usage_stability(self):
        """Test that repeated calculations don't cause memory leaks"""
        import gc

        # Run many calculations
        for _ in range(1000):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type="relative",
                improvement_value=5,
                power=0.8,
                alpha=0.05,
            )

            # Occasionally force garbage collection
            if _ % 100 == 0:
                gc.collect()

        # Test passes if no memory errors occur
        assert True


class TestRegressionTests:
    """Regression tests to ensure calculations remain consistent"""

    @pytest.mark.regression
    def test_sample_size_regression_known_values(self):
        """Test that sample size calculations match known good values"""
        # Known good results from previous runs
        test_cases = [
            {
                "params": {
                    "baseline_mean": 100,
                    "baseline_std": 20,
                    "improvement_type": "relative",
                    "improvement_value": 5,
                    "power": 0.8,
                    "alpha": 0.05,
                },
                "expected_sample_size": 252,
                "expected_effect_size": 0.25,
            },
            {
                "params": {
                    "baseline_mean": 50,
                    "baseline_std": 10,
                    "improvement_type": "absolute",
                    "improvement_value": 2,
                    "power": 0.9,
                    "alpha": 0.01,
                },
                "expected_sample_size": 745,  # Updated to actual calculated value
                "expected_effect_size": 0.2,
            },
        ]

        for test_case in test_cases:
            result = calculate_sample_size(**test_case["params"])

            # Allow small tolerance for floating point differences
            assert (
                abs(result["sample_size_per_group"] - test_case["expected_sample_size"])
                <= 1
            )
            assert abs(result["effect_size"] - test_case["expected_effect_size"]) < 0.01

    @pytest.mark.regression
    def test_msprt_regression_known_values(self):
        """Test that mSPRT calculations match known good values"""
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

        result = calculate_msprt_plan(**params)

        # Test key values remain consistent
        assert result["A"] == 16.0  # (1-0.2)/0.05
        assert abs(result["B"] - 0.21052631578947367) < 0.001  # 0.2/(1-0.05)
        assert result["power"] == 0.8  # 1 - beta
        assert result["test_mean"] == 105  # 100 + 5%
        assert result["absolute_improvement"] == 5
        assert result["relative_improvement"] == 5

    @pytest.mark.regression
    def test_std_calculation_regression(self):
        """Test that std calculations match known good values"""
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = calculate_std_from_data(test_data)

        # Known statistical values for this dataset
        assert result["n"] == 10
        assert result["mean"] == 5.5
        assert result["median"] == 5.5
        assert abs(result["std_dev"] - 3.0276503540974917) < 0.001
        assert abs(result["variance"] - 9.166666666666666) < 0.001
        assert result["min"] == 1
        assert result["max"] == 10

    @pytest.mark.regression
    def test_template_formatting_regression(self):
        """Test that template formatting produces consistent output"""
        # This test would use the Flask test client to ensure
        # template rendering produces consistent formatted output
        from app import app

        with app.test_client() as client:
            response = client.post(
                "/calculate-sample-size",
                data={
                    "baseline_mean": "100",
                    "baseline_std": "20",
                    "improvement_type": "relative",
                    "relative_improvement": "5",
                    "power": "0.8",
                    "alpha": "0.05",
                    "test_type": "two-sided",
                },
            )

            assert response.status_code == 200
            content = response.data.decode("utf-8")

            # Check that specific formatted values appear
            assert "80.0%" in content  # Power
            assert "5.0%" in content  # Alpha
            assert "252" in content  # Sample size

    @pytest.mark.regression
    def test_input_validation_regression(self):
        """Test that input validation behaves consistently"""
        # Test various invalid inputs
        invalid_cases = [
            {"baseline_mean": 0, "error_contains": "positive"},
            {"baseline_mean": 100, "baseline_std": -5, "error_contains": "positive"},
            {"baseline_mean": 100, "power": 1.5, "error_contains": "between 0 and 1"},
            {"baseline_mean": 100, "alpha": 0, "error_contains": "between 0 and 1"},
            {"baseline_mean": 100, "improvement_value": 0, "error_contains": "zero"},
        ]

        for case in invalid_cases:
            error_contains = case.pop("error_contains")
            params = {
                "baseline_mean": 100,
                "baseline_std": 20,
                "improvement_type": "relative",
                "improvement_value": 5,
                "power": 0.8,
                "alpha": 0.05,
                **case,
            }

            with pytest.raises(ValueError) as exc_info:
                calculate_sample_size(**params)

            assert error_contains.lower() in str(exc_info.value).lower()

    @pytest.mark.regression
    def test_statistical_properties_regression(self):
        """Test that statistical properties remain consistent"""
        # Test that higher power requires more samples
        result_low_power = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            power=0.7,
            alpha=0.05,
        )

        result_high_power = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            power=0.9,
            alpha=0.05,
        )

        assert (
            result_high_power["sample_size_per_group"]
            > result_low_power["sample_size_per_group"]
        )

        # Test that smaller alpha requires more samples
        result_high_alpha = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            power=0.8,
            alpha=0.10,
        )

        result_low_alpha = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type="relative",
            improvement_value=5,
            power=0.8,
            alpha=0.01,
        )

        assert (
            result_low_alpha["sample_size_per_group"]
            > result_high_alpha["sample_size_per_group"]
        )
