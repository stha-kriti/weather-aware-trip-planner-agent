import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from tools import parse_forecast, parse_geocode, run_tool


def test_parse_geocode_picks_first_result():
    data = {"results": [{"name": "Lisbon", "country": "Portugal", "latitude": 38.7,
                         "longitude": -9.1, "timezone": "Europe/Lisbon", "id": 1}]}
    assert parse_geocode(data) == {"name": "Lisbon", "country": "Portugal", "latitude": 38.7,
                                   "longitude": -9.1, "timezone": "Europe/Lisbon"}


def test_parse_geocode_unknown_city():
    assert parse_geocode({}) == {"error": "city not found"}


def test_parse_forecast_zips_daily_columns():
    data = {"daily": {"time": ["2026-05-01", "2026-05-02"], "temperature_2m_min": [10, 11],
                      "temperature_2m_max": [20, 21], "precipitation_sum": [0.0, 5.2]}}
    days = parse_forecast(data)
    assert days[1] == {"date": "2026-05-02", "temp_min_c": 11, "temp_max_c": 21, "precipitation_mm": 5.2}


def test_unknown_tool_returns_error_text():
    assert run_tool("nope", {}).startswith("Error")


def test_bad_arguments_return_error_text():
    assert run_tool("get_forecast", {"latitude": 1}).startswith("Error")
