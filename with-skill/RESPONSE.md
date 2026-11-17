# Claude's reply (with skill)

> Prompt: "Generate 500 fake e-commerce orders with users and products. Save the files in this folder."

I generated 500 fake orders, along with the users, products and order line items behind them, as four CSV files in a `data/` folder here. A separate check script found 0 errors: every order points to a real user, every line item to a real order and product, and all the money columns add up.

| File | Rows | What's in it |
|---|---|---|
| `data/orders.csv` | 500 | Order header: id, user_id, order_date, status, payment_method, shipping_country, item_count, subtotal, discount, shipping_fee, total, note |
| `data/order_items.csv` | 999 | One row per product in an order: id, order_id, product_id, quantity, unit_price, line_total |
| `data/users.csv` | 200 | id, first_name, last_name, email, phone, country, city, signup_date, status |
| `data/products.csv` | 80 | id, sku, name, category, unit_price, stock_qty, is_active |

**How the numbers fit together**
- Each line item's total is quantity × unit price.
- Each order's subtotal is the sum of its line items, and total = subtotal − discount + shipping.
- No order is dated before its user signed up, and no IDs repeat.
- 156 of the 200 users placed orders.

**To make it look like real shop data:**
- **Prices:** product prices vary by category and are skewed (many cheap items, a few expensive ones); 70% of them end in .99.
- **Buyers:** a few people buy a lot and most buy once or twice. The top buyer has 28 orders.
- **Orders:** 63% delivered, 16% shipped, 10% cancelled, 8% processing, 3% refunded. Most orders have one item and quantity 1, and evenings are the busiest hours.
- **Order totals:** median $69.02, ranging from $4.99 to $1,288.51.
- **Discounts and shipping:** 25% of orders get a 5–25% discount, and shipping is free over $50.

**Deliberate oddities (about 5% of rows, never in IDs)**
- Missing values: an empty cell means blank text, and the word `NULL` means no value.
- Accented and non-Latin names (José Ñúñez, 李小龙, Анна Иванова) and emoji in names and order notes.
- 255-character names and notes.
- Unusual products: one priced $0.00, one at $99,999.99, one with stock of −5 and one with 1,000,000.
- Records with the same name but different IDs.

**Preview (`orders.csv`)**
```
id,user_id,order_date,status,payment_method,shipping_country,item_count,subtotal,discount,shipping_fee,total,note
1,190,2025-01-21 17:09:06,cancelled,credit_card,US,1,14.99,0.00,4.99,19.98,NULL
2,161,2024-11-28 18:02:13,cancelled,credit_card,JP,3,507.00,0.00,0.00,507.00,Call on arrival
3,109,2026-07-08 20:08:07,shipped,credit_card,CA,1,169.90,33.98,0.00,135.92,NULL
4,28,2024-05-17 10:41:28,delivered,credit_card,CA,3,75.47,0.00,0.00,75.47,NULL
5,76,2025-07-30 10:17:28,delivered,gift_card,DE,4,214.59,21.46,0.00,193.13,NULL
```

The data comes from a script that uses a fixed seed, so it should give the same files every time, but I didn't run it twice to confirm. To regenerate and re-check:
```
python3 scripts/generate_ecommerce.py --rows 500 --seed 42
python3 scripts/validate_ecommerce.py
```
`--rows` sets the number of orders, and `--users` / `--products` change those counts. Files are in:
- `data/`
- `scripts/generate_ecommerce.py`
- `scripts/validate_ecommerce.py`
