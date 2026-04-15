# AgroChain Pulse

USSD-based agricultural credit scoring system with energy tokens for Uganda.

## Project Structure

```
AgroChain_Pulse/
├── python/          # USSD simulator, YPS model, data generation
│   ├── ussd_simulator.py
│   ├── data_generator.py
│   └── data/
├── go/              # Blockchain-lite (append-only log)
├── java/            # Spring Boot ECT ledger
└── frontend/        # HTML/TypeScript dashboard
```

## Day 1 Completed

- USSD Session Simulator (MTN/Airtel Uganda gateway simulation)
- Data generator for 50 farmer profiles + 180 days of sensor readings
- Generated synthetic soil moisture, temperature, rainfall data

## Running

```bash
cd python
python ussd_simulator.py
python data_generator.py
```