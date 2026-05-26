# Generate Synthetic Data

## Trigger
Use this skill when the user asks to generate synthetic data, sample data, test data, or mock data for the Frostbyte ski supply project.

## Overview
This skill generates realistic synthetic ski supply inventory data using the included Python script. The data covers stores, products, suppliers, stock levels, and purchase orders for a fictional Australian ski supply company called **Frostbyte**.

## How to Use

1. Ask the user the following questions before running the script:
   - **Number of stores** (default: 5)
   - **Number of products** (default: 50)
   - **Number of suppliers** (default: 10)
   - **Number of stock records** (default: 1000)
   - **Number of purchase orders** (default: 200)
   - **Output directory** (default: current working directory)

2. Run the Python script `generate_data.py` located in this skill's directory, passing the user's answers as command-line arguments:

```bash
python3 <path-to-skill>/generate_data.py \
  --stores 5 \
  --products 50 \
  --suppliers 10 \
  --stock-records 1000 \
  --purchase-orders 200 \
  --output-dir .
```

3. The script generates five CSV files:
   - `stores.csv` — Store locations and metadata
   - `products.csv` — Product catalog with categories and pricing
   - `suppliers.csv` — Supplier directory
   - `stock_levels.csv` — Current inventory positions per store/product
   - `purchase_orders.csv` — Inbound purchase orders from suppliers

4. After generation, offer to load the CSVs into Snowflake tables in the `FROSTBYTE_DB.RAW` schema following the naming convention skill.

## Loading into Snowflake
When loading data, use PUT + COPY INTO pattern:
1. Create a file format: `FROSTBYTE_CSV_FF` (CSV, skip header, field optionally enclosed by double quotes)
2. Create an internal stage: `FROSTBYTE_LOAD_STG`
3. PUT each CSV file to the stage
4. COPY INTO the corresponding RAW table from the stage
