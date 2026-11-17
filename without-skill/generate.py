"""Generate synthetic e-commerce data: users, products, orders, order_items (CSV).

Usage: python3 generate.py [--orders 500] [--users 150] [--products 80] [--seed 42]
Stdlib only; deterministic for a given seed.
"""
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

FIRST = ["James", "Mary", "Liam", "Olivia", "Noah", "Emma", "Ava", "Ethan", "Sophia", "Mason",
         "Isabella", "Lucas", "Mia", "Logan", "Amelia", "Aiden", "Harper", "Elijah", "Evelyn", "Jacob",
         "Abigail", "Daniel", "Emily", "Henry", "Ella", "Jackson", "Chloe", "Sebastian", "Grace", "Leo",
         "Priya", "Wei", "Hiro", "Fatima", "Carlos", "Sofia", "Omar", "Yuna", "Mateo", "Aisha"]
LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
        "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
        "Martin", "Lee", "Kim", "Nguyen", "Patel", "Chen", "Wang", "Tanaka", "Silva", "Khan", "Clark", "Lewis"]
DOMAINS = ["example.com", "example.org", "example.net", "mail.test", "inbox.test"]
CITIES = [("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
          ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
          ("Dallas", "TX"), ("Austin", "TX"), ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA"),
          ("Portland", "OR"), ("Atlanta", "GA"), ("Miami", "FL"), ("Minneapolis", "MN"), ("Nashville", "TN")]
STREETS = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine St", "Elm St", "Washington Blvd",
           "Lake Rd", "Hill St", "Park Ave", "Sunset Blvd", "River Rd"]

CATALOG = {
    "Electronics": (["Wireless Earbuds", "Bluetooth Speaker", "USB-C Charger", "Smart Watch", "Webcam",
                     "Mechanical Keyboard", "Gaming Mouse", "Portable SSD", "Noise-Cancelling Headphones",
                     "Phone Case", "Tablet Stand", "HDMI Cable"], (9, 299)),
    "Home & Kitchen": (["French Press", "Chef's Knife", "Cutting Board", "Non-Stick Pan", "Electric Kettle",
                        "Throw Pillow", "Scented Candle", "Storage Bins", "Blender", "Dish Rack"], (8, 149)),
    "Clothing": (["Cotton T-Shirt", "Hoodie", "Denim Jeans", "Running Shorts", "Wool Socks",
                  "Rain Jacket", "Baseball Cap", "Leather Belt", "Flannel Shirt"], (10, 129)),
    "Sports & Outdoors": (["Yoga Mat", "Water Bottle", "Resistance Bands", "Camping Lantern",
                           "Hiking Backpack", "Jump Rope", "Dumbbell Set", "Bike Light"], (7, 199)),
    "Beauty": (["Face Moisturizer", "Lip Balm", "Shampoo", "Sunscreen SPF 50", "Hair Dryer",
                "Makeup Brush Set", "Body Wash"], (5, 89)),
    "Books": (["Mystery Novel", "Cookbook", "Sci-Fi Anthology", "Self-Help Guide", "Travel Guide",
               "Children's Picture Book", "History Biography"], (6, 45)),
    "Toys": (["Building Blocks", "Puzzle 1000pc", "Plush Bear", "RC Car", "Board Game", "Art Kit"], (8, 79)),
}
ADJ = ["Classic", "Pro", "Eco", "Deluxe", "Essential", "Premium", "Compact", "Ultra", "Everyday", "Lite"]
BRANDS = ["Northwind", "Acme", "Lumen", "Brightway", "Kestrel", "Oakline", "Vertex", "Summit", "Nimbus", "Harbor"]

STATUSES = [("delivered", 0.68), ("shipped", 0.12), ("processing", 0.07), ("pending", 0.04),
            ("cancelled", 0.06), ("returned", 0.03)]
PAYMENTS = [("credit_card", 0.55), ("debit_card", 0.18), ("paypal", 0.17), ("apple_pay", 0.06), ("gift_card", 0.04)]


def weighted(rng, pairs):
    return rng.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]


