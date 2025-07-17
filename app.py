"""
Team Tools Dashboard - Modular Flask Application
"""
import logging
import traceback

from flask import Flask, render_template, request

from calculations.fixed_horizon import calculate_sample_size
from calculations.msprt import calculate_msprt_plan
from calculations.std_calculator import (
    calculate_std_from_conversion_data,
    calculate_std_from_data,
    estimate_conversion_rate_std,
    estimate_std_from_percentiles,
    estimate_std_from_range,
    sample_size_for_std_estimation,
)

app = Flask(__name__)

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("team_tools_debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def log_error(error, context_info=None):
    """Enhanced error logging with context"""
    logger.error(f"Error occurred: {str(error)}")
    if context_info:
        logger.error(f"Context: {context_info}")
    logger.error(f"Traceback: {traceback.format_exc()}")


def validate_numeric_input(
    value, field_name, min_val=None, max_val=None, allow_none=False
):
    """Validate numeric input with detailed error messages"""
    if value is None or value == "":
        if allow_none:
            return None
        raise ValueError(f"{field_name} is required")

    try:
        num_value = float(value)
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{field_name} must be >= {min_val}")
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{field_name} must be <= {max_val}")
        return num_value
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"{field_name} must be a valid number")
        raise e


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/sample-size-calculator")
def sample_size_calculator():
    return render_template("fixed_horizon_form.html")


@app.route("/calculate-sample-size", methods=["POST"])
def calculate_sample_size_route():
    try:
        logger.info("Starting sample size calculation")
        logger.debug(f"Form data received: {dict(request.form)}")

        # Extract and validate form data
        baseline_mean = validate_numeric_input(
            request.form.get("baseline_mean"), "Baseline mean", min_val=0
        )

        baseline_std = validate_numeric_input(
            request.form.get("baseline_std"),
            "Baseline standard deviation",
            min_val=0,
            allow_none=True,
        )

        power = validate_numeric_input(
            request.form.get("power"), "Statistical power", min_val=0.01, max_val=0.99
        )

        alpha = validate_numeric_input(
            request.form.get("alpha"), "Significance level", min_val=0.001, max_val=0.5
        )

        test_type = request.form.get("test_type")
        if test_type not in ["two-sided", "one-sided"]:
            raise ValueError("Test type must be 'two-sided' or 'one-sided'")

        improvement_type = request.form.get("improvement_type")
        if improvement_type not in ["absolute", "relative"]:
            raise ValueError("Improvement type must be 'absolute' or 'relative'")

        # Get improvement value
        if improvement_type == "absolute":
            improvement_value = validate_numeric_input(
                request.form.get("absolute_improvement"), "Absolute improvement"
            )
        else:
            improvement_value = validate_numeric_input(
                request.form.get("relative_improvement"),
                "Relative improvement (%)",
                min_val=-100,
                max_val=1000,
            )

        logger.info(
            f"Validated inputs: baseline_mean={baseline_mean}, baseline_std={baseline_std}, power={power}, alpha={alpha}"
        )

        # Calculate results
        results = calculate_sample_size(
            baseline_mean,
            baseline_std,
            improvement_type,
            improvement_value,
            power,
            alpha,
            test_type,
        )

        logger.info("Sample size calculation completed successfully")
        return render_template("fixed_horizon_results.html", **results)

    except Exception as e:
        error_context = {
            "route": "/calculate-sample-size",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/sample-size-calculator"
        )


@app.route("/sequential-calculator")
def sequential_calculator():
    return render_template("msprt_form.html")


