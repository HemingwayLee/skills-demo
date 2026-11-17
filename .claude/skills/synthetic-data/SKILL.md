---
name: synthetic-data
description: Generate realistic, reproducible synthetic/fake/test/mock data (CSV, JSON, SQL seed rows). Use whenever the user asks for sample data, dummy records, test fixtures, mock users/orders/transactions, or a dataset to try something out.
---

# Synthetic Data Generator

When asked to create synthetic data, do NOT type rows out by hand.
Always write a small, seeded generator script and run it. Follow these steps.

## 1. Pin down the schema first

Before writing code, write a short schema table in your reply:

| column | type | rule / range | nullable |
|--------|------|--------------|----------|

Infer sensible columns if the user didn't list them. Keep relationships
consistent (e.g. `order.user_id` must exist in `users.id`,
`end_date >= start_date`, `total = qty * unit_price`).

## 2. Write a reproducible generator

- Python 3, standard library only (`random`, `csv`, `json`, `datetime`, `uuid`) unless the user's project already uses Faker/pandas.
- Put it at `scripts/generate_<name>.py`.
- Fixed seed at the top: `SEED = 42`, and accept `--rows N` and `--seed S` CLI args.
- Write output to `data/<name>.csv` (or `.json` if asked).

## 3. Make the data realistic, not uniform

- Use skewed distributions where the real world is skewed (prices, order counts, session length → log-normal or weighted choices), not `randint` for everything.
- Dates: spread over a realistic window, respect weekdays/business hours when relevant.
- Categorical values: use weighted frequencies (e.g. 70% `active`, 25% `inactive`, 5% `banned`).

## 4. Inject edge cases on purpose (~5% of rows)

Include a few rows with each of the following, where the type allows:
- empty string and `null`
- min / max boundary values (0, negative, very large)
- unicode and long text (`"José Ñúñez"`, `"李小龙"`, emoji, 255-char strings)
- duplicate-looking but distinct records (same name, different id)

Never inject edge cases into primary keys or foreign keys — those stay valid.

## 5. Verify, then report

After running the script, check the output (row count, no broken foreign keys,
constraints hold) and finish with a short **data card**:

```
File:        data/users.csv
Rows:        1000   (seed 42)
Columns:     id, name, email, signup_date, plan, monthly_spend
Edge cases:  50 rows (nulls, unicode names, spend = 0 / 99999.99)
Regenerate:  python scripts/generate_users.py --rows 1000 --seed 42
```

Show the first 5 rows as a preview. Do not paste the whole dataset into chat.
