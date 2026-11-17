#!/usr/bin/env python3
"""Generate a reproducible synthetic e-commerce dataset.

Outputs (in data/):
    users.csv, products.csv, orders.csv, order_items.csv

Usage:
    python scripts/generate_ecommerce.py --rows 500 --seed 42
    (--rows = number of orders; users/products scale with it)
"""
import argparse
import csv
import math
import random
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SEED = 42
DEFAULT_ORDERS = 500
OUT_DIR = Path(__file__).resolve().parent.parent / "data"

START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 11, 16)
EDGE_RATE = 0.05

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "David", "Elizabeth", "William", "Susan", "Sophie", "Lukas", "Emma", "Liam",
               "Olivia", "Noah", "Ava", "Mateo", "Yuki", "Hiro", "Priya", "Arjun", "Chloé",
               "Lucas", "Mia", "Ethan", "Isabella", "Aiden", "Grace", "Ben", "Hannah", "Oscar"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Müller", "Schmidt",
              "Dubois", "Martin", "Tanaka", "Sato", "Patel", "Sharma", "Nguyen", "Kim", "Lee",
              "O'Brien", "Clark", "Lewis", "Walker", "Young"]
UNICODE_NAMES = [("José", "Ñúñez"), ("李", "小龙"), ("Zoë", "Ångström"), ("Анна", "Иванова"),
                 ("محمد", "الأحمد"), ("Søren", "Kierkegård"), ("😀Emoji", "Tester"), ("Đặng", "Thị Ngọc")]

COUNTRIES = [  # (country, weight, cities, phone prefix)
    ("US", 45, ["New York", "Los Angeles", "Chicago", "Austin", "Seattle", "Miami"], "+1"),
    ("GB", 14, ["London", "Manchester", "Bristol", "Leeds"], "+44"),
    ("DE", 10, ["Berlin", "Munich", "Hamburg", "Cologne"], "+49"),
    ("CA", 9, ["Toronto", "Vancouver", "Montreal"], "+1"),
    ("FR", 7, ["Paris", "Lyon", "Marseille"], "+33"),
    ("AU", 6, ["Sydney", "Melbourne", "Brisbane"], "+61"),
    ("JP", 5, ["Tokyo", "Osaka", "Kyoto"], "+81"),
    ("IN", 4, ["Mumbai", "Bangalore", "Delhi"], "+91"),
]
USER_STATUS = (["active", "inactive", "banned"], [80, 15, 5])

CATEGORIES = {  # name: (weight, log-normal mu, sigma, nouns, adjectives)
    "Electronics": (22, math.log(120), 0.9, ["Headphones", "Charger", "Speaker", "Smartwatch", "Keyboard", "Mouse", "Webcam", "Monitor"], ["Wireless", "Pro", "Ultra", "Compact", "Smart"]),
    "Apparel": (25, math.log(35), 0.6, ["T-Shirt", "Hoodie", "Jeans", "Sneakers", "Jacket", "Socks", "Cap"], ["Classic", "Slim-Fit", "Organic", "Vintage", "Sport"]),
    "Home & Kitchen": (18, math.log(40), 0.8, ["Mug", "Knife Set", "Blender", "Lamp", "Pillow", "Frying Pan", "Candle"], ["Ceramic", "Stainless", "Cozy", "Modern", "Rustic"]),
    "Beauty": (12, math.log(22), 0.5, ["Moisturizer", "Serum", "Lip Balm", "Shampoo", "Face Mask"], ["Hydrating", "Natural", "Vegan", "Daily", "Repair"]),
    "Sports": (10, math.log(45), 0.8, ["Yoga Mat", "Dumbbells", "Water Bottle", "Resistance Bands", "Running Belt"], ["Eco", "Heavy-Duty", "Lightweight", "Pro", "Travel"]),
    "Books": (8, math.log(16), 0.4, ["Cookbook", "Novel", "Notebook", "Planner", "Guide"], ["Illustrated", "Hardcover", "Pocket", "Deluxe", "Annotated"]),
    "Toys": (5, math.log(25), 0.6, ["Puzzle", "Building Set", "Plush Bear", "Board Game", "RC Car"], ["Mini", "Giant", "Classic", "Family", "Junior"]),
}

