import importlib.util
import json
import sys
from datetime import datetime, timezone
from math import isclose
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PRODUCER_PATH = ROOT / "0_synthetic_data" / "04_eventhub_orders.py"
spec = importlib.util.spec_from_file_location("eventhub_orders", PRODUCER_PATH)
eventhub_orders = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eventhub_orders)

sys.path.insert(0, str(ROOT / "1_pipeline_bronze_to_gold"))
from business_rules import REALIZED_ORDER_STATUSES


RESTAURANTS = ["REST-001"]
CUSTOMERS = ["CUST-001"]
MENU = {
    "REST-001": [
        {
            "item_id": "ITEM-001",
            "name": "Soup",
            "category": "Starter",
            "price": 5.50,
        },
        {
            "item_id": "ITEM-002",
            "name": "Pie",
            "category": "Main Course",
            "price": 12.00,
        },
    ]
}


class OrderGenerationTests(unittest.TestCase):
    def make_order(self):
        return eventhub_orders.generate_order(RESTAURANTS, CUSTOMERS, MENU)

    def test_payload_matches_bronze_contract(self):
        order = self.make_order()
        required = {
            "order_id", "timestamp", "restaurant_id", "customer_id",
            "order_type", "items", "total_amount", "payment_method",
            "order_status",
        }
        self.assertTrue(required.issubset(order))
        self.assertIsInstance(order["items"], list)
        self.assertGreater(len(order["items"]), 0)
        self.assertEqual(
            set(order["items"][0]),
            {"item_id", "name", "category", "quantity", "unit_price", "subtotal"},
        )
        self.assertIsInstance(order["items"][0]["quantity"], int)
        self.assertIsInstance(order["items"][0]["unit_price"], (int, float))
        self.assertIsInstance(order["items"][0]["subtotal"], (int, float))
        json.dumps(order)  # confirms the Event Hub serialization contract

    def test_order_and_item_amounts_reconcile(self):
        order = self.make_order()
        item_total = sum(item["subtotal"] for item in order["items"])
        self.assertTrue(isclose(item_total, order["total_amount"], abs_tol=0.01))
        for item in order["items"]:
            self.assertTrue(
                isclose(
                    item["subtotal"],
                    round(item["quantity"] * item["unit_price"], 2),
                    abs_tol=0.01,
                )
            )

    def test_item_ids_are_unique_within_order(self):
        order = self.make_order()
        item_ids = [item["item_id"] for item in order["items"]]
        self.assertEqual(len(item_ids), len(set(item_ids)))

    def test_generated_relationships_reference_known_entities(self):
        order = self.make_order()
        self.assertIn(order["restaurant_id"], RESTAURANTS)
        self.assertIn(order["customer_id"], CUSTOMERS)
        self.assertTrue(all(item["item_id"] in {"ITEM-001", "ITEM-002"} for item in order["items"]))

    def test_event_timestamp_is_utc(self):
        order = self.make_order()
        timestamp = datetime.fromisoformat(order["timestamp"].replace("Z", "+00:00"))
        self.assertEqual(timestamp.tzinfo, timezone.utc)

    def test_realized_status_rule_matches_generators(self):
        self.assertEqual(set(REALIZED_ORDER_STATUSES), {"delivered", "completed"})
        self.assertTrue(set(REALIZED_ORDER_STATUSES).issubset(set(eventhub_orders.ORDER_STATUSES) | {"completed"}))
        self.assertTrue({"pending", "confirmed", "preparing", "ready"}.isdisjoint(REALIZED_ORDER_STATUSES))


if __name__ == "__main__":
    unittest.main()
