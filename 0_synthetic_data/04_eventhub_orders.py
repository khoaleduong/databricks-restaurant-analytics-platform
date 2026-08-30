import os
import json
import random
import time
from datetime import datetime, timezone

# Load reference data lazily so generation can run without cloud credentials.
script_dir = os.path.dirname(os.path.abspath(__file__))
RESTAURANTS = []
CUSTOMERS = []
MENU_BY_RESTAURANT = {}

ORDER_TYPES = ["dine_in", "takeaway", "delivery"]
PAYMENT_METHODS = ["cash", "card", "wallet"]
ORDER_STATUSES = ["pending", "confirmed", "preparing", "ready", "delivered"]

def load_reference_data():
    import pandas as pd

    df_restaurants = pd.read_csv(os.path.join(script_dir, "data", "restaurants.csv"))
    df_customers = pd.read_csv(os.path.join(script_dir, "data", "customers.csv"))
    df_menu_items = pd.read_csv(os.path.join(script_dir, "data", "menu_items.csv"))

    return (
        df_restaurants["restaurant_id"].tolist(),
        df_customers["customer_id"].tolist(),
        df_menu_items.groupby("restaurant_id").apply(
            lambda x: x.to_dict("records")
        ).to_dict(),
    )


def generate_order(restaurants=None, customers=None, menu_by_restaurant=None):
    # Each message is one immutable order; order_id identifies it.
    if restaurants is None or customers is None or menu_by_restaurant is None:
        restaurants, customers, menu_by_restaurant = load_reference_data()

    order_date = datetime.now(timezone.utc).replace(microsecond=0)
    order_timestamp = order_date.isoformat().replace("+00:00", "Z")
    restaurant_id = random.choice(restaurants)
    customer_id = random.choice(customers)
    
    menu_items = menu_by_restaurant[restaurant_id]
    num_items = random.randint(1, min(5, len(menu_items)))
    selected_items = random.sample(menu_items, num_items)
    
    items = []
    total_amount = 0.0
    
    for item in selected_items:
        quantity = random.randint(1, 3)
        subtotal = item["price"] * quantity
        total_amount += subtotal
        
        items.append({
            "item_id": item["item_id"],
            "name": item["name"],
            "category": item["category"],
            "quantity": quantity,
            "unit_price": item["price"],
            "subtotal": round(subtotal, 2)
        })
    
    order_id = f"ORD-{order_date.strftime('%Y%m%d')}-{random.randint(100000, 999999)}"
    
    return {
        "order_id": order_id,
        "timestamp": order_timestamp,
        "restaurant_id": restaurant_id,
        "customer_id": customer_id,
        "order_type": random.choice(ORDER_TYPES),
        "items": items,
        "total_amount": round(total_amount, 2),
        "payment_method": random.choice(PAYMENT_METHODS),
        "order_status": random.choice(ORDER_STATUSES),
        "created_at": order_timestamp
    }

def stream_to_eventhub(interval_seconds=3, max_orders=30):
    from azure.eventhub import EventHubProducerClient, EventData
    from dotenv import load_dotenv

    load_dotenv()
    eventhub_connection_string = os.getenv("EVENTHUB_CONNECTION_STRING")
    eventhub_name = os.getenv("EVENTHUB_NAME")

    global RESTAURANTS, CUSTOMERS, MENU_BY_RESTAURANT
    RESTAURANTS, CUSTOMERS, MENU_BY_RESTAURANT = load_reference_data()

    producer = EventHubProducerClient.from_connection_string(
        conn_str=eventhub_connection_string,
        eventhub_name=eventhub_name
    )
    
    print(f"\n\nStreaming to Event Hub: {eventhub_name}")
    order_count = 0
    
    try:
        while order_count < max_orders:
            order = generate_order()
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(json.dumps(order)))
            producer.send_batch(event_data_batch)
            
            order_count += 1
            print(f"[{order_count}/{max_orders}] {order['order_id']} | {order['restaurant_id']} | GBP £{order['total_amount']}")
            
            if order_count < max_orders:
                time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        producer.close()
        pass

if __name__ == "__main__":
    stream_to_eventhub(interval_seconds=3, max_orders=30)
