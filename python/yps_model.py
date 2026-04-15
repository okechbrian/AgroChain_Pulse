import json
import random
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os


class YPSModel:
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )
        self.crop_encoder = LabelEncoder()
        self.is_trained = False

    def _generate_training_data(self, num_samples=1000):
        crops = [
            "maize",
            "cassava",
            "beans",
            "coffee",
            "banana",
            "groundnuts",
            "sorghum",
        ]
        self.crop_encoder.fit(crops)

        X = []
        y = []

        for _ in range(num_samples):
            moisture = random.uniform(10, 100)
            temp = random.uniform(15, 35)
            rainfall_dev = random.uniform(-10, 10)
            farm_size = random.uniform(0.5, 10.0)
            crop_idx = random.randint(0, len(crops) - 1)

            optimal_moisture = 40 + random.uniform(-10, 10)
            moisture_score = 100 - abs(moisture - optimal_moisture)

            optimal_temp = 25 + random.uniform(-3, 3)
            temp_score = 100 - abs(temp - optimal_temp) * 3

            rain_score = 100 - abs(rainfall_dev) * 2 if rainfall_dev < 0 else 100

            base_yps = (
                moisture_score * 0.4
                + temp_score * 0.3
                + rain_score * 0.2
                + (farm_size / 10) * 0.1 * 100
            )

            base_yps = max(200, min(950, base_yps))

            if crop_idx == 0:  # maize
                base_yps *= 1.05
            elif crop_idx == 3:  # coffee
                base_yps *= 0.9

            base_yps = max(200, min(950, base_yps))

            X.append([moisture, temp, rainfall_dev, farm_size, crop_idx])
            y.append(int(base_yps))

        return np.array(X), np.array(y)

    def train(self):
        print("Generating training data...")
        X, y = self._generate_training_data(1000)

        print("Training Gradient Boosting model...")
        self.model.fit(X, y)

        self.is_trained = True
        print("Model trained successfully!")

        train_score = self.model.score(X, y)
        print(f"Training R2 Score: {train_score:.4f}")

    def predict(self, sensor_data: dict) -> int:
        if not self.is_trained:
            raise ValueError("Model not trained yet!")

        crop_type = sensor_data.get("crop_type", "maize")
        if crop_type not in self.crop_encoder.classes_:
            crop_type = "maize"

        crop_idx = self.crop_encoder.transform([crop_type])[0]

        features = np.array(
            [
                [
                    sensor_data.get("soil_moisture", 50),
                    sensor_data.get("temperature", 25),
                    sensor_data.get("rainfall_deviation", 0),
                    sensor_data.get("farm_size", 1.0),
                    crop_idx,
                ]
            ]
        )

        yps = self.model.predict(features)[0]
        yps = max(0, min(1000, int(yps)))

        return yps

    def predict_batch(self, sensor_readings: list) -> list:
        results = []

        for reading in sensor_readings:
            try:
                yps = self.predict(reading)
            except:
                yps = 500

            results.append(
                {
                    "farmer_id": reading.get("farmer_id"),
                    "timestamp": reading.get("timestamp"),
                    "yps_score": yps,
                }
            )

        return results

    def save_model(self, path: str = "models/yps_model.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "crop_encoder": self.crop_encoder,
                    "is_trained": self.is_trained,
                },
                f,
            )
        print(f"Model saved to {path}")

    def load_model(self, path: str = "models/yps_model.pkl"):
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.crop_encoder = data["crop_encoder"]
            self.is_trained = data["is_trained"]
        print(f"Model loaded from {path}")


def demo():
    print("=" * 60)
    print("YPS MODEL DEMO - Gradient Boosting Yield Score")
    print("=" * 60)

    model = YPSModel()
    model.train()

    model.save_model("models/yps_model.pkl")

    print("\n--- Testing Predictions ---")
    test_cases = [
        {
            "farmer_id": "FAR001",
            "soil_moisture": 45.2,
            "temperature": 24.5,
            "rainfall_deviation": 2.1,
            "farm_size": 2.5,
            "crop_type": "maize",
        },
        {
            "farmer_id": "FAR002",
            "soil_moisture": 20.5,
            "temperature": 32.0,
            "rainfall_deviation": -8.0,
            "farm_size": 1.0,
            "crop_type": "beans",
        },
        {
            "farmer_id": "FAR003",
            "soil_moisture": 65.0,
            "temperature": 22.0,
            "rainfall_deviation": 5.0,
            "farm_size": 4.0,
            "crop_type": "rice",
        },
    ]

    for test in test_cases:
        yps = model.predict(test)
        category = (
            "Excellent"
            if yps >= 800
            else "Good"
            if yps >= 600
            else "Fair"
            if yps >= 400
            else "Low"
        )
        print(f"{test['farmer_id']}: YPS = {yps} ({category})")

    print("\n--- Testing Inference Speed ---")
    import time

    test_data = {
        "soil_moisture": 45.0,
        "temperature": 25.0,
        "rainfall_deviation": 0.0,
        "farm_size": 2.0,
        "crop_type": "maize",
    }

    start = time.time()
    for _ in range(100):
        model.predict(test_data)
    elapsed = time.time() - start

    avg_time_ms = (elapsed / 100) * 1000
    print(f"Average inference time: {avg_time_ms:.2f}ms")
    print(
        f"Target: <400ms on Raspberry Pi 4 - {'PASS' if avg_time_ms < 10 else 'CHECK'}"
    )

    print("\n" + "=" * 60)
    print("YPS Model Ready!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