@app.route("/calculate-msprt", methods=["POST"])
def calculate_msprt_route():
    try:
        logger.info("Starting mSPRT calculation")
        logger.debug(f"Form data received: {dict(request.form)}")

        # Extract and validate form data
        baseline_mean = validate_numeric_input(
            request.form.get("baseline_mean"), "Baseline mean", min_val=0
        )

        alpha = validate_numeric_input(
            request.form.get("alpha"),
            "Type I error (alpha)",
            min_val=0.001,
            max_val=0.5,
        )

        beta = validate_numeric_input(
            request.form.get("beta"), "Type II error (beta)", min_val=0.001, max_val=0.5
        )

        weekly_visitors = validate_numeric_input(
            request.form.get("weekly_visitors"), "Weekly visitors per group", min_val=10
        )
        weekly_visitors = int(weekly_visitors)

        max_weeks = validate_numeric_input(
            request.form.get("max_weeks"), "Maximum test duration (weeks)", min_val=1, max_val=52
        )
        max_weeks = int(max_weeks)

        # Calculate sample size parameters from weekly visitors
        max_n = weekly_visitors * max_weeks
        min_n = weekly_visitors  # Start analyzing after first week

        std_known = request.form.get("std_known")
        if std_known not in ["known", "estimated", "unknown"]:
            raise ValueError(
                "Standard deviation knowledge must be 'known', 'estimated', or 'unknown'"
            )

        improvement_type = request.form.get("improvement_type")
        if improvement_type not in ["absolute", "relative"]:
            raise ValueError("Improvement type must be 'absolute' or 'relative'")

        # Get standard deviation if provided
        baseline_std = None
        if std_known == "known" or std_known == "estimated":
            baseline_std = validate_numeric_input(
                request.form.get("baseline_std"),
                "Baseline standard deviation",
                min_val=0,
                allow_none=True,
            )

        # Get improvement value
        if improvement_type == "absolute":
            improvement_value = validate_numeric_input(
                request.form.get("absolute_improvement"), "Absolute improvement"
            )
        else:
            improvement_value = validate_numeric_input(
                request.form.get("relative_improvement"),
                "Relative improvement (%)",
                min_val=-100,
                max_val=1000,
            )

        logger.info(
            f"Validated inputs: baseline_mean={baseline_mean}, weekly_visitors={weekly_visitors}, max_weeks={max_weeks}, alpha={alpha}, beta={beta}"
        )

        # Calculate mSPRT plan
        results = calculate_msprt_plan(
            baseline_mean,
            std_known,
            baseline_std,
            improvement_type,
            improvement_value,
            alpha,
            beta,
            max_n,
            min_n,
            weekly_visitors,
            max_weeks,
        )

        logger.info("mSPRT calculation completed successfully")
        return render_template("msprt_results.html", **results)

    except Exception as e:
        error_context = {
            "route": "/calculate-msprt",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/sequential-calculator"
        )


@app.route("/std-calculator")
def std_calculator():
    return render_template("std_calculator_form.html")


@app.route("/calculate-std-from-data", methods=["POST"])
def calculate_std_from_data_route():
    try:
        logger.info("Starting std calculation from data")
        logger.debug(f"Form data received: {dict(request.form)}")

        # Parse data points from textarea
        data_input = request.form.get("data_points", "").strip()
        if not data_input:
            raise ValueError("Data points are required")

        logger.debug(f"Raw data input: {data_input}")

        # Handle different input formats
        data_points = []
        try:
            if "," in data_input:
                data_points = [
                    float(x.strip()) for x in data_input.split(",") if x.strip()
                ]
            elif "\n" in data_input:
                data_points = [
                    float(x.strip()) for x in data_input.split("\n") if x.strip()
                ]
            else:
                data_points = [
                    float(x.strip()) for x in data_input.split() if x.strip()
                ]
        except ValueError as e:
            raise ValueError(
                f"Invalid data format. All values must be numbers. Error: {str(e)}"
            )

        if len(data_points) < 2:
            raise ValueError(
                "At least 2 data points are required for standard deviation calculation"
            )

        logger.info(f"Parsed {len(data_points)} data points")

        results = calculate_std_from_data(data_points)
        logger.info("Std calculation from data completed successfully")
        return render_template("std_calculator_results.html", method="data", **results)

    except Exception as e:
        error_context = {
            "route": "/calculate-std-from-data",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/std-calculator"
        )


@app.route("/calculate-std-from-range", methods=["POST"])
def calculate_std_from_range_route():
    try:
        logger.info("Starting std calculation from range")
        logger.debug(f"Form data received: {dict(request.form)}")

        min_val = validate_numeric_input(request.form.get("min_val"), "Minimum value")

        max_val = validate_numeric_input(request.form.get("max_val"), "Maximum value")

        if min_val >= max_val:
            raise ValueError("Minimum value must be less than maximum value")

        method = request.form.get("estimation_method")
        if method not in ["range_rule", "six_sigma"]:
            raise ValueError("Estimation method must be 'range_rule' or 'six_sigma'")

        logger.info(
            f"Validated inputs: min_val={min_val}, max_val={max_val}, method={method}"
        )

        results = estimate_std_from_range(min_val, max_val, method)
        logger.info("Std calculation from range completed successfully")
        return render_template("std_calculator_results.html", method="range", **results)

    except Exception as e:
        error_context = {
            "route": "/calculate-std-from-range",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/std-calculator"
        )


