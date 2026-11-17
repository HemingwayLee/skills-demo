# Claude's reply (without skill)

> Prompt: "Generate 500 fake e-commerce orders with users and products. Save the files in this folder."

I generated 500 fake orders, along with the users and products they refer to, as four linked CSV files in this folder:

| File | Rows | Contents |
|---|---|---|
| `users.csv` | 150 | Name, email, phone, address, signup date |
| `products.csv` | 80 | SKU, name, category (7 kinds), price, cost, stock, rating |
| `orders.csv` | 500 | Order number, user, date, status, payment method, subtotal, discount, shipping, tax, total, shipped and delivered dates |
| `order_items.csv` | 988 | The line items in each order: product, quantity, unit price, line total |

I checked the output: every user and product ID in the orders and line items points to a real row, and each order's subtotal equals the sum of its line items.

- **Dates:** orders cover Nov 19, 2025 to Nov 16, 2026. Order IDs go up in date order, and no order is dated before its user signed up.
- **Status:** about 68% of orders are delivered; the rest are shipped, processing, pending, cancelled or returned. Orders from the last few days are never marked delivered, and shipped/delivered dates are only filled in where the status calls for them.
- **Realism:** some users order much more often than others (137 of the 150 placed at least one order), and some products sell much more than others.
- **Pricing:** about 20% of orders get a 10–20% discount, shipping is free on orders of $50 or more, and tax is 8%. Total revenue is about $118.8k.
- **Fake contact details:** emails use reserved test domains such as `example.com`, and phone numbers use the 555 prefix, so none of them belong to real people.

I also saved the script that made the files, `generate.py`. It only uses Python's standard library, and the same seed always gives the same data. To make a different amount, run for example `python3 generate.py --orders 2000 --users 400 --seed 7`.
