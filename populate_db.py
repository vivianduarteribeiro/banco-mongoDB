from faker import Faker
from pymongo import MongoClient
import os, random
from datetime import datetime, timedelta

def get_client():
    uri = os.getenv("MONGO_URI", "mongodb://root:example@mongo:27017/")
    return MongoClient(uri)

def generate_orders(n=200):
    fake = Faker("pt_BR")
    orders = []
    categories = ["Eletrônicos", "Moda", "Casa", "Beleza", "Esportes"]
    for _ in range(n):
        order_date = datetime.now() - timedelta(days=random.randint(0, 180))
        order = {
            "order_id": fake.uuid4(),
            "customer": {
                "name": fake.name(),
                "email": fake.email(),
                "cep": fake.postcode(),
                "city": fake.city(),
                "state": fake.state_abbr()
            },
            "items": [{
                "sku": fake.bothify(text="SKU-####"),
                "name": fake.word().title(),
                "category": random.choice(categories),
                "price": round(random.uniform(10, 2000), 2),
                "quantity": random.randint(1, 3)
            }],
            "order_total": 0.0,
            "order_date": order_date,
            "status": random.choice(["processing", "shipped", "delivered", "cancelled"]),
            "shipping_region": random.choice(["SE", "NE", "S", "CW", "N"]),
        }
        order["order_total"] = sum(i["price"] * i["quantity"] for i in order["items"])
        orders.append(order)
    return orders

def populate(n=200):
    client = get_client()
    db = client[os.getenv("MONGO_DB", "eshop")]
    coll = db[os.getenv("MONGO_COLLECTION", "orders")]
    orders = generate_orders(n)
    coll.insert_many(orders)
    print(f"Inserted {len(orders)} documents")

if __name__ == "__main__":
    populate(300)
