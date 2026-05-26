import argparse
import csv
import hashlib
import os
import random
from datetime import datetime, timedelta


def _hash_id(prefix, *parts):
    raw = "|".join(str(p) for p in parts)
    return prefix + hashlib.md5(raw.encode()).hexdigest()[:12].upper()

STORE_LOCATIONS = [
    ("Thredbo", "NSW", "AUS", "ALPINE"),
    ("Perisher", "NSW", "AUS", "ALPINE"),
    ("Charlotte Pass", "NSW", "AUS", "HIGHLANDS"),
    ("Mt Buller", "VIC", "AUS", "ALPINE"),
    ("Falls Creek", "VIC", "AUS", "ALPINE"),
    ("Mt Hotham", "VIC", "AUS", "ALPINE"),
    ("Dinner Plain", "VIC", "AUS", "ALPINE"),
    ("Mt Baw Baw", "VIC", "AUS", "SOUTHERN"),
    ("Ben Lomond", "TAS", "AUS", "SOUTHERN"),
    ("Cradle Mountain", "TAS", "AUS", "SOUTHERN"),
    ("Selwyn Snow Resort", "NSW", "AUS", "HIGHLANDS"),
    ("Corin Forest", "ACT", "AUS", "HIGHLANDS"),
]

CATEGORY_CODES = {
    "Skis & Boards": "SKI",
    "Boots & Bindings": "BOO",
    "Outerwear & Apparel": "APP",
    "Helmets & Goggles": "HEL",
    "Accessories": "ACC",
    "Tuning & Maintenance": "TUN",
}

PRODUCT_CATEGORIES = {
    "Skis & Boards": [
        "All-Mountain Ski 170cm", "Powder Ski 180cm", "Carving Ski 165cm",
        "Freestyle Ski 160cm", "Touring Ski 175cm", "Snowboard All-Mountain 155cm",
        "Snowboard Freestyle 150cm", "Snowboard Splitboard 160cm",
    ],
    "Boots & Bindings": [
        "Alpine Boot Flex 100", "Alpine Boot Flex 130", "Touring Boot Ultralight",
        "Snowboard Boot BOA System", "Alpine Binding Race", "Alpine Binding Touring",
        "Snowboard Binding Freestyle", "Snowboard Binding All-Mountain",
    ],
    "Outerwear & Apparel": [
        "Gore-Tex Jacket Pro", "Insulated Ski Jacket", "Shell Pant Waterproof",
        "Insulated Bib Pant", "Merino Base Layer Top", "Merino Base Layer Bottom",
        "Mid-Layer Fleece", "Down Vest Packable",
    ],
    "Helmets & Goggles": [
        "MIPS Helmet Adult", "MIPS Helmet Junior", "Goggle Magnetic Lens",
        "Goggle Low-Light Lens", "Visor Helmet Pro", "Goggle Spare Lens Pack",
        "Junior Goggle Set", "Helmet Audio Kit",
    ],
    "Accessories": [
        "Ski Pole Carbon 120cm", "Ski Pole Aluminium 125cm", "Heated Gloves",
        "Gore-Tex Mittens", "Neck Gaiter Merino", "Ski Socks 3-Pack",
        "Hand Warmers Box 40", "Boot Bag Padded",
    ],
    "Tuning & Maintenance": [
        "Edge Tuning Kit", "Wax Iron Digital", "Base Repair P-Tex Sticks",
        "All-Temp Wax 200g", "Cold Wax 200g", "Binding Test Gauge",
        "Ski Brake Retainers", "Deburring Stone Set",
    ],
}

SUPPLIER_NAMES = [
    "Alpine Edge Australia", "Southern Peaks Supply", "Snowline Distributors",
    "Blizzard Trade Co", "Glacier Point Wholesale", "Frost & Summit Imports",
    "Powder House Supply", "Ice Cap Equipment", "Avalanche Gear Co",
    "Mountain Fox Trading", "Snowgum Wholesale", "Coldfront Logistics",
    "Summit Direct Supply", "Basecamp Distribution", "White Peak Imports",
]

ORDER_STATUSES = ["PENDING", "SHIPPED", "DELIVERED", "CANCELLED"]


def _assign_tier(sqm):
    if sqm < 150:
        return "T4"
    if sqm < 400:
        return "T3"
    if sqm >= 800:
        return "T1"
    return "T2"


def generate_stores(n):
    rows = []
    for i in range(n):
        location, state, country, region = STORE_LOCATIONS[i % len(STORE_LOCATIONS)]
        sqm = random.randint(80, 1200)
        rows.append({
            "STORE_ID": _hash_id("S_", location, state, i),
            "STORE_NAME": f"Frostbyte {location}",
            "CITY": location,
            "STATE": state,
            "COUNTRY": country,
            "SALES_REGION": region,
            "STORE_TIER": _assign_tier(sqm),
            "OPENED_DATE": (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2000))).strftime("%Y-%m-%d"),
            "SQUARE_METRES": sqm,
            "IS_ACTIVE": random.choices([True, False], weights=[95, 5])[0],
        })
    return rows


