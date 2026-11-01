"""Tools the agent can call. Both use Open-Meteo, which needs no API key."""
import json
import urllib.parse
import urllib.request

TOOLS = [
    {"type": "function", "function": {
        "name": "geocode_city",
        "description": "Look up the latitude, longitude, country and timezone of a city.",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string", "description": "City name, e.g. 'Lisbon'"}},
                       "required": ["city"]},
    }},
    {"type": "function", "function": {
        "name": "get_forecast",
        "description": "Daily weather forecast starting today for given coordinates. "
                       "Returns date, min/max temperature in C and precipitation in mm.",
        "parameters": {"type": "object",
                       "properties": {"latitude": {"type": "number"},
                                      "longitude": {"type": "number"},
                                      "days": {"type": "integer", "minimum": 1, "maximum": 16}},
                       "required": ["latitude", "longitude", "days"]},
    }},
]


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode())


def parse_geocode(data: dict) -> dict:
    results = data.get("results")
    if not results:
        return {"error": "city not found"}
    top = results[0]
    return {k: top.get(k) for k in ("name", "country", "latitude", "longitude", "timezone")}


def parse_forecast(data: dict) -> list[dict]:
    daily = data["daily"]
    return [
        {"date": d, "temp_min_c": lo, "temp_max_c": hi, "precipitation_mm": rain}
        for d, lo, hi, rain in zip(daily["time"], daily["temperature_2m_min"],
                                   daily["temperature_2m_max"], daily["precipitation_sum"])
    ]


def geocode_city(city: str) -> str:
    query = urllib.parse.urlencode({"name": city, "count": 1})
    return json.dumps(parse_geocode(_get_json(f"https://geocoding-api.open-meteo.com/v1/search?{query}")))


def get_forecast(latitude: float, longitude: float, days: int) -> str:
    query = urllib.parse.urlencode({
        "latitude": latitude, "longitude": longitude, "timezone": "auto",
        "forecast_days": max(1, min(int(days), 16)),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    })
    return json.dumps(parse_forecast(_get_json(f"https://api.open-meteo.com/v1/forecast?{query}")))


def run_tool(name: str, args: dict) -> str:
    """Dispatch a tool call. Errors are returned as text so the model can recover."""
    try:
        if name == "geocode_city":
            return geocode_city(**args)
        if name == "get_forecast":
            return get_forecast(**args)
        return f"Error: unknown tool {name}"
    except Exception as exc:  # network, bad args, parse errors
        return f"Error: {exc}"
