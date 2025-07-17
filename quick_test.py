#!/usr/bin/env python3
"""
Quick test to verify essential functionality
"""

def test_calculators():
    """Test that all calculators work"""
    print("Testing calculators...")
    
    # Test fixed horizon
    try:
        from calculations.fixed_horizon import calculate_sample_size
        result = calculate_sample_size(100, 20, 'relative', 5, 0.8, 0.05)
        assert result['sample_size_per_group'] == 252
        print("✅ Fixed horizon calculator works")
    except Exception as e:
        print(f"❌ Fixed horizon calculator failed: {e}")
    
    # Test mSPRT
    try:
        from calculations.msprt import calculate_msprt_plan
        result = calculate_msprt_plan(100, 'known', 20, 'relative', 5, 0.05, 0.2, 1000, 100)
        assert result['A'] == 16.0
        print("✅ mSPRT calculator works")
    except Exception as e:
        print(f"❌ mSPRT calculator failed: {e}")
    
    # Test std calculator
    try:
        from calculations.std_calculator import calculate_std_from_data
        result = calculate_std_from_data([1, 2, 3, 4, 5])
        assert result['n'] == 5
        print("✅ Standard deviation calculator works")
    except Exception as e:
        print(f"❌ Standard deviation calculator failed: {e}")

def test_flask_app():
    """Test that Flask app works"""
    print("\nTesting Flask app...")
    
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Flask app home page works")
            
            response = client.post('/calculate-sample-size', data={
                'baseline_mean': '100',
                'baseline_std': '20',
                'improvement_type': 'relative',
                'relative_improvement': '5',
                'power': '0.8',
                'alpha': '0.05',
                'test_type': 'two-sided'
            })
            assert response.status_code == 200
            print("✅ Flask app calculation works")
    except Exception as e:
        print(f"❌ Flask app failed: {e}")

if __name__ == "__main__":
    print("Quick Test for Team Tools Calculator")
    print("=" * 40)
    
    test_calculators()
    test_flask_app()
    
    print("\n" + "=" * 40)
    print("Quick test completed!")
    print("\nIf all tests above show ✅, your core functionality is working!")