def generate_suppliers(n):
    rows = []
    names = random.sample(SUPPLIER_NAMES, min(n, len(SUPPLIER_NAMES)))
    while len(names) < n:
        names.append(f"Supplier {len(names)+1}")
    for i, name in enumerate(names):
        loc = random.choice(STORE_LOCATIONS)
        rows.append({
            "SUPPLIER_ID": _hash_id("SUP_", name, i),
            "SUPPLIER_NAME": name,
            "CONTACT_EMAIL": name.lower().replace(" ", ".").replace("&", "and") + "@example.com",
            "PHONE": f"+61 4{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
            "CITY": loc[0],
            "STATE": loc[1],
            "COUNTRY": "AUS",
            "LEAD_TIME_DAYS": random.randint(2, 28),
        })
    return rows


def generate_products(n, suppliers):
    rows = []
    all_products = []
    for cat, items in PRODUCT_CATEGORIES.items():
        for item in items:
            all_products.append((cat, item))
    random.shuffle(all_products)
    for i in range(n):
        cat, name = all_products[i % len(all_products)]
        if i >= len(all_products):
            name = f"{name} V{i // len(all_products) + 1}"
        cost = round(random.uniform(15.0, 800.0), 2)
        margin = round(random.uniform(0.25, 0.65), 2)
        rows.append({
            "PRODUCT_ID": _hash_id("P_", cat, name, i),
            "PRODUCT_NAME": name,
            "CATEGORY": cat,
            "CATEGORY_CODE": CATEGORY_CODES[cat],
            "UNIT_COST": cost,
            "UNIT_PRICE": round(cost * (1 + margin), 2),
            "SUPPLIER_ID": random.choice(suppliers)["SUPPLIER_ID"],
            "WEIGHT_KG": round(random.uniform(0.1, 15.0), 2),
            "IS_ACTIVE": random.choices([True, False], weights=[90, 10])[0],
        })
    return rows


def generate_stock_levels(n, stores, products):
    rows = []
    for i in range(n):
        store = random.choice(stores)
        product = random.choice(products)
        qty = random.randint(0, 200)
        reorder = random.randint(5, 50)
        rows.append({
            "STOCK_LEVEL_ID": _hash_id("SL_", store["STORE_ID"], product["PRODUCT_ID"], i),
            "STORE_ID": store["STORE_ID"],
            "PRODUCT_ID": product["PRODUCT_ID"],
            "QUANTITY_ON_HAND": qty,
            "REORDER_POINT": reorder,
            "REORDER_QUANTITY": reorder * random.randint(2, 5),
            "LAST_COUNTED_DATE": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "IS_BELOW_REORDER": qty < reorder,
        })
    return rows


def generate_purchase_orders(n, stores, products, suppliers):
    rows = []
    for i in range(n):
        store = random.choice(stores)
        product = random.choice(products)
        supplier = next((s for s in suppliers if s["SUPPLIER_ID"] == product["SUPPLIER_ID"]), random.choice(suppliers))
        qty = random.randint(5, 100)
        order_date = datetime.now() - timedelta(days=random.randint(0, 180))
        status = random.choice(ORDER_STATUSES)
        delivered = None
        if status == "DELIVERED":
            delivered = (order_date + timedelta(days=random.randint(2, 35))).strftime("%Y-%m-%d")
        rows.append({
            "PO_ID": _hash_id("PO_", store["STORE_ID"], product["PRODUCT_ID"], order_date.isoformat(), i),
            "STORE_ID": store["STORE_ID"],
            "PRODUCT_ID": product["PRODUCT_ID"],
            "SUPPLIER_ID": supplier["SUPPLIER_ID"],
            "QUANTITY_ORDERED": qty,
            "UNIT_COST": product["UNIT_COST"],
            "TOTAL_COST": round(qty * product["UNIT_COST"], 2),
            "ORDER_DATE": order_date.strftime("%Y-%m-%d"),
            "EXPECTED_DELIVERY_DATE": (order_date + timedelta(days=supplier["LEAD_TIME_DAYS"])).strftime("%Y-%m-%d"),
            "ACTUAL_DELIVERY_DATE": delivered or "",
            "STATUS": status,
        })
    return rows


def write_csv(filepath, rows):
    if not rows:
        return
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {filepath} ({len(rows)} rows)")


def main():
    parser = argparse.ArgumentParser(description="Generate Frostbyte ski supply synthetic data")
    parser.add_argument("--stores", type=int, default=5)
    parser.add_argument("--products", type=int, default=50)
    parser.add_argument("--suppliers", type=int, default=10)
    parser.add_argument("--stock-records", type=int, default=1000)
    parser.add_argument("--purchase-orders", type=int, default=200)
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    print("Generating Frostbyte synthetic data...")
    stores = generate_stores(args.stores)
    suppliers = generate_suppliers(args.suppliers)
    products = generate_products(args.products, suppliers)
    stock_levels = generate_stock_levels(args.stock_records, stores, products)
    purchase_orders = generate_purchase_orders(args.purchase_orders, stores, products, suppliers)

    write_csv(os.path.join(args.output_dir, "stores.csv"), stores)
    write_csv(os.path.join(args.output_dir, "suppliers.csv"), suppliers)
    write_csv(os.path.join(args.output_dir, "products.csv"), products)
    write_csv(os.path.join(args.output_dir, "stock_levels.csv"), stock_levels)
    write_csv(os.path.join(args.output_dir, "purchase_orders.csv"), purchase_orders)
    print("Done!")


if __name__ == "__main__":
    main()
