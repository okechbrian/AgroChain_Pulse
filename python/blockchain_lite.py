import json
import time
import hashlib
import os
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
import struct


@dataclass
class YPSRecord:
    farmer_id: str
    yps_score: int
    timestamp: str
    data_hash: str
    record_hash: str


class BlockchainLite:
    def __init__(self, storage_path: str = "data/chain.log"):
        self.storage_path = storage_path
        self.chain: List[YPSRecord] = []
        self._load_chain()

    def _load_chain(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.chain = [YPSRecord(**r) for r in data]
            except:
                self.chain = []

    def _save_chain(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump([asdict(r) for r in self.chain], f, indent=2)

    def _hash_data(self, data: dict) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _calculate_record_hash(
        self, farmer_id: str, yps: int, timestamp: str, data_hash: str, prev_hash: str
    ) -> str:
        raw = f"{farmer_id}{yps}{timestamp}{data_hash}{prev_hash}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def add_yps_record(
        self, farmer_id: str, sensor_data: dict, yps_score: int
    ) -> YPSRecord:
        timestamp = datetime.now().isoformat()
        data_hash = self._hash_data(sensor_data)

        prev_hash = self.chain[-1].record_hash if self.chain else "0000"

        record_hash = self._calculate_record_hash(
            farmer_id, yps_score, timestamp, data_hash, prev_hash
        )

        record = YPSRecord(
            farmer_id=farmer_id,
            yps_score=yps_score,
            timestamp=timestamp,
            data_hash=data_hash,
            record_hash=record_hash,
        )

        self.chain.append(record)
        self._save_chain()

        return record

    def get_yps(self, farmer_id: str) -> Optional[YPSRecord]:
        for record in reversed(self.chain):
            if record.farmer_id == farmer_id:
                return record
        return None

    def get_all_yps(self) -> List[YPSRecord]:
        return self.chain

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            prev_record = self.chain[i - 1]
            curr_record = self.chain[i]

            expected_hash = self._calculate_record_hash(
                curr_record.farmer_id,
                curr_record.yps_score,
                curr_record.timestamp,
                curr_record.data_hash,
                prev_record.record_hash,
            )

            if curr_record.record_hash != expected_hash:
                return False
        return True

    def get_stats(self) -> dict:
        return {
            "total_records": len(self.chain),
            "unique_farmers": len(set(r.farmer_id for r in self.chain)),
            "verified": self.verify_chain(),
            "latest_hash": self.chain[-1].record_hash if self.chain else "0000",
        }


def demo():
    print("=" * 60)
    print("BLOCKCHAIN-LITE DEMO - Go-ready Append-Only Log")
    print("=" * 60)

    chain = BlockchainLite("data/chain.log")

    sample_data = [
        {
            "farmer_id": "FAR001",
            "soil_moisture": 45.2,
            "temperature": 24.5,
            "rainfall_deviation": 2.1,
        },
        {
            "farmer_id": "FAR002",
            "soil_moisture": 38.7,
            "temperature": 26.1,
            "rainfall_deviation": -1.3,
        },
        {
            "farmer_id": "FAR001",
            "soil_moisture": 52.3,
            "temperature": 23.8,
            "rainfall_deviation": 5.2,
        },
    ]

    print("\n--- Adding YPS Records ---")
    for data in sample_data:
        yps = hash(data["farmer_id"]) % 1000
        record = chain.add_yps_record(data["farmer_id"], data, yps)
        print(
            f"[ADD] {record.farmer_id} -> YPS: {record.yps_score} | Hash: {record.record_hash}"
        )

    print("\n--- Chain Stats ---")
    stats = chain.get_stats()
    print(f"Total Records: {stats['total_records']}")
    print(f"Unique Farmers: {stats['unique_farmers']}")
    print(f"Chain Verified: {stats['verified']}")
    print(f"Latest Hash: {stats['latest_hash']}")

    print("\n--- Query FAR001 YPS ---")
    record = chain.get_yps("FAR001")
    if record:
        print(f"Farmer: {record.farmer_id}")
        print(f"YPS Score: {record.yps_score}")
        print(f"Timestamp: {record.timestamp}")
        print(f"Data Hash: {record.data_hash}")
        print(f"Record Hash: {record.record_hash}")

    print("\n--- Full Chain ---")
    for r in chain.get_all_yps():
        print(f"  {r.farmer_id}: YPS={r.yps_score} @ {r.timestamp[:19]}")

    print("\n" + "=" * 60)
    print("Blockchain-Lite Ready for Go Integration!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
