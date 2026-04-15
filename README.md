# AgroChain Pulse

USSD-based agricultural credit scoring system with energy tokens for Uganda.

## Quick Start

Open `frontend/index.html` in a browser to see the live dashboard with 3 demo farmer nodes.

---

## 📂 Project Structure

```
AgroChain_Pulse/
├── python/          # USSD simulator, ML model, data generation
│   ├── ussd_simulator.py    # MTN/Airtel USSD gateway simulation
│   ├── yps_model.py         # Gradient Boosting YPS model
│   ├── blockchain_lite.py   # Python blockchain-lite (SHA-256)
│   ├── pipeline.py          # End-to-end pipeline
│   ├── data_generator.py    # Synthetic sensor data generator
│   ├── data/                # Generated farmer & sensor data
│   └── models/              # Trained ML model
├── go/              # Go blockchain-lite
│   └── main.go              # Append-only log with SHA-256
├── java/            # Spring Boot ECT Ledger
│   ├── pom.xml
│   └── src/main/java/com/agrochain/pulse/
│       └── PulseApplication.java    # ECT token system
└── frontend/        # Dashboard
    └── index.html   # Uganda map with farmer nodes
```

---

## 🚀 Running Each Component

### Day 1: USSD Simulator + Data Generator

```bash
cd python
python ussd_simulator.py
```

**What it does:** Simulates USSD menu flow (dial *201# → Register → Check YPS → Redeem Energy)

---

### Day 2: YPS Model + Blockchain

**Python (ML + Chain):**
```bash
cd python
python yps_model.py          # Train & test YPS model
python blockchain_lite.py     # Test append-only log
python pipeline.py           # Full pipeline demo
```

**Go (Blockchain-lite):**
```bash
cd go
go run main.go
```

**Performance:** YPS inference: ~1.5ms (target: <400ms on Pi4) ✅

---

### Day 3: ECT Ledger (Java)

```bash
cd java
javac ECTDemo.java
java ECTDemo
```

**Features:**
- Token issuance based on YPS score
- 72-hour expiry
- GPS-locked redemption (5km radius)
- Token JSON structure:
```json
{
  "token_id": "ECT1234567890",
  "farmer_id": "FAR001",
  "yps_score": 850,
  "kwh_allocated": 50.0,
  "issued_at": 1713187200,
  "expires_at": 1713273600,
  "gps_lock": "0.347600,32.582500",
  "issuer_sig": "a1b2c3d4",
  "redeemed": false
}
```

---

### Day 4: Dashboard (HTML/JS)

**Simply open in browser:**
```bash
# Windows
start frontend/index.html
# Or drag the file into Chrome/Firefox
```

**Features:**
- Interactive map of Uganda with 3 farmer nodes
- Real-time YPS scores with color coding
- ECT balance display
- Demo buttons: Simulate Sensor → Issue Token → Redeem
- Activity log

---

## 🔄 End-to-End Flow

```
[Sensor Data] → [YPS Model] → [Blockchain-Lite] → [ECT Ledger] → [Dashboard]
     ↓              ↓               ↓                  ↓              ↓
  50 farmers   0-1000 score   SHA-256 hash     72h expiry +    Uganda map
  180 days     Gradient       tamper-proof    GPS lock        live demo
               Boosting
```

---

## 📊 Key Features Implemented

| Feature | File | Status |
|---------|------|--------|
| USSD Simulator | `python/ussd_simulator.py` | ✅ |
| Data Generator | `python/data_generator.py` | ✅ |
| YPS ML Model | `python/yps_model.py` | ✅ |
| Blockchain-lite (Python) | `python/blockchain_lite.py` | ✅ |
| Blockchain-lite (Go) | `go/main.go` | ✅ |
| ECT Ledger (Java) | `java/ECTDemo.java` | ✅ |
| Dashboard | `frontend/index.html` | ✅ |

---

## 🌐 Demo Day Flow

1. **Open `frontend/index.html`** → Shows Uganda map with 3 nodes
2. **Click "Simulate Sensor"** → YPS updates for random farmer
3. **Click "Issue Token"** → Token issued based on YPS (50/30/15/5 kWh)
4. **Click "Redeem Energy"** → Token redeemed at pump node

This runs entirely on a laptop with no internet required.

---

## 📝 GitHub

**Repository:** https://github.com/okechbrian/AgroChain_Pulse

**Commits:**
- Day 1: USSD simulator + data generator
- Day 2: YPS model + blockchain-lite (Python + Go)
- Days 3-4: ECT Ledger + Dashboard