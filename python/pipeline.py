"""
Integration: YPS Model + Blockchain-Lite
Complete pipeline from sensor data to tamper-proof YPS records
"""

import json
import time
import os
import sys

sys.path.append(os.path.dirname(__file__))

from yps_model import YPSModel
from blockchain_lite import BlockchainLite
from data_generator import generate_farmers, generate_sensor_readings


def run_pipeline():
    print("=" * 60)
    print("AGROCHAIN PULSE PIPELINE")
    print("Sensor Data -> YPS Score -> Blockchain Storage")
    print("=" * 60)

    print("\n[1/4] Generating farmer profiles and sensor data...")
    farmers = generate_farmers(10)
    readings = generate_sensor_readings(farmers, 10)

    print(f"[OK] {len(farmers)} farmers, {len(readings)} readings")

    print("\n[2/4] Loading YPS Model...")
    model = YPSModel()
    if os.path.exists("models/yps_model.pkl"):
        model.load_model("models/yps_model.pkl")
    else:
        model.train()
        model.save_model("models/yps_model.pkl")

    print("\n[3/4] Initializing Blockchain-Lite...")
    chain = BlockchainLite("data/chain.log")

    print("\n[4/4] Processing sensor readings -> YPS -> Chain...")

    processed_count = 0
    farmer_latest = {}

    for reading in readings:
        farmer_id = reading["farmer_id"]

        sensor_data = {
            "soil_moisture": reading["soil_moisture_percent"],
            "temperature": reading["temperature_celsius"],
            "rainfall_deviation": reading["rainfall_deviation_mm"],
            "farm_size": 2.0,
            "crop_type": reading["crop_type"],
        }

        yps_score = model.predict(sensor_data)

        record = chain.add_yps_record(farmer_id, sensor_data, yps_score)

        farmer_latest[farmer_id] = {"yps": yps_score, "timestamp": reading["timestamp"]}
        processed_count += 1

        if processed_count % 100 == 0:
            print(f"  Processed {processed_count} readings...")

    print(f"\n[OK] Processed {processed_count} sensor readings")

    stats = chain.get_stats()
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Total YPS Records: {stats['total_records']}")
    print(f"Unique Farmers: {stats['unique_farmers']}")
    print(f"Chain Verified: {stats['verified']}")
    print(f"Latest Hash: {stats['latest_hash']}")

    print("\n--- Sample Farmer YPS Scores ---")
    for i, (farmer_id, data) in enumerate(list(farmer_latest.items())[:10]):
        category = (
            "Excellent"
            if data["yps"] >= 800
            else "Good"
            if data["yps"] >= 600
            else "Fair"
            if data["yps"] >= 400
            else "Low"
        )
        print(f"  {farmer_id}: YPS={data['yps']} ({category})")

    return chain, model


if __name__ == "__main__":
    chain, model = run_pipeline()
