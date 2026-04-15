import random
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List
import os


@dataclass
class FarmerProfile:
    farmer_id: str
    name: str
    region: str
    gps_lat: float
    gps_lon: float
    crop_type: str
    farm_size_hectares: float


REGIONS = ["Kampala", "Mbarara", "Gulu", "Jinja", "Soroti", "Masaka", "Lira", "Kabale"]
CROP_TYPES = ["maize", "cassava", "beans", "coffee", "banana", "groundnuts", "sorghum"]

FARMER_NAMES = [
    "John",
    "Mary",
    "Peter",
    "Sarah",
    "James",
    "Grace",
    "David",
    "Agnes",
    "Michael",
    "Florence",
    "Robert",
    "Janet",
    "William",
    "Margaret",
    "George",
    "Florence",
    "Charles",
    "Catherine",
    "Daniel",
    "Ruth",
    "Joseph",
    "Beacon",
    "Thomas",
    "Esther",
    "Andrew",
    "Judith",
    "Paul",
    "Lucy",
    "Stephen",
    "Mercy",
    "Francis",
    "Dorothy",
    "Patrick",
    "Rose",
    "Martin",
    "Florence",
    "Simon",
    "Alice",
    "Emmanuel",
    "Christine",
    "Samuel",
    "Joan",
    "Richard",
    "Elizabeth",
    "Edward",
    "Innocent",
    "Timothy",
    "Peace",
    "Nicholas",
    "Diana",
]


def generate_farmers(count: int = 50) -> List[FarmerProfile]:
    farmers = []
    uganda_bounds = {"lat_min": -1.5, "lat_max": 4.2, "lon_min": 29.5, "lon_max": 35.0}

    for i in range(count):
        farmer = FarmerProfile(
            farmer_id=f"FAR{i + 1:03d}",
            name=FARMER_NAMES[i],
            region=random.choice(REGIONS),
            gps_lat=round(
                random.uniform(uganda_bounds["lat_min"], uganda_bounds["lat_max"]), 6
            ),
            gps_lon=round(
                random.uniform(uganda_bounds["lon_min"], uganda_bounds["lon_max"]), 6
            ),
            crop_type=random.choice(CROP_TYPES),
            farm_size_hectares=round(random.uniform(0.5, 5.0), 2),
        )
        farmers.append(farmer)
    return farmers


def generate_sensor_readings(
    farmers: List[FarmerProfile], days: int = 180
) -> List[dict]:
    readings = []
    start_date = datetime(2025, 10, 1)

    for farmer in farmers:
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)

            base_moisture = random.uniform(20, 60)
            rainfall_factor = random.uniform(0, 30) if random.random() > 0.7 else 0
            moisture = min(100, base_moisture + rainfall_factor)

            temperature = random.uniform(18, 32)

            if day_offset > 0 and random.random() < 0.1:
                deviation = random.uniform(-5, 5)
            else:
                deviation = 0

            reading = {
                "farmer_id": farmer.farmer_id,
                "timestamp": date.isoformat(),
                "soil_moisture_percent": round(moisture, 2),
                "temperature_celsius": round(temperature, 1),
                "rainfall_deviation_mm": round(deviation, 2),
                "gps_lat": farmer.gps_lat,
                "gps_lon": farmer.gps_lon,
                "crop_type": farmer.crop_type,
            }
            readings.append(reading)

    return readings


def main():
    print("Generating 50 farmer profiles...")
    farmers = generate_farmers(50)

    print("Generating 6 months of sensor readings...")
    readings = generate_sensor_readings(farmers, 180)

    os.makedirs("data", exist_ok=True)

    with open("data/farmers.json", "w") as f:
        json.dump([asdict(f) for f in farmers], f, indent=2)

    with open("data/sensor_readings.json", "w") as f:
        json.dump(readings, f, indent=2)

    print(f"[OK] Generated {len(farmers)} farmer profiles")
    print(f"[OK] Generated {len(readings)} sensor readings")
    print(f"[OK] Data saved to data/")


if __name__ == "__main__":
    main()