def make_users(rng, n, now):
    users, seen = [], set()
    for i in range(1, n + 1):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        base = f"{first}.{last}".lower()
        email, k = f"{base}@{rng.choice(DOMAINS)}", 1
        while email in seen:
            k += 1
            email = f"{base}{k}@{rng.choice(DOMAINS)}"
        seen.add(email)
        city, state = rng.choice(CITIES)
        signup = now - timedelta(days=rng.randint(30, 3 * 365), seconds=rng.randint(0, 86399))
        users.append({
            "user_id": i,
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": f"555-{rng.randint(100, 999)}-{rng.randint(1000, 9999)}",
            "street": f"{rng.randint(1, 9999)} {rng.choice(STREETS)}",
            "city": city,
            "state": state,
            "zip": f"{rng.randint(10000, 99999)}",
            "country": "US",
            "signup_date": signup.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return users


def make_products(rng, n, now):
    products, names = [], set()
    cats = list(CATALOG)
    while len(products) < n:
        cat = rng.choice(cats)
        items, (lo, hi) = CATALOG[cat]
        name = f"{rng.choice(BRANDS)} {rng.choice(ADJ)} {rng.choice(items)}"
        if name in names:
            continue
        names.add(name)
        price = round(rng.uniform(lo, hi), 2)
        pid = len(products) + 1
        products.append({
            "product_id": pid,
            "sku": f"{cat[:3].upper()}-{pid:05d}",
            "name": name,
            "category": cat,
            "price": f"{price:.2f}",
            "cost": f"{price * rng.uniform(0.35, 0.7):.2f}",
            "stock_quantity": rng.randint(0, 500),
            "rating": round(rng.uniform(2.5, 5.0), 1),
            "created_at": (now - timedelta(days=rng.randint(60, 4 * 365))).strftime("%Y-%m-%d"),
        })
    return products


def make_orders(rng, n, users, products, now):
    orders, items = [], []
    # Some users are repeat buyers: Pareto-ish weights
    user_weights = [rng.paretovariate(1.5) for _ in users]
    # Popular products get picked more often
    prod_weights = [rng.paretovariate(1.2) for _ in products]
    item_id = 0
    for oid in range(1, n + 1):
        user = rng.choices(users, weights=user_weights)[0]
        signup = datetime.strptime(user["signup_date"], "%Y-%m-%d %H:%M:%S")
        start = max(signup, now - timedelta(days=365))
        span = int((now - start).total_seconds())
        order_dt = start + timedelta(seconds=rng.randint(0, max(span, 1)))

        n_items = rng.choices([1, 2, 3, 4, 5], weights=[45, 28, 15, 8, 4])[0]
        chosen = set()
        while len(chosen) < n_items:
            chosen.add(rng.choices(range(len(products)), weights=prod_weights)[0])

        subtotal = 0.0
        for idx in chosen:
            p = products[idx]
            qty = rng.choices([1, 2, 3, 4], weights=[75, 17, 6, 2])[0]
            unit = float(p["price"])
            line = round(unit * qty, 2)
            subtotal += line
            item_id += 1
            items.append({
                "order_item_id": item_id,
                "order_id": oid,
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": f"{unit:.2f}",
                "line_total": f"{line:.2f}",
            })

        subtotal = round(subtotal, 2)
        discount = round(subtotal * rng.choice([0.1, 0.15, 0.2]), 2) if rng.random() < 0.2 else 0.0
        shipping = 0.0 if subtotal >= 50 else 5.99
        tax = round((subtotal - discount) * 0.08, 2)
        total = round(subtotal - discount + shipping + tax, 2)

        # Recent orders are less likely to be delivered yet
        age_days = (now - order_dt).days
        status = weighted(rng, STATUSES)
        if age_days < 3 and status in ("delivered", "returned"):
            status = rng.choice(["pending", "processing", "shipped"])

        shipped = delivered = ""
        if status in ("shipped", "delivered", "returned"):
            s = order_dt + timedelta(days=rng.randint(1, 3), hours=rng.randint(0, 23))
            shipped = s.strftime("%Y-%m-%d %H:%M:%S")
            if status in ("delivered", "returned"):
                d = s + timedelta(days=rng.randint(1, 7), hours=rng.randint(0, 23))
                delivered = min(d, now).strftime("%Y-%m-%d %H:%M:%S")

        orders.append({
            "order_id": oid,
            "order_number": f"ORD-{order_dt:%Y%m%d}-{oid:05d}",
            "user_id": user["user_id"],
            "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "payment_method": weighted(rng, PAYMENTS),
            "item_count": n_items,
            "subtotal": f"{subtotal:.2f}",
            "discount": f"{discount:.2f}",
            "shipping_fee": f"{shipping:.2f}",
            "tax": f"{tax:.2f}",
            "total": f"{total:.2f}",
            "shipping_city": user["city"],
            "shipping_state": user["state"],
            "shipped_at": shipped,
            "delivered_at": delivered,
        })
    # Renumber so order_id increases with order_date
    orders.sort(key=lambda o: o["order_date"])
    remap = {}
    for new_id, o in enumerate(orders, 1):
        remap[o["order_id"]] = new_id
        o["order_id"] = new_id
        o["order_number"] = f"ORD-{o['order_date'][:10].replace('-', '')}-{new_id:05d}"
    for it in items:
        it["order_id"] = remap[it["order_id"]]
    items.sort(key=lambda it: (it["order_id"], it["order_item_id"]))
    for i, it in enumerate(items, 1):
        it["order_item_id"] = i
    return orders, items


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders", type=int, default=500)
    ap.add_argument("--users", type=int, default=150)
    ap.add_argument("--products", type=int, default=80)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(Path(__file__).parent))
    a = ap.parse_args()

    rng = random.Random(a.seed)
    now = datetime(2026, 11, 17, 12, 0, 0)
    users = make_users(rng, a.users, now)
    products = make_products(rng, a.products, now)
    orders, items = make_orders(rng, a.orders, users, products, now)

    out = Path(a.out)
    for name, rows in [("users", users), ("products", products), ("orders", orders), ("order_items", items)]:
        write_csv(out / f"{name}.csv", rows)
        print(f"{name}.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
