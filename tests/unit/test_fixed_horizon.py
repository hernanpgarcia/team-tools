"""
Unit tests for fixed horizon sample size calculations
"""

import pytest
import math
from calculations.fixed_horizon import calculate_sample_size


class TestFixedHorizonCalculator:
    """Test suite for fixed horizon sample size calculations"""
    
    def test_valid_relative_improvement(self):
        """Test calculation with valid relative improvement"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.05
        )
        
        assert result is not None
        assert result['sample_size_per_group'] > 0
        assert result['total_sample_size'] == result['sample_size_per_group'] * 2
        assert result['baseline_mean'] == 100
        assert result['baseline_std'] == 20
        assert result['test_mean'] == 105  # 100 + 5%
        assert result['absolute_improvement'] == 5
        assert result['relative_improvement'] == 5
        assert result['power'] == 0.8
        assert result['alpha'] == 0.05
        assert result['std_estimated'] == False
        
    def test_valid_absolute_improvement(self):
        """Test calculation with valid absolute improvement"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='absolute',
            improvement_value=5,
            power=0.8,
            alpha=0.05
        )
        
        assert result is not None
        assert result['sample_size_per_group'] > 0
        assert result['test_mean'] == 105  # 100 + 5
        assert result['absolute_improvement'] == 5
        assert result['relative_improvement'] == 5  # 5/100 * 100 = 5%
        
    def test_estimated_std_deviation(self):
        """Test calculation when std deviation is not provided"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=None,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.05
        )
        
        assert result is not None
        assert result['std_estimated'] == True
        assert result['baseline_std'] == 50  # Conservative estimate: 50% of mean
        
    def test_one_sided_vs_two_sided(self):
        """Test difference between one-sided and two-sided tests"""
        result_two_sided = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.05,
            test_type='two-sided'
        )
        
        result_one_sided = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.05,
            test_type='one-sided'
        )
        
        # One-sided test should require smaller sample size
        assert result_one_sided['sample_size_per_group'] < result_two_sided['sample_size_per_group']
        
    def test_power_effect_on_sample_size(self):
        """Test that higher power requires larger sample size"""
        result_low_power = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.7,
            alpha=0.05
        )
        
        result_high_power = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.9,
            alpha=0.05
        )
        
        assert result_high_power['sample_size_per_group'] > result_low_power['sample_size_per_group']
        
    def test_alpha_effect_on_sample_size(self):
        """Test that lower alpha requires larger sample size"""
        result_high_alpha = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.10
        )
        
        result_low_alpha = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.01
        )
        
        assert result_low_alpha['sample_size_per_group'] > result_high_alpha['sample_size_per_group']
        
    def test_effect_size_calculation(self):
        """Test that effect size is calculated correctly"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='absolute',
            improvement_value=5,
            power=0.8,
            alpha=0.05
        )
        
        # Effect size should be |improvement| / std_dev
        expected_effect_size = 5 / 20
        assert abs(result['effect_size'] - expected_effect_size) < 0.001
        
    def test_confidence_intervals(self):
        """Test that confidence intervals are calculated"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=5,
            power=0.8,
            alpha=0.05
        )
        
        assert 'effect_size_ci_lower' in result
        assert 'effect_size_ci_upper' in result
        assert result['effect_size_ci_lower'] < result['effect_size']
        assert result['effect_size_ci_upper'] > result['effect_size']
        
    # Error cases
    def test_negative_baseline_mean(self):
        """Test error handling for negative baseline mean"""
        with pytest.raises(ValueError, match="Baseline mean must be positive"):
            calculate_sample_size(
                baseline_mean=-10,
                baseline_std=20,
                improvement_type='relative',
                improvement_value=5,
                power=0.8,
                alpha=0.05
            )
            
    def test_negative_baseline_std(self):
        """Test error handling for negative baseline std"""
        with pytest.raises(ValueError, match="Baseline standard deviation must be positive"):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=-5,
                improvement_type='relative',
                improvement_value=5,
                power=0.8,
                alpha=0.05
            )
            
    def test_invalid_power_values(self):
        """Test error handling for invalid power values"""
        with pytest.raises(ValueError, match="Power must be between 0 and 1"):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type='relative',
                improvement_value=5,
                power=1.5,
                alpha=0.05
            )
            
        with pytest.raises(ValueError, match="Power must be between 0 and 1"):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type='relative',
                improvement_value=5,
                power=0,
                alpha=0.05
            )
            
    def test_invalid_alpha_values(self):
        """Test error handling for invalid alpha values"""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type='relative',
                improvement_value=5,
                power=0.8,
                alpha=1.5
            )
            
    def test_zero_improvement_value(self):
        """Test error handling for zero improvement value"""
        with pytest.raises(ValueError, match="Effect size cannot be zero"):
            calculate_sample_size(
                baseline_mean=100,
                baseline_std=20,
                improvement_type='relative',
                improvement_value=0,
                power=0.8,
                alpha=0.05
            )
            
    def test_small_effect_size_large_sample(self):
        """Test that small effect sizes result in large sample sizes"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=0.1,  # Very small improvement
            power=0.8,
            alpha=0.05
        )
        
        assert result['sample_size_per_group'] > 10000  # Should require large sample
        
    def test_large_effect_size_small_sample(self):
        """Test that large effect sizes result in small sample sizes"""
        result = calculate_sample_size(
            baseline_mean=100,
            baseline_std=20,
            improvement_type='relative',
            improvement_value=50,  # Large improvement
            power=0.8,
            alpha=0.05
        )
        
        assert result['sample_size_per_group'] < 100  # Should require small sample
        
    def test_reproducibility(self):
        """Test that calculations are reproducible"""
        params = {
            'baseline_mean': 100,
            'baseline_std': 20,
            'improvement_type': 'relative',
            'improvement_value': 5,
            'power': 0.8,
            'alpha': 0.05
        }
        
        result1 = calculate_sample_size(**params)
        result2 = calculate_sample_size(**params)
        
        assert result1['sample_size_per_group'] == result2['sample_size_per_group']
        assert result1['effect_size'] == result2['effect_size']
        
    @pytest.mark.parametrize("baseline_mean,baseline_std,improvement_type,improvement_value,power,alpha", [
        (50, 10, 'relative', 10, 0.8, 0.05),
        (200, 40, 'absolute', 15, 0.9, 0.01),
        (1000, 100, 'relative', 2, 0.7, 0.10),
        (25, 5, 'absolute', 3, 0.85, 0.02),
    ])
    def test_various_parameter_combinations(self, baseline_mean, baseline_std, improvement_type, improvement_value, power, alpha):
        """Test various parameter combinations"""
        result = calculate_sample_size(
            baseline_mean=baseline_mean,
            baseline_std=baseline_std,
            improvement_type=improvement_type,
            improvement_value=improvement_value,
            power=power,
            alpha=alpha
        )
        
        assert result is not None
        assert result['sample_size_per_group'] > 0
        assert result['total_sample_size'] == result['sample_size_per_group'] * 2
        assert result['baseline_mean'] == baseline_mean
        assert result['baseline_std'] == baseline_std
        assert result['power'] == power
        assert result['alpha'] == alpha