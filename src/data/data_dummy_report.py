# from datetime import datetime, timedelta
# import random
#
#
# def generate_dummy_sales():
#     products = [
#         {"id": 1, "name": "Cahier 96p", "price": 2.5},
#         {"id": 2, "name": "Stylo bleu", "price": 1.2},
#         {"id": 3, "name": "Règle 30cm", "price": 1.5},
#         {"id": 4, "name": "Gomme", "price": 0.5},
#         {"id": 5, "name": "Crayon HB", "price": 0.3},
#         {"id": 6, "name": "Feutre", "price": 1.8},
#         {"id": 7, "name": "Taille-crayon", "price": 0.7},
#         {"id": 8, "name": "Classeur", "price": 4.2},
#         {"id": 9, "name": "Chemise", "price": 1.0},
#         {"id": 10, "name": "Pochette", "price": 0.8}
#     ]
#
#     sales = []
#     start_date = datetime.now() - timedelta(days=365)
#
#     for i in range(500):
#         num_items = random.randint(1, min(4, len(products)))
#         items = random.sample(products, num_items)
#
#         sale_items = []
#         for item in items:
#             quantity = random.randint(1, 10)
#             item_total = round(item["price"] * quantity, 2)
#             sale_items.append({
#                 "product": item["name"],
#                 "quantity": quantity,
#                 "unit_price": item["price"],
#                 "total": item_total  # Ceci est maintenant correctement défini
#             })
#
#         sale = {
#             "invoice_id": f"FAC-{1000 + i}",
#             "date": start_date + timedelta(days=random.randint(0, 365),
#                                            hours=random.randint(8, 20)),
#             "items": sale_items,
#             "total": round(sum(item["total"] for item in sale_items), 2),
#             "payment_method": random.choice(["Cash", "Carte", "Virement"]),
#             "client": f"Client-{random.randint(1, 50)}"
#         }
#         sales.append(sale)
#
#     return sales
#
#
# SALES_DATA = generate_dummy_sales()

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