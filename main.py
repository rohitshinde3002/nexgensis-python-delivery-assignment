"""
FastBox Mystery Delivery System
Nexgensis Technologies - Python Developer Assignment

Usage:
    python main.py
    python main.py --input base_case.json
    python main.py --input test_cases/test_case_1.json --output report.json
    python main.py --input base_case.json --detailed

The required report.json contains the exact core fields requested by the assignment.
A detailed route report can also be generated with --detailed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    """Read and parse a JSON input file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input JSON must contain a top-level object.")
    return data


def normalize_locations(raw: Any, item_name: str) -> dict[str, tuple[float, float]]:
    """
    Accept both schemas supplied in the assignment package:
      {"W1": [x, y], ...}
    and
      [{"id": "W1", "location": [x, y]}, ...]
    """
    result: dict[str, tuple[float, float]] = {}

    if isinstance(raw, dict):
        items = raw.items()
        for item_id, location in items:
            result[str(item_id)] = validate_point(location, f"{item_name} {item_id}")
        return result

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict) or "id" not in item:
                raise ValueError(f"Every {item_name} must have an 'id'.")
            location = item.get("location")
            if location is None:
                raise ValueError(f"{item_name} {item['id']} is missing 'location'.")
            result[str(item["id"])] = validate_point(
                location, f"{item_name} {item['id']}"
            )
        return result

    raise ValueError(f"'{item_name}s' must be an object or list.")


def validate_point(value: Any, label: str) -> tuple[float, float]:
    """Validate and convert a coordinate pair."""
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{label} must be a coordinate pair [x, y].")
    try:
        return float(value[0]), float(value[1])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} contains invalid coordinates.") from exc


def normalize_packages(raw: Any) -> list[dict[str, Any]]:
    """Normalize package records from the assignment's JSON schema."""
    if not isinstance(raw, list):
        raise ValueError("'packages' must be a list.")

    packages = []
    for package in raw:
        if not isinstance(package, dict):
            raise ValueError("Each package must be an object.")

        package_id = package.get("id")
        warehouse_id = package.get("warehouse_id", package.get("warehouse"))
        destination = package.get("destination")

        if package_id is None or warehouse_id is None or destination is None:
            raise ValueError(
                "Each package needs id, warehouse/warehouse_id, and destination."
            )

        packages.append(
            {
                "id": str(package_id),
                "warehouse_id": str(warehouse_id),
                "destination": validate_point(destination, f"package {package_id} destination"),
            }
        )
    return packages


def euclidean_distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Return Euclidean distance between two 2-D points."""
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def nearest_agent(
    warehouse_location: tuple[float, float],
    agents: dict[str, tuple[float, float]],
) -> str:
    """
    Find the nearest agent to a warehouse.

    Assumption for ties:
    If two agents have exactly the same distance, choose the lexicographically
    smaller agent ID. This makes the result deterministic.
    """
    return min(
        agents,
        key=lambda agent_id: (
            euclidean_distance(agents[agent_id], warehouse_location),
            agent_id,
        ),
    )


def assign_packages(
    warehouses: dict[str, tuple[float, float]],
    agents: dict[str, tuple[float, float]],
    packages: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Assign every package to the nearest agent using the agent's initial position."""
    assignments = {agent_id: [] for agent_id in agents}

    for package in packages:
        warehouse_id = package["warehouse_id"]
        if warehouse_id not in warehouses:
            raise ValueError(
                f"Package {package['id']} references unknown warehouse {warehouse_id}."
            )

        agent_id = nearest_agent(warehouses[warehouse_id], agents)
        assignments[agent_id].append(package)

    return assignments


