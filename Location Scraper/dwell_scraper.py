import requests
import time
from geopy.distance import geodesic
from datetime import datetime

# --- CONFIG ---
ROUTE = "404"
STOP_NAME = "Westside Shopping Centre"   # example
STOP_COORDS = (53.276148, -9.077608)     # lat, lon
STOP_RADIUS_METERS = 25
POLL_INTERVAL = 30  # seconds

inside_stop_zone = False
arrival_time = None

print("Tracking 404 bus... Press Ctrl+C to stop.")

while True:
    try:
        # Fetch real-time data
        data = requests.get("https://galway-bus.apis.ie/api/realtime/galway").json()

        # Filter for route 404 vehicles
        vehicles = [v for v in data if v.get("route_short_name") == ROUTE]

        if not vehicles:
            print("No 404 bus found at this moment.")
            time.sleep(POLL_INTERVAL)
            continue

        bus = vehicles[0]  # first bus found (expand if tracking multiple)
        bus_pos = (bus["vehicle_lat"], bus["vehicle_lon"])
        dist = geodesic(bus_pos, STOP_COORDS).meters

        now = datetime.now()

        # Check if bus enters stop zone
        if dist <= STOP_RADIUS_METERS and not inside_stop_zone:
            inside_stop_zone = True
            arrival_time = now
            print(f"Bus ARRIVED at stop at {arrival_time}")

        # Check if bus exits stop zone
        if dist > STOP_RADIUS_METERS and inside_stop_zone:
            inside_stop_zone = False
            departure_time = now

            dwell_seconds = (departure_time - arrival_time).total_seconds()
            print(f"Bus DEPARTED at {departure_time} — Dwell time = {dwell_seconds:.1f} sec")

        time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("Stopped tracking.")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(POLL_INTERVAL)