ORDER_STATUS = (["delivered", "shipped", "processing", "cancelled", "refunded"], [62, 15, 8, 10, 5])
PAYMENT = (["credit_card", "paypal", "apple_pay", "gift_card"], [60, 20, 12, 8])
HOUR_WEIGHTS = [1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 7, 7, 6, 6, 6, 7, 8, 9, 9, 8, 5, 3]
EDGE_NOTES = ["", "Please leave at the door 🚪📦", "Geschenk – bitte ohne Rechnung", "请在下午送货",
              "L" + "o" * 254, "Ring twice 🔔🔔", "N/A", "  "]


def money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rand_date(rng, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def gen_users(rng, n):
    users, seen_emails = [], set()
    countries = [c[0] for c in COUNTRIES]
    cweights = [c[1] for c in COUNTRIES]
    cinfo = {c[0]: c for c in COUNTRIES}
    for uid in range(1, n + 1):
        edge = rng.random() < EDGE_RATE
        if edge and rng.random() < 0.6:
            first, last = rng.choice(UNICODE_NAMES)
        else:
            first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        country = rng.choices(countries, cweights)[0]
        _, _, cities, prefix = cinfo[country]
        city = rng.choice(cities)
        phone = f"{prefix} {rng.randint(200, 999)} {rng.randint(100, 999)} {rng.randint(1000, 9999)}"

        base = "".join(ch for ch in f"{first}.{last}".lower() if ch.isascii() and (ch.isalnum() or ch == "."))
        base = base.strip(".") or f"user{uid}"
        email = f"{base}@example.com"
        if email in seen_emails:
            email = f"{base}{uid}@example.com"
        seen_emails.add(email)

        if edge:  # inject non-key edge cases
            kind = rng.choice(["null_city", "empty_phone", "null_phone", "long_name", "null_last"])
            if kind == "null_city":
                city = None
            elif kind == "empty_phone":
                phone = ""
            elif kind == "null_phone":
                phone = None
            elif kind == "long_name":
                first = ("Maximilian" * 26)[:255]
            elif kind == "null_last":
                last = None
        elif rng.random() < 0.08:
            phone = None  # realistic: some users don't provide phone

        users.append({
            "id": uid, "first_name": first, "last_name": last, "email": email, "phone": phone,
            "country": country, "city": city,
            "signup_date": rand_date(rng, START_DATE, END_DATE - timedelta(days=14)),
            "status": rng.choices(*USER_STATUS)[0],
        })

    # duplicate-looking but distinct records: same name, different id/email
    for i in range(min(4, n // 50)):
        src, dst = users[i], users[-(i + 1)]
        dst["first_name"], dst["last_name"] = src["first_name"], src["last_name"]
    return users


def gen_products(rng, n):
    products = []
    cats = list(CATEGORIES)
    weights = [CATEGORIES[c][0] for c in cats]
    counters = {}
    for pid in range(1, n + 1):
        cat = rng.choices(cats, weights)[0]
        _, mu, sigma, nouns, adjs = CATEGORIES[cat]
        counters[cat] = counters.get(cat, 0) + 1
        price = money(min(max(rng.lognormvariate(mu, sigma), 2.99), 2499))
        price = money(math.floor(price) + Decimal("0.99")) if rng.random() < 0.7 else price
        products.append({
            "id": pid,
            "sku": f"{cat[:3].upper()}-{pid:05d}",
            "name": f"{rng.choice(adjs)} {rng.choice(nouns)}",
            "category": cat,
            "unit_price": price,
            "stock_qty": int(rng.paretovariate(1.2) * 20) if rng.random() > 0.06 else 0,
            "is_active": rng.random() < 0.92,
        })
    # targeted edge cases (non-key fields only)
    edges = [
        ("unit_price", Decimal("0.00")),           # free sample
        ("unit_price", Decimal("99999.99")),       # max boundary
        ("stock_qty", -5),                         # backorder / negative
        ("stock_qty", 1_000_000),                  # very large
        ("name", "Café Crème ☕ Édition Spéciale"),
        ("name", "无线蓝牙耳机 🎧"),
        ("name", ("Extremely Long Product Name " * 10)[:255]),
    ]
    for (field, value), p in zip(edges, rng.sample(products, len(edges))):
        p[field] = value
        if field == "unit_price":
            p["is_active"] = True
    # duplicate-looking products: same name, different id/sku
    products[-1]["name"] = products[0]["name"]
    products[-1]["category"] = products[0]["category"]
    return products


def gen_orders(rng, n, users, products):
    orders, items = [], []
    # skewed purchase frequency: few heavy buyers, many one-off buyers
    eligible = [u for u in users if u["status"] != "banned"] or users
    uweights = [rng.paretovariate(1.5) for _ in eligible]
    active_products = [p for p in products if p["is_active"]]
    # popularity: cheap items sell more; ultra-expensive edge item rarely
    pweights = [1 / math.sqrt(float(p["unit_price"]) + 5) * rng.uniform(0.3, 2.0) for p in active_products]
    item_id = 1
    for oid in range(1, n + 1):
        user = rng.choices(eligible, uweights)[0]
        d = rand_date(rng, user["signup_date"], END_DATE)
        # weekends slightly busier: re-roll some weekday dates
        if d.weekday() < 5 and rng.random() < 0.15:
            d = rand_date(rng, user["signup_date"], END_DATE)
        hour = rng.choices(range(24), HOUR_WEIGHTS)[0]
        order_dt = datetime(d.year, d.month, d.day, hour, rng.randint(0, 59), rng.randint(0, 59))

        n_items = rng.choices([1, 2, 3, 4, 5, 6], [50, 25, 12, 7, 4, 2])[0]
        chosen = []
        while len(chosen) < n_items:
            p = rng.choices(active_products, pweights)[0]
            if p not in chosen:
                chosen.append(p)
        subtotal = Decimal("0.00")
        for p in chosen:
            qty = rng.choices([1, 2, 3, 4, 5, 10], [70, 17, 6, 3, 2, 2])[0]
            line = money(p["unit_price"] * qty)
            subtotal += line
            items.append({"id": item_id, "order_id": oid, "product_id": p["id"],
                          "quantity": qty, "unit_price": p["unit_price"], "line_total": line})
            item_id += 1

        discount = Decimal("0.00")
        if rng.random() < 0.25:
            discount = money(subtotal * Decimal(rng.choice([5, 10, 15, 20, 25])) / 100)
        shipping = Decimal("0.00") if subtotal >= 50 else Decimal(rng.choice(["4.99", "4.99", "9.99"]))
        total = subtotal - discount + shipping

        note = None
        if rng.random() < EDGE_RATE:
            note = rng.choice(EDGE_NOTES)
        elif rng.random() < 0.05:
            note = rng.choice(["Gift wrap please", "Call on arrival", "Leave with neighbor"])

        orders.append({
            "id": oid, "user_id": user["id"], "order_date": order_dt.isoformat(sep=" "),
            "status": rng.choices(*ORDER_STATUS)[0], "payment_method": rng.choices(*PAYMENT)[0],
            "shipping_country": user["country"], "item_count": len(chosen),
            "subtotal": subtotal, "discount": discount, "shipping_fee": shipping, "total": total,
            "note": note,
        })
    return orders, items


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:  # None -> "NULL" marker so null is distinguishable from empty string
            w.writerow({k: ("NULL" if v is None else v) for k, v in r.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=DEFAULT_ORDERS, help="number of orders")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--users", type=int, help="number of users (default: rows * 0.4)")
    ap.add_argument("--products", type=int, help="number of products (default: rows * 0.16, min 20)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    n_users = args.users or max(20, int(args.rows * 0.4))
    n_products = args.products or max(20, int(args.rows * 0.16))

    users = gen_users(rng, n_users)
    products = gen_products(rng, n_products)
    orders, items = gen_orders(rng, args.rows, users, products)

    for name, rows in [("users", users), ("products", products), ("orders", orders), ("order_items", items)]:
        write_csv(OUT_DIR / f"{name}.csv", rows)
        print(f"wrote {len(rows):>5} rows -> data/{name}.csv")


if __name__ == "__main__":
    main()
