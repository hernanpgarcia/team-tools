"""
Integration tests for Flask routes
"""


import pytest
from bs4 import BeautifulSoup

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client


class TestHomeRoute:
    """Test home page route"""

    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Team Tools" in response.data

    def test_home_page_has_navigation(self, client):
        """Test that home page has navigation links"""
        response = client.get("/")
        soup = BeautifulSoup(response.data, "html.parser")

        # Check for calculator links
        links = soup.find_all("a")
        link_hrefs = [link.get("href") for link in links]

        assert "/sample-size-calculator" in link_hrefs
        assert "/sequential-calculator" in link_hrefs
        assert "/std-calculator" in link_hrefs


class TestSampleSizeCalculator:
    """Test sample size calculator routes"""

    def test_sample_size_form_loads(self, client):
        """Test that sample size form loads"""
        response = client.get("/sample-size-calculator")
        assert response.status_code == 200
        assert b"Sample Size Calculator" in response.data

    def test_valid_sample_size_calculation(self, client):
        """Test valid sample size calculation"""
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
        assert b"Sample Size Calculator Results" in response.data
        soup = BeautifulSoup(response.data, "html.parser")

        # Check that results are displayed
        assert soup.find(string="Baseline Mean:")
        assert soup.find(string="Standard Deviation:")
        assert "Sample Size Requirements" in response.data.decode("utf-8")

    def test_sample_size_with_missing_baseline_mean(self, client):
        """Test error handling for missing baseline mean"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_std": "20",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "power": "0.8",
                "alpha": "0.05",
                "test_type": "two-sided",
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_sample_size_with_invalid_power(self, client):
        """Test error handling for invalid power"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "power": "1.5",  # Invalid power
                "alpha": "0.05",
                "test_type": "two-sided",
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_sample_size_with_zero_improvement(self, client):
        """Test error handling for zero improvement"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "improvement_type": "relative",
                "relative_improvement": "0",  # Zero improvement
                "power": "0.8",
                "alpha": "0.05",
                "test_type": "two-sided",
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_sample_size_absolute_improvement(self, client):
        """Test sample size calculation with absolute improvement"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "improvement_type": "absolute",
                "absolute_improvement": "5",
                "power": "0.8",
                "alpha": "0.05",
                "test_type": "two-sided",
            },
        )

        assert response.status_code == 200
        assert b"Sample Size Calculator Results" in response.data

    def test_sample_size_one_sided_test(self, client):
        """Test sample size calculation with one-sided test"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "power": "0.8",
                "alpha": "0.05",
                "test_type": "one-sided",
            },
        )

        assert response.status_code == 200
        assert b"Sample Size Calculator Results" in response.data

    def test_sample_size_without_std(self, client):
        """Test sample size calculation without providing std"""
        response = client.post(
            "/calculate-sample-size",
            data={
                "baseline_mean": "100",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "power": "0.8",
                "alpha": "0.05",
                "test_type": "two-sided",
            },
        )

        assert response.status_code == 200
        assert b"Sample Size Calculator Results" in response.data
        # Should show that std was estimated
        assert b"estimated" in response.data.lower()


class TestMSPRTCalculator:
    """Test mSPRT calculator routes"""

    def test_msprt_form_loads(self, client):
        """Test that mSPRT form loads"""
        response = client.get("/sequential-calculator")
        assert response.status_code == 200
        assert b"Sequential" in response.data or b"mSPRT" in response.data

    def test_valid_msprt_calculation(self, client):
        """Test valid mSPRT calculation"""
        response = client.post(
            "/calculate-msprt",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "std_known": "known",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "alpha": "0.05",
                "beta": "0.2",
                "max_n": "1000",
                "min_n": "100",
            },
        )

        assert response.status_code == 200
        assert b"mSPRT" in response.data or b"Sequential" in response.data

    def test_msprt_with_unknown_std(self, client):
        """Test mSPRT calculation with unknown std"""
        response = client.post(
            "/calculate-msprt",
            data={
                "baseline_mean": "100",
                "std_known": "unknown",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "alpha": "0.05",
                "beta": "0.2",
                "max_n": "1000",
                "min_n": "100",
            },
        )

        assert response.status_code == 200
        assert b"mSPRT" in response.data or b"Sequential" in response.data

    def test_msprt_with_invalid_sample_sizes(self, client):
        """Test error handling for invalid sample sizes"""
        response = client.post(
            "/calculate-msprt",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "std_known": "known",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "alpha": "0.05",
                "beta": "0.2",
                "max_n": "100",  # max_n <= min_n
                "min_n": "100",
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()


class TestStdCalculator:
    """Test standard deviation calculator routes"""

    def test_std_form_loads(self, client):
        """Test that std calculator form loads"""
        response = client.get("/std-calculator")
        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_std_from_data_points(self, client):
        """Test std calculation from data points"""
        response = client.post(
            "/calculate-std-from-data", data={"data_points": "1,2,3,4,5,6,7,8,9,10"}
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data
        assert b"Calculated from" in response.data

    def test_std_from_data_newline_separated(self, client):
        """Test std calculation from newline-separated data"""
        response = client.post(
            "/calculate-std-from-data", data={"data_points": "1\\n2\\n3\\n4\\n5"}
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_std_from_data_space_separated(self, client):
        """Test std calculation from space-separated data"""
        response = client.post(
            "/calculate-std-from-data", data={"data_points": "1 2 3 4 5"}
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_std_from_data_empty(self, client):
        """Test error handling for empty data"""
        response = client.post("/calculate-std-from-data", data={"data_points": ""})

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_std_from_data_invalid_format(self, client):
        """Test error handling for invalid data format"""
        response = client.post(
            "/calculate-std-from-data", data={"data_points": "a,b,c,d,e"}
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_std_from_range(self, client):
        """Test std calculation from range"""
        response = client.post(
            "/calculate-std-from-range",
            data={"min_val": "10", "max_val": "30", "estimation_method": "range_rule"},
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_std_from_range_invalid_range(self, client):
        """Test error handling for invalid range"""
        response = client.post(
            "/calculate-std-from-range",
            data={
                "min_val": "30",
                "max_val": "10",  # min > max
                "estimation_method": "range_rule",
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_std_from_percentiles(self, client):
        """Test std calculation from percentiles"""
        response = client.post(
            "/calculate-std-from-percentiles",
            data={"p25": "25", "p50": "50", "p75": "75"},
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_std_from_percentiles_invalid_order(self, client):
        """Test error handling for invalid percentile order"""
        response = client.post(
            "/calculate-std-from-percentiles",
            data={"p25": "75", "p50": "50", "p75": "25"},  # Invalid order
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()

    def test_conversion_rate_std_historical(self, client):
        """Test conversion rate std from historical data"""
        response = client.post(
            "/calculate-conversion-rate-std",
            data={
                "calc_type": "historical_data",
                "conversions": "50,45,55,48,52",
                "visitors": "1000,1000,1000,1000,1000",
            },
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_conversion_rate_std_theoretical(self, client):
        """Test conversion rate std theoretical calculation"""
        response = client.post(
            "/calculate-conversion-rate-std",
            data={
                "calc_type": "theoretical",
                "baseline_rate": "5",  # 5%
                "sample_size": "1000",
            },
        )

        assert response.status_code == 200
        assert b"Standard Deviation" in response.data

    def test_conversion_rate_std_mismatched_data(self, client):
        """Test error handling for mismatched conversion data"""
        response = client.post(
            "/calculate-conversion-rate-std",
            data={
                "calc_type": "historical_data",
                "conversions": "50,45,55",  # 3 values
                "visitors": "1000,1000",  # 2 values
            },
        )

        assert response.status_code == 200
        assert b"error" in response.data.lower()


class TestErrorHandling:
    """Test error handling across all routes"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-route")
        assert response.status_code == 404

    def test_invalid_method(self, client):
        """Test invalid HTTP method"""
        response = client.patch("/calculate-sample-size")
        assert response.status_code == 405

    def test_empty_post_data(self, client):
        """Test POST with empty data"""
        response = client.post("/calculate-sample-size", data={})
        assert response.status_code == 200
        assert b"error" in response.data.lower()


