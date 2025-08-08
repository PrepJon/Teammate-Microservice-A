Request Format
    Transport: ZeroMQ REQ socket connects to microservice’s REP socket at tcp://<host>:5555
    Send JSON string with fields:
        city (string, required): city name to look up
        units (string, optional): "metric" or "imperial" (defaults to imperial)
Example Request JSON:

{ "city": "Detroit", "units": "metric" }

Response Format
    JSON string reply from microservice.
Success (status 200):

{
  "status": 200,
  "city": "Detroit",
  "temperature": 22.5,
  "wind_speed": 13.4,
  "summary": "Partly cloudy",
  "units": "metric"
}

Error (e.g., city not found):

{
  "status": 404,
  "error": "City 'Detroitt' not found. Please check spelling."
}

Usage Overview
    Connect ZeroMQ REQ socket to microservice REP socket.
    Send JSON request with city (unit's optional).
    Receive JSON response with weather data or error.
    Handle status field to detect success or failure.