def simulate(
    warehouses: dict[str, tuple[float, float]],
    agents: dict[str, tuple[float, float]],
    packages: list[dict[str, Any]],
    add_random_delay: bool = False,
    delay_min: int = 5,
    delay_max: int = 20,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Simulate delivery in package input order within each agent's assignment.

    Routing assumption:
    - Assignment is based on the agent's INITIAL location to the package warehouse,
      exactly as stated in the task.
    - Once assigned, packages for an agent are processed in the original JSON order.
    - For the first package, travel starts at the agent's initial location.
    - For subsequent packages, the agent starts from the previous delivery destination.
    - Each package route is: current position -> warehouse -> destination.
    - An agent is allowed to deliver multiple packages, including from the same
      warehouse, and no package is delivered twice.
    - Distance is continuous Euclidean distance and is rounded only in output.
    """
    assignments = assign_packages(warehouses, agents, packages)

    summary: dict[str, Any] = {}
    routes: list[dict[str, Any]] = []
    delivered_count = 0

    rng = random.Random()

    for agent_id, assigned_packages in assignments.items():
        current_position = agents[agent_id]
        total_distance = 0.0

        for package in assigned_packages:
            warehouse = warehouses[package["warehouse_id"]]
            destination = package["destination"]

            pickup_distance = euclidean_distance(current_position, warehouse)
            delivery_distance = euclidean_distance(warehouse, destination)
            route_distance = pickup_distance + delivery_distance

            delay = 0
            if add_random_delay:
                delay = rng.randint(delay_min, delay_max)

            total_distance += route_distance
            routes.append(
                {
                    "agent": agent_id,
                    "package": package["id"],
                    "warehouse": package["warehouse_id"],
                    "pickup_distance": round(pickup_distance, 2),
                    "delivery_distance": round(delivery_distance, 2),
                    "distance": round(route_distance, 2),
                    "delay_minutes": delay,
                }
            )

            current_position = destination
            delivered_count += 1

        count = len(assigned_packages)
        efficiency = total_distance / count if count else 0.0

        summary[agent_id] = {
            "packages_delivered": count,
            "total_distance": round(total_distance, 2),
            "efficiency": round(efficiency, 2),
        }

    # "Most efficient" is defined as the smallest average distance per package.
    # If tied, choose the lexicographically smaller agent ID.
    if delivered_count:
        best_agent = min(
            agents,
            key=lambda agent_id: (
                summary[agent_id]["efficiency"] if summary[agent_id]["packages_delivered"] else math.inf,
                agent_id,
            ),
        )
    else:
        best_agent = None

    summary["best_agent"] = best_agent

    if delivered_count != len(packages):
        raise RuntimeError(
            f"Delivery count mismatch: delivered {delivered_count} of {len(packages)}."
        )

    return summary, routes


def save_json(data: dict[str, Any], path: str | Path) -> None:
    """Save JSON with readable indentation."""
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_csv(summary: dict[str, Any], path: str | Path) -> None:
    """Bonus: export agent performance to CSV."""
    rows = []
    for agent_id, values in summary.items():
        if agent_id == "best_agent":
            continue
        rows.append(
            {
                "agent": agent_id,
                "packages_delivered": values["packages_delivered"],
                "total_distance": values["total_distance"],
                "efficiency": values["efficiency"],
            }
        )

    with Path(path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["agent", "packages_delivered", "total_distance", "efficiency"],
        )
        writer.writeheader()
        writer.writerows(rows)


def print_ascii_routes(
    warehouses: dict[str, tuple[float, float]],
    agents: dict[str, tuple[float, float]],
    routes: list[dict[str, Any]],
) -> None:
    """Bonus: simple text visualization of route relationships."""
    print("\nRoute visualization")
    print("-" * 60)
    for route in routes:
        print(
            f"{route['agent']} -> {route['warehouse']} -> {route['package']} "
            f"| {route['distance']:.2f} distance units"
        )
    print("-" * 60)
    print(f"Agents: {', '.join(agents)}")
    print(f"Warehouses: {', '.join(warehouses)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FastBox delivery simulator")
    parser.add_argument(
        "--input",
        default="base_case.json",
        help="Path to input JSON (default: base_case.json)",
    )
    parser.add_argument(
        "--output",
        default="report.json",
        help="Path to required report JSON (default: report.json)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Also create route_report.json and show ASCII routes.",
    )
    parser.add_argument(
        "--delays",
        action="store_true",
        help="Bonus: add random delivery delay minutes to detailed route output.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Bonus: create agent_report.csv.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    data = load_json(args.input)
    warehouses = normalize_locations(data.get("warehouses"), "warehouse")
    agents = normalize_locations(data.get("agents"), "agent")
    packages = normalize_packages(data.get("packages"))

    if not warehouses:
        raise ValueError("At least one warehouse is required.")
    if not agents:
        raise ValueError("At least one agent is required.")

    report, routes = simulate(
        warehouses,
        agents,
        packages,
        add_random_delay=args.delays,
    )

    save_json(report, args.output)

    print(json.dumps(report, indent=4))
    print(f"\nSaved report to: {args.output}")

    if args.detailed:
        detailed = {"routes": routes, "best_agent": report["best_agent"]}
        save_json(detailed, "route_report.json")
        print_ascii_routes(warehouses, agents, routes)
        print("Saved detailed route report to: route_report.json")

    if args.csv:
        save_csv(report, "agent_report.csv")
        print("Saved CSV to: agent_report.csv")


if __name__ == "__main__":
    main()
