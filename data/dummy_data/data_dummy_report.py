from datetime import datetime, timedelta
import random

products = [
    {"id": 1, "name": "Cahier 96p", "price": 2.5, "type": "unitaire"},
    {"id": 2, "name": "Stylo bleu", "price": 1.2, "type": "unitaire"},
    {"id": 3, "name": "Pack stylos (10)", "price": 10.0, "type": "paquet", "contains": [2]*10},
    {"id": 4, "name": "Carton cahiers (50)", "price": 100.0, "type": "carton", "contains": [1]*50}
]

def generate_sales():
    sales = []
    for i in range(100):
        items = []
        for _ in range(random.randint(1, 4)):  # 1-4 articles par vente
            product = random.choice(products)
            if product["type"] in ["paquet", "carton"]:
                items.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "type": product["type"],
                    "quantity": 1,
                    "unit_price": product["price"],
                    "total": product["price"]
                })
            else:
                quantity = random.randint(1, 10)
                items.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "type": product["type"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "total": product["price"] * quantity
                })

        sales.append({
            "invoice_id": f"INV-{1000+i}",
            "date": datetime.now() - timedelta(days=random.randint(0, 365)),
            "items": items,
            "total": sum(item["total"] for item in items),
            "payment_method": random.choice(["Cash", "Carte", "Virement"]),
            "client": f"CLIENT-{random.randint(1, 50)}"
        })
    return sales

SALES_DATA = generate_sales()