@app.route("/calculate-std-from-percentiles", methods=["POST"])
def calculate_std_from_percentiles_route():
    try:
        logger.info("Starting std calculation from percentiles")
        logger.debug(f"Form data received: {dict(request.form)}")

        p25 = validate_numeric_input(request.form.get("p25"), "25th percentile (Q1)")

        p50 = validate_numeric_input(
            request.form.get("p50"), "50th percentile (Median)"
        )

        p75 = validate_numeric_input(request.form.get("p75"), "75th percentile (Q3)")

        # Validate percentile order
        if not (p25 <= p50 <= p75):
            raise ValueError("Percentiles must be in ascending order: Q1 ≤ Median ≤ Q3")

        logger.info(f"Validated inputs: p25={p25}, p50={p50}, p75={p75}")

        results = estimate_std_from_percentiles(p25, p50, p75)
        logger.info("Std calculation from percentiles completed successfully")
        return render_template(
            "std_calculator_results.html", method="percentiles", **results
        )

    except Exception as e:
        error_context = {
            "route": "/calculate-std-from-percentiles",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/std-calculator"
        )


@app.route("/calculate-conversion-rate-std", methods=["POST"])
def calculate_conversion_rate_std_route():
    try:
        logger.info("Starting conversion rate std calculation")
        logger.debug(f"Form data received: {dict(request.form)}")

        calc_type = request.form.get("calc_type")
        if calc_type not in ["historical_data", "theoretical"]:
            raise ValueError(
                "Calculation type must be 'historical_data' or 'theoretical'"
            )

        if calc_type == "historical_data":
            # Parse historical conversion data
            conversions_input = request.form.get("conversions", "").strip()
            visitors_input = request.form.get("visitors", "").strip()

            if not conversions_input or not visitors_input:
                raise ValueError("Both conversions and visitors data are required")

            logger.debug(f"Conversions input: {conversions_input}")
            logger.debug(f"Visitors input: {visitors_input}")

            # Parse conversions
            try:
                if "," in conversions_input:
                    conversions = [
                        int(x.strip())
                        for x in conversions_input.split(",")
                        if x.strip()
                    ]
                else:
                    conversions = [
                        int(x.strip()) for x in conversions_input.split() if x.strip()
                    ]
            except ValueError as e:
                raise ValueError(
                    f"Invalid conversions format. All values must be integers. Error: {str(e)}"
                )

            # Parse visitors
            try:
                if "," in visitors_input:
                    visitors = [
                        int(x.strip()) for x in visitors_input.split(",") if x.strip()
                    ]
                else:
                    visitors = [
                        int(x.strip()) for x in visitors_input.split() if x.strip()
                    ]
            except ValueError as e:
                raise ValueError(
                    f"Invalid visitors format. All values must be integers. Error: {str(e)}"
                )

            if len(conversions) != len(visitors):
                raise ValueError(
                    "Number of conversion values must match number of visitor values"
                )

            if len(conversions) < 2:
                raise ValueError("At least 2 data points are required")

            # Validate that conversions <= visitors for each pair
            for i, (conv, vis) in enumerate(zip(conversions, visitors)):
                if conv > vis:
                    raise ValueError(
                        f"Conversions cannot exceed visitors in data point {i+1}"
                    )
                if vis <= 0:
                    raise ValueError(
                        f"Visitor count must be positive in data point {i+1}"
                    )

            logger.info(f"Parsed {len(conversions)} conversion/visitor pairs")

            results = calculate_std_from_conversion_data(conversions, visitors)
            logger.info(
                "Conversion rate std calculation from historical data completed successfully"
            )
            return render_template(
                "std_calculator_results.html", method="conversion_data", **results
            )

        elif calc_type == "theoretical":
            baseline_rate = validate_numeric_input(
                request.form.get("baseline_rate"),
                "Baseline conversion rate (%)",
                min_val=0.001,
                max_val=100,
            )
            baseline_rate = baseline_rate / 100  # Convert percentage to decimal

            sample_size = validate_numeric_input(
                request.form.get("sample_size"), "Sample size", min_val=1
            )
            sample_size = int(sample_size)

            logger.info(
                f"Validated inputs: baseline_rate={baseline_rate}, sample_size={sample_size}"
            )

            results = estimate_conversion_rate_std(baseline_rate, sample_size)
            logger.info(
                "Theoretical conversion rate std calculation completed successfully"
            )
            return render_template(
                "std_calculator_results.html",
                method="conversion_theoretical",
                **results,
            )

    except Exception as e:
        error_context = {
            "route": "/calculate-conversion-rate-std",
            "form_data": dict(request.form),
            "error_type": type(e).__name__,
        }
        log_error(e, error_context)
        return render_template(
            "error.html", error_message=str(e), back_url="/std-calculator"
        )


@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {request.url}")
    return (
        render_template("error.html", error_message="Page not found", back_url="/"),
        404,
    )


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return (
        render_template(
            "error.html", error_message="Internal server error occurred", back_url="/"
        ),
        500,
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") != "production"

    logger.info(f"Starting Flask app on port {port} with debug={debug_mode}")

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
