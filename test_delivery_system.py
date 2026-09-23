import unittest
from pathlib import Path

from main import (
    euclidean_distance,
    load_json,
    normalize_locations,
    normalize_packages,
    simulate,
)


class DeliverySystemTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent

    def test_distance(self):
        self.assertAlmostEqual(euclidean_distance((0, 0), (3, 4)), 5.0)

    def test_base_case_delivers_every_package(self):
        data = load_json(self.root / "base_case.json")
        warehouses = normalize_locations(data["warehouses"], "warehouse")
        agents = normalize_locations(data["agents"], "agent")
        packages = normalize_packages(data["packages"])

        report, routes = simulate(warehouses, agents, packages)

        total_delivered = sum(
            value["packages_delivered"]
            for key, value in report.items()
            if key != "best_agent"
        )
        self.assertEqual(total_delivered, len(packages))
        self.assertEqual(len(routes), len(packages))
        self.assertIn(report["best_agent"], agents)

    def test_both_location_schemas(self):
        as_dict = {"W1": [0, 0], "W2": [10, 10]}
        as_list = [
            {"id": "W1", "location": [0, 0]},
            {"id": "W2", "location": [10, 10]},
        ]
        self.assertEqual(
            normalize_locations(as_dict, "warehouse"),
            normalize_locations(as_list, "warehouse"),
        )


if __name__ == "__main__":
    unittest.main()
