import zmq
import requests
import json
import time

# ZeroMQ setup
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")  # listen on port 5555

# Helper: Map Meteo weather codes to text summary (partial example)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    # Add more codes as needed...
}

# Helper: Convert metric to imperial
def celsius_to_fahrenheit(c):
    return c * 9/5 + 32

def kph_to_mph(kph):
    return kph * 0.621371

# Get lat/lon from city name
def get_lat_lon(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    resp = requests.get(geo_url)
    data = resp.json()
    if "results" not in data or len(data["results"]) == 0:
        return None, None
    loc = data["results"][0]
    return loc["latitude"], loc["longitude"]

# Get current weather info from lat/lon
def get_weather(lat, lon):
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true"
    )
    resp = requests.get(weather_url)
    data = resp.json()
    if "current_weather" not in data:
        return None
    return data["current_weather"]

print("Weather microservice running...")

while True:
    try:
        # Wait for next request
        message = socket.recv_string()
        start_time = time.time()

        # Parse request JSON
        request = json.loads(message)
        city = request.get("city")
        units = request.get("units", "imperial")  # default imperial

        if not city:
            response = {"status": 400, "error": "Missing 'city' in request."}
            socket.send_json(response)
            continue

        lat, lon = get_lat_lon(city)
        if lat is None:
            # City not found, send ZeroMQ 404 error message
            response = {"status": 404, "error": f"City '{city}' not found. Please check spelling."}
            socket.send_json(response)
            continue

        weather = get_weather(lat, lon)
        if weather is None:
            response = {"status": 500, "error": "Weather data unavailable."}
            socket.send_json(response)
            continue

        temp_c = weather["temperature"]
        wind_kph = weather["windspeed"]
        code = weather["weathercode"]

        # Convert units if imperial requested
        if units == "imperial":
            temperature = round(celsius_to_fahrenheit(temp_c), 1)
            wind_speed = round(kph_to_mph(wind_kph), 1)
        else:  # metric
            temperature = round(temp_c, 1)
            wind_speed = round(wind_kph, 1)

        summary = WEATHER_CODES.get(code, "Unknown")

        response = {
            "status": 200,
            "city": city,
            "temperature": temperature,
            "wind_speed": wind_speed,
            "summary": summary,
            "units": units,
        }

        socket.send_json(response)

        # Enforce your 1-second response time target if needed here (optional)
        elapsed = time.time() - start_time
        print(f"Processed request for '{city}' in {elapsed:.2f} seconds.")

    except Exception as e:
        # Catch all to prevent crashes, return error message
        error_response = {"status": 500, "error": str(e)}
        socket.send_json(error_response)