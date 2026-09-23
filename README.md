# FastBox Mystery Delivery System

Python Developer Assignment — Nexgensis Technologies Pvt. Ltd.

## 1. Overview

This project simulates one day of operations for a fictional logistics company, FastBox.

The program:

1. Reads delivery data from JSON.
2. Assigns each package to the nearest delivery agent.
3. Simulates each assigned delivery.
4. Calculates total distance travelled by every agent.
5. Calculates average distance per delivered package (`efficiency`).
6. Identifies the most efficient agent.
7. Saves the required result to `report.json`.

The repository also includes the 10 supplied test cases.

## 2. Project Structure

```text
nexgensis-python-delivery-assignment/
│
├── main.py
├── base_case.json
├── test_cases/
│   ├── test_case_1.json
│   ├── ...
│   └── test_case_10.json
├── README.md
├── requirements.txt
├── .gitignore
└── assignment_source.zip
```

## 3. Requirements

- Python 3.9+
- No external Python packages are required.

`requirements.txt` is intentionally empty because the implementation uses only the Python standard library.

## 4. Run the Assignment

Open a terminal in the project folder.

### Base case

```bash
python main.py
```

This creates:

```text
report.json
```

### Run a supplied test case

```bash
python main.py --input test_cases/test_case_1.json --output report.json
```

You can repeat this for test cases 1–10.

### Detailed route output

```bash
python main.py --input base_case.json --detailed
```

This creates:

- `report.json`
- `route_report.json`

### Bonus: random delivery delays

```bash
python main.py --input base_case.json --detailed --delays
```

The random delay is recorded in `route_report.json`.

### Bonus: CSV export

```bash
python main.py --input base_case.json --csv
```

This creates:

```text
agent_report.csv
```

## 5. Algorithm

### Step 1 — Read JSON

The program uses Python's built-in `json` module.

### Step 2 — Find the nearest agent

For every package, the program looks at its warehouse and calculates the Euclidean distance from every agent's initial location to that warehouse.

Formula:

```text
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

The agent with the smallest distance receives the package.

### Step 3 — Simulate the route

For each agent, assigned packages are processed in the original package order.

The route for a package is:

```text
current agent position
        ↓
warehouse
        ↓
destination
```

After delivery, the agent's current position becomes that package's destination.

### Step 4 — Calculate efficiency

```text
efficiency = total_distance / packages_delivered
```

Lower average distance per package means greater route efficiency.

### Step 5 — Find best agent

The most efficient agent is the agent with the lowest average distance per delivered package.

## 6. Engineering Assumptions

The assignment intentionally leaves some routing details open. The following assumptions are documented explicitly:

1. **Two input formats are supported.**
   - The provided `base_case.json` uses lists of objects.
   - Several supplied test cases use dictionaries such as `"W1": [x, y]`.
   The program normalizes both formats.

2. **Assignment uses initial agent location.**
   Package assignment is based on the distance from the agent's starting location to the package's warehouse, matching the task wording.

3. **Package order.**
   After assignment, an agent processes its packages in their original JSON order. This is deterministic and avoids inventing a scheduling rule that was not specified.

4. **Agent movement.**
   After delivering a package, the agent remains at that package's destination. The next package therefore starts from the previous destination.

5. **Tie-breaking.**
   If two agents have exactly equal distance to a warehouse, the lexicographically smaller agent ID is selected. This makes results deterministic.

6. **Efficiency definition.**
   Efficiency is interpreted as average distance per delivered package:
   `total_distance / packages_delivered`.

7. **Distance units.**
   Coordinates are treated as abstract 2-D units. No conversion to kilometres or miles is made.

8. **Rounding.**
   Calculations use full floating-point precision internally. Values are rounded to two decimal places only when written to the report.

9. **Invalid references.**
   A package referring to an unknown warehouse causes a clear validation error rather than silently producing an incorrect report.

10. **All packages must be delivered.**
    The program checks that the number of delivered packages equals the number of input packages.

## 7. Required Output

The required `report.json` has this structure:

```json
{
    "A1": {
        "packages_delivered": 2,
        "total_distance": 78.28,
        "efficiency": 39.14
    },
    "A2": {
        "packages_delivered": 2,
        "total_distance": 72.24,
        "efficiency": 36.12
    },
    "A3": {
        "packages_delivered": 1,
        "total_distance": 14.14,
        "efficiency": 14.14
    },
    "best_agent": "A3"
}
```

The exact numbers depend on the input and the routing assumptions documented above.

## 8. Why the Implementation Is Structured This Way

The solution separates responsibilities into small functions:

- `load_json()` — file input
- `normalize_locations()` — handles both supplied schemas
- `normalize_packages()` — validates packages
- `euclidean_distance()` — mathematical calculation
- `nearest_agent()` — assignment logic
- `assign_packages()` — package grouping
- `simulate()` — delivery simulation
- `save_json()` — output
- `save_csv()` — bonus export
- `print_ascii_routes()` — bonus visualization

This makes the code easier to test, maintain, and extend.

## 9. Testing

The repository contains all 10 JSON test cases supplied with the assignment.

Example:

```bash
python main.py --input test_cases/test_case_1.json --output report.json
python main.py --input test_cases/test_case_2.json --output report.json
python main.py --input test_cases/test_case_3.json --output report.json
```

Continue through `test_case_10.json`.

For each test, verify:

- the program exits without an exception,
- `report.json` is valid JSON,
- every input package is delivered exactly once,
- every agent has a report entry,
- `packages_delivered` totals the number of input packages,
- distances are non-negative.

## 10. Author

Prepared by Rohit Shinde

Python Developer Assignment Round – Nexgensis Technologies Pvt. Ltd.