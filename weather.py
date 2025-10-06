# weather_route.py
from flask import Blueprint, request, jsonify
import requests
from datetime import datetime, timezone

bp = Blueprint("weather", __name__)

WX_URL = "https://api.open-meteo.com/v1/forecast"

@bp.route("/weather", methods=["GET", "OPTIONS"])
def weather():
    # CORS (adjust in prod)
    cors = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    if request.method == "OPTIONS":
        return ("", 204, cors)

    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        if lat is None or lon is None:
            return (jsonify({"error": "lat and lon query params are required"}), 400, cors)

        vars = "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m,visibility,precipitation,cloud_cover"
        r = requests.get(WX_URL, params={
            "latitude": lat,
            "longitude": lon,
            "hourly": vars,
            "timezone": "UTC",
            "forecast_days": 1
        }, timeout=10)
        r.raise_for_status()
        j = r.json(); h = j["hourly"]; t = h["time"]

        # Pick current UTC hour
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat(timespec="minutes").replace("+00:00","")
        idx = t.index(now) if now in t else (len(t)-1)

        data = {
            "latitude": lat,
            "longitude": lon,
            "observed_hour_utc": t[idx],
            "wind_speed":        h["wind_speed_10m"][idx],
            "wind_gusts":        h["wind_gusts_10m"][idx],
            "wind_direction_deg":h["wind_direction_10m"][idx],
            "visibility":        h["visibility"][idx],
            "temperature":       h["temperature_2m"][idx],
            "humidity_pct":      h["relative_humidity_2m"][idx],
            "precipitation":     h["precipitation"][idx],
            "cloud_cover_pct":   h["cloud_cover"][idx],
            "units":             j.get("hourly_units", {}),
        }
        return (jsonify(data), 200, cors)
    except Exception as e:
        return (jsonify({"error": str(e)}), 500, cors)
