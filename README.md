# 🚚 FastBox Delivery System Simulator

> **Assignment:** Mystery Delivery System — Python Logistics Simulator
> **Company:** FastBox (Fictional)

---

## 📌 Overview

FastBox Delivery Simulator models one day of package delivery operations.
It reads a JSON input describing warehouses, delivery agents, and packages,
assigns packages to the nearest available agent, simulates each delivery
trip, and produces a structured JSON report.

---

## 🛠️ Technology Stack

| Layer         | Technology          | Purpose                              |
|---------------|---------------------|--------------------------------------|
| Language      | Python 3.8+         | Core programming language            |
| `json`        | Built-in module     | Parse input / save report            |
| `math`        | Built-in module     | Euclidean distance calculation       |
| `csv`         | Built-in module     | Export top performer (Bonus)         |
| `random`      | Built-in module     | Simulated delivery delays (Bonus)    |
| `os`          | Built-in module     | File path validation                 |
| `sys`         | Built-in module     | Command-line argument support        |

> ✅ **Zero external dependencies** — runs with standard Python only.

---

## 📁 Project Structure

```
fastbox/
├── main.py              ← Complete simulator (single-file solution)
├── data.json            ← Default input (from assignment)
├── report.json          ← Auto-generated delivery report (output)
├── top_performer.csv    ← Bonus: CSV export of best agent (output)
└── README.md            ← This file
```

---

## 🚀 How to Run

### Basic run (uses `data.json`)
```bash
python main.py
```

### Run with a specific input file
```bash
python main.py data.json
python main.py test_case_1.json
python main.py test_case_5.json
```

### Requirements
- Python 3.8 or higher
- No pip installs needed

---

## 📥 Input Format

The simulator supports **two JSON formats**:

### Format A — Dict-based (recommended)
```json
{
  "warehouses": {
    "W1": [0, 0],
    "W2": [50, 75]
  },
  "agents": {
    "A1": [5, 5],
    "A2": [60, 60]
  },
  "packages": [
    {"id": "P1", "warehouse": "W1", "destination": [30, 40]}
  ]
}
```

### Format B — List-based (also supported)
```json
{
  "warehouses": [
    {"id": "W1", "location": [0, 0]}
  ],
  "agents": [
    {"id": "A1", "location": [5, 5]}
  ],
  "packages": [
    {"id": "P1", "warehouse_id": "W1", "destination": [30, 40]}
  ]
}
```

---

## 📤 Output: `report.json`

```json
{
  "A1": {
    "packages_delivered": 2,
    "total_distance": 121.21,
    "efficiency": 60.61
  },
  "A2": {
    "packages_delivered": 2,
    "total_distance": 79.21,
    "efficiency": 39.60
  },
  "A3": {
    "packages_delivered": 1,
    "total_distance": 14.14,
    "efficiency": 14.14
  },
  "best_agent": "A3"
}
```

| Field                | Description                                          |
|----------------------|------------------------------------------------------|
| `packages_delivered` | Total packages this agent successfully delivered     |
| `total_distance`     | Sum of all travel distances (Euclidean, 2 decimal)   |
| `efficiency`         | `total_distance ÷ packages_delivered` (lower = better) |
| `best_agent`         | Agent with the lowest efficiency score               |

---

## ⚙️ How It Works

### Step 1 — JSON Parsing
Loads `data.json` and normalizes both supported input formats into
a consistent internal representation.

### Step 2 — Package Assignment
For each package, calculates the **Euclidean distance** from every agent's
**initial position** to the package's **warehouse**:

```
distance = √((x₂ - x₁)² + (y₂ - y₁)²)
```

The nearest agent gets the package assigned to them.

### Step 3 — Delivery Simulation
Each agent delivers their packages **sequentially**:

```
Trip = (current_position → warehouse) + (warehouse → destination)
```

The agent's position updates to the delivery `destination` after each trip.
Total distance accumulates across all trips.

### Step 4 — Report Generation
Computes `packages_delivered`, `total_distance`, and `efficiency` per agent.
Selects `best_agent` as the one with the **lowest efficiency score**
(= minimum average distance per package).

### Step 5 — Save to File
Writes the final report to `report.json`.

---

## 🎁 Bonus Features

All bonus features are enabled by default and toggleable in `main.py`:

| Bonus Feature              | Flag in `run()`       | Output                         |
|----------------------------|-----------------------|--------------------------------|
| Random delivery delays     | `enable_delays=True`  | Delays in report.json          |
| ASCII route visualization  | `enable_ascii=True`   | Printed to console             |
| New agent joining mid-day  | `midday_agent={...}`  | Printed to console             |
| Export top performer CSV   | `enable_csv=True`     | `top_performer.csv`            |

### Enabling Mid-Day Agent (in `main.py`)
```python
run(
    input_file   = 'data.json',
    midday_agent = {"id": "A_NEW", "location": [50, 50]},
)
```

---

## 🧪 Test Cases

| File              | Warehouses | Agents | Packages | Status  |
|-------------------|-----------|--------|----------|---------|
| `data.json`       | 3         | 3      | 5        | ✅ Pass |
| `base_case.json`  | 3         | 3      | 5        | ✅ Pass |
| `test_case_1.json`| 5         | 4      | 12       | ✅ Pass |
| `test_case_2.json`| 3         | 3      | 10       | ✅ Pass |
| `test_case_3.json`| 4         | 4      | 6        | ✅ Pass |
| `test_case_4.json`| 5         | 5      | 12       | ✅ Pass |
| `test_case_5.json`| 5         | 5      | 10       | ✅ Pass |
| `test_case_6.json`| 4         | 4      | 9        | ✅ Pass |
| `test_case_7.json`| 4         | 4      | 10       | ✅ Pass |
| `test_case_8.json`| 5         | 4      | 11       | ✅ Pass |
| `test_case_9.json`| 3         | 4      | 8        | ✅ Pass |
| `test_case_10.json`| 5        | 4      | 11       | ✅ Pass |

---

## 📊 Evaluation Criteria Coverage

| Criteria                    | Weight | Implementation                        |
|-----------------------------|--------|---------------------------------------|
| JSON parsing                | 10%    | `load_data()` + `parse_input()`       |
| Distance calculation        | 20%    | `euclidean_distance()` — correct math |
| Agent-package assignment    | 25%    | `assign_packages()` — nearest agent   |
| Simulation & report         | 25%    | `simulate_deliveries()` + `build_report()` |
| Code clarity & comments     | 10%    | Fully commented with docstrings       |
| Bonus creativity            | 10%    | 4 bonus features implemented          |

---

## 👨‍💻 Author Notes

- All packages are guaranteed to be delivered (verified by the summary check)
- Agents with 0 packages are excluded from `best_agent` calculation
- The simulator handles edge cases: unknown warehouses, malformed entries, empty datasets
