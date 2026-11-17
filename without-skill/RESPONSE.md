# Claude's reply (without skill)

> Prompt: "Make me 20 fake users for testing. Save them as a CSV in this folder."

I saved 20 fake users to `fake_users.csv` in this folder.

**Columns:** `id`, `first_name`, `last_name`, `username`, `email`, `phone`, `date_of_birth`, `city`, `country`, `signup_date`, `is_active`

**Safety:**
- All emails use `example.com`, `example.org` or `example.net`. These domains are reserved for testing, so messages sent to them won't reach anyone.
- All phone numbers are in the `+1-555-01xx` range, which is reserved for fictional use.

**Useful for testing:**
- Names come from many countries, and one includes an apostrophe (`O'Connell`) to test quoting and escaping.
- Four users have `is_active` set to `false` (ids 4, 8, 13, 18).
- Dates are in ISO format (`YYYY-MM-DD`). Birth dates run from 1978 to 2000, and sign-up dates from January 2024 to January 2025.

I can add more rows, add fields like address, role, password hash or UUIDs, or put in deliberately bad data (missing fields, invalid emails, duplicates) to test validation.
