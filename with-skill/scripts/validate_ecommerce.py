#!/usr/bin/env python3
"""Validate data/*.csv produced by generate_ecommerce.py (FKs, sums, dates)."""
import csv
from collections import Counter, defaultdict
from decimal import Decimal as D
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


u, p, o, i = load("users"), load("products"), load("orders"), load("order_items")
uid = {r["id"]: r for r in u}
pid = {r["id"]: r for r in p}
oid = {r["id"] for r in o}
errs = []
for name, rows in [("users", u), ("products", p), ("orders", o), ("order_items", i)]:
    if len({r["id"] for r in rows}) != len(rows):
        errs.append(("duplicate pk", name))
errs += [("bad user fk", r["id"]) for r in o if r["user_id"] not in uid]
errs += [("bad order fk", r["id"]) for r in i if r["order_id"] not in oid]
errs += [("bad product fk", r["id"]) for r in i if r["product_id"] not in pid]
errs += [("line_total", r["id"]) for r in i if D(r["unit_price"]) * int(r["quantity"]) != D(r["line_total"])]
sub, cnt = defaultdict(D), Counter()
for r in i:
    sub[r["order_id"]] += D(r["line_total"])
    cnt[r["order_id"]] += 1
for r in o:
    if D(r["subtotal"]) != sub[r["id"]]:
        errs.append(("subtotal", r["id"]))
    if D(r["subtotal"]) - D(r["discount"]) + D(r["shipping_fee"]) != D(r["total"]):
        errs.append(("total", r["id"]))
    if int(r["item_count"]) != cnt[r["id"]]:
        errs.append(("item_count", r["id"]))
    if r["order_date"][:10] < uid[r["user_id"]]["signup_date"]:
        errs.append(("order before signup", r["id"]))

print(f"rows: users={len(u)} products={len(p)} orders={len(o)} order_items={len(i)}")
print("constraint errors:", len(errs), errs[:10])
print("order status:", dict(Counter(r["status"] for r in o)))
per_user = Counter(r["user_id"] for r in o)
print(f"users with orders: {len(per_user)}, top buyer: {per_user.most_common(1)}")
t = sorted(D(r["total"]) for r in o)
print(f"order total min/median/max: {t[0]} / {t[len(t)//2]} / {t[-1]}")
print("orders with note:", sum(r["note"] != "NULL" for r in o))
print("users with a NULL field:", sum("NULL" in r.values() for r in u),
      "| empty phone:", sum(r["phone"] == "" for r in u))
raise SystemExit(1 if errs else 0)
