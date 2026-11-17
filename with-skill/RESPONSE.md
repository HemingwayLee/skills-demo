# Claude's reply (with skill)

> Prompt: "Make me 20 fake users for testing. Save them as a CSV in this folder."

I saved 20 fake users to `users.csv` in this folder. A small script makes them, so you can rebuild the same file any time. I ran it and checked the output: there are 20 rows, the IDs run 1–20, everyone was at least 18 at signup, no signup is later than today, and free-plan users all have $0 spend.

**Data card**
```
File:        users.csv
Rows:        20   (seed 42)
Columns:     id, first_name, last_name, email, phone, date_of_birth,
             signup_date, country, plan, status, monthly_spend
Edge cases:  4 rows (ids 5, 6, 14, 15): empty first_name/email/phone,
             unicode name "José Ñúñez 李小龙 😀", 255-char last_name,
             monthly_spend = 99999.99, and a duplicate name with a
             different id and email
Regenerate:  python3 scripts/generate_users.py --rows 20 --seed 42
```

**Preview (first 5 rows)**

| id | first_name | last_name | email | phone | dob | signup | country | plan | status | spend |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Priya | Smith | priya.smith1@example.net | +1-555-0111 | 1991-09-16 | 2026-02-17 | CA | free | active | 0.00 |
| 2 | Wei | Brown | wei.brown2@example.net | +1-555-0128 | 1999-07-28 | 2024-10-31 | US | pro | active | 16.10 |
| 3 | James | Khan | james.khan3@example.com | +1-555-0197 | 1996-12-02 | 2024-05-15 | US | free | active | 0.00 |
| 4 | Priya | Nguyen | priya.nguyen4@example.com | +1-555-0148 | 1982-11-06 | 2026-02-03 | US | free | active | 0.00 |
| 5 | *(empty)* | Nguyen | *(empty)* | *(empty)* | 2003-02-01 | 2023-01-29 | BR | pro | active | 38.21 |

- **Safe contact details:** emails use domains reserved for testing (`example.com`, `.org`, `.net`), and phone numbers are in the fictional 555-01xx range. None of them can reach a real person.
- **Edge-case rows:** 4 of the 20 rows (20%) are deliberately odd, which is more than the usual ~5%. With only 20 users, that's the only way to fit in one row of each type. If you want only clean rows, remove the `inject_edge_cases` call from the script.

The script is in `scripts/generate_users.py`, and `--rows` and `--seed` change how many users you get and which ones.