class TestResultsFormatting:
    """Test that results are properly formatted"""

    def test_sample_size_results_formatting(self, client):
        """Test that sample size results are properly formatted"""
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
        soup = BeautifulSoup(response.data, "html.parser")

        # Check that numeric values are properly formatted
        # This tests our template formatting fixes
        tables = soup.find_all("table")
        assert len(tables) > 0

        # Look for percentage formatting
        text_content = response.data.decode("utf-8")
        assert "80.0%" in text_content  # Power
        assert "5.0%" in text_content  # Alpha

    def test_msprt_results_formatting(self, client):
        """Test that mSPRT results are properly formatted"""
        response = client.post(
            "/calculate-msprt",
            data={
                "baseline_mean": "100",
                "baseline_std": "20",
                "std_known": "known",
                "improvement_type": "relative",
                "relative_improvement": "5",
                "alpha": "0.05",
                "beta": "0.2",
                "max_n": "1000",
                "min_n": "100",
            },
        )

        assert response.status_code == 200
        text_content = response.data.decode("utf-8")

        # Check for percentage formatting
        assert "5.0%" in text_content  # Alpha
        assert "20.0%" in text_content  # Beta
        assert "80.0%" in text_content  # Power

    def test_std_results_formatting(self, client):
        """Test that std results are properly formatted"""
        response = client.post(
            "/calculate-std-from-data", data={"data_points": "1,2,3,4,5,6,7,8,9,10"}
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        # Check that results table exists
        tables = soup.find_all("table")
        assert len(tables) > 0

        # Check for proper numeric formatting
        text_content = response.data.decode("utf-8")
        # Should contain decimal numbers
        import re

        assert re.search(r"\d+\.\d+", text_content)


class TestNavigationAndLinks:
    """Test navigation and internal links"""

    def test_navigation_links_work(self, client):
        """Test that navigation links work"""
        # Test from home page
        response = client.get("/")
        soup = BeautifulSoup(response.data, "html.parser")

        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href and href.startswith("/") and not href.startswith("//"):
                # Test internal links
                link_response = client.get(href)
                assert link_response.status_code == 200

    def test_back_links_in_results(self, client):
        """Test that back links work in results pages"""
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
        soup = BeautifulSoup(response.data, "html.parser")

        # Look for back links
        links = soup.find_all("a")
        back_links = [link for link in links if "back" in link.get_text().lower()]
        assert len(back_links) > 0
