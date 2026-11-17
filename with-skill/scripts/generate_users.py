#!/usr/bin/env python3
"""Generate reproducible fake users for testing. Standard library only."""
import argparse
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
TODAY = date(2026, 11, 17)
SIGNUP_START = date(2022, 1, 1)

FIRST_NAMES = ["James", "Mary", "Wei", "Priya", "Carlos", "Fatima", "Liam", "Olivia",
               "Noah", "Emma", "Yuki", "Ahmed", "Sofia", "Lucas", "Aisha", "Mateo",
               "Hannah", "Arjun", "Chloe", "Daniel"]
LAST_NAMES = ["Smith", "Johnson", "Chen", "Patel", "Garcia", "Khan", "Brown", "Müller",
              "Tanaka", "Silva", "Kim", "Nguyen", "Rossi", "Martin", "Okafor", "Lopez"]
DOMAINS = ["example.com", "example.org", "example.net"]  # RFC 2606 reserved
COUNTRIES = [("US", 45), ("GB", 12), ("CA", 10), ("DE", 9), ("IN", 9),
             ("BR", 6), ("JP", 5), ("AU", 4)]
PLANS = [("free", 60), ("pro", 30), ("enterprise", 10)]
STATUSES = [("active", 70), ("inactive", 25), ("banned", 5)]

FIELDS = ["id", "first_name", "last_name", "email", "phone", "date_of_birth",
          "signup_date", "country", "plan", "status", "monthly_spend"]


def weighted(rng, pairs):
    values, weights = zip(*pairs)
    return rng.choices(values, weights=weights, k=1)[0]


def rand_date(rng, start, end):
    return start + timedelta(days=rng.randint(0, (end - start).days))


def make_user(rng, uid):
    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    # Age skewed toward 25-45 (clamped normal)
    age = min(80, max(18, int(rng.gauss(36, 11))))
    dob = TODAY - timedelta(days=age * 365 + rng.randint(0, 364))
    adult_on = dob + timedelta(days=round(18 * 365.25) + 1)
    earliest_signup = max(SIGNUP_START, adult_on)
    signup = rand_date(rng, earliest_signup, TODAY)
    plan = weighted(rng, PLANS)
    if plan == "free":
        spend = 0.0
    elif plan == "pro":
        spend = round(math.exp(rng.gauss(math.log(29), 0.4)), 2)
    else:
        spend = round(math.exp(rng.gauss(math.log(400), 0.7)), 2)
    local = f"{first}.{last}".lower().replace("ü", "u")
    return {
        "id": uid,
        "first_name": first,
        "last_name": last,
        "email": f"{local}{uid}@{rng.choice(DOMAINS)}",
        "phone": "" if rng.random() < 0.10 else f"+1-555-01{rng.randint(0, 99):02d}",
        "date_of_birth": dob.isoformat(),
        "signup_date": signup.isoformat(),
        "country": weighted(rng, COUNTRIES),
        "plan": plan,
        "status": weighted(rng, STATUSES),
        "monthly_spend": f"{spend:.2f}",
    }


def inject_edge_cases(rng, users):
    """Mutate a few rows with edge cases. Never touches `id`."""
    if len(users) < 5:
        return []
    idx = rng.sample(range(len(users)), 4)
    # 1. Unicode names
    u = users[idx[0]]
    u.update(first_name="José", last_name="Ñúñez 李小龙 😀",
             email=f"jose.nunez{u['id']}@example.com")
    # 2. Null / empty values
    users[idx[1]].update(first_name="", email="", phone="")
    # 3. Boundary values: 255-char last name, max spend
    u = users[idx[2]]
    u.update(last_name=("L" * 255), plan="enterprise", monthly_spend="99999.99")
    # 4. Duplicate-looking record: same name as another row, distinct id/email
    dup = users[idx[3]]
    src = next(users[i] for i in range(len(users)) if i not in idx)
    dup.update(first_name=src["first_name"], last_name=src["last_name"],
               email=f"dup.{dup['id']}@example.org")
    return sorted(u_["id"] for u_ in (users[i] for i in idx))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=20)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--out", default="users.csv")
    a = p.parse_args()
    rng = random.Random(a.seed)
    users = [make_user(rng, i) for i in range(1, a.rows + 1)]
    edge_ids = inject_edge_cases(rng, users)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(users)
    print(f"Wrote {len(users)} rows to {out} (seed {a.seed}); edge-case ids: {edge_ids}")


if __name__ == "__main__":
    main()
