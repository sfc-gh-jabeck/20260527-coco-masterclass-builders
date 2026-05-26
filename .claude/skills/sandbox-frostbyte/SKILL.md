---
name: sandbox-frostbyte
description: "Interactive sandbox environment for teams to fast-prototype on Snowflake. Identifies user team, surfaces relevant datasets, spins up a sandbox database, then guides through prototyping tracks: pipelines, Streamlit apps, AI/ML experiments, analytics, or open exploration. Use when: sandboxs, experiment, fail fast, prototype, sandbox, snowcamp, sandbox database, spin up sandbox, quick prototype, try something."
---

# sandbox

Two-phase interactive skill: (1) provision a sandbox database from selected database schema based on team access, (2) guide through a prototyping track.

## Workflow

### Step 1: Team Identification

**Ask** user which team they belong to:

```
Which team are you in?

1. Supply Chain / Inventory Operations
2. Procurement / Vendor Management
3. Retail / Store Operations
```


**STOP**: Confirm team selection before proceeding.

### Step 2: Dataset Discovery

Based on team, present the tables from the mapping below. Show schema name, description, and approximate table count.

#### Team-to-Schema Access Mapping

## Data Access by Business Team

### Supply Chain / Inventory Operations
Primary consumer of fct_inventory_health. They'd monitor IS_BELOW_REORDER flags to trigger replenishment, track DAYS_SINCE_LAST_COUNT to schedule physical counts, and analyse STOCK_VALUE by store/region to optimise inventory allocation across the network.

| Schema | Table | Purpose |
|--------|-------|---------|
| MARTS | FCT_INVENTORY_HEALTH | Stock inventory details |


### Procurement / Vendor Management
Primary consumer of fct_procurement_summary. They'd evaluate supplier performance via ON_TIME_DELIVERY_RATE and AVG_DELIVERY_DELAY_DAYS, identify problematic suppliers with high CANCELLED_ORDER_COUNT, and negotiate based on TOTAL_SPEND per supplier-product combination.

| Schema | Table | Purpose |
|--------|-------|---------|
| MARTS | FCT_PROCUREMENT_SUMMARY | Supplier Performance |


### Retail / Store Operations
Cross-consumer of both tables (FCT_INVENTORY_HEALTH, FCT_PROCUREMENT_SUMMARY). Use inventory health data sliced by SALES_REGION and STORE_TIER to understand which stores are understocked, and procurement data to anticipate incoming stock. Useful for seasonal planning (pre-season build-up at flagship resort stores vs. pop-up locations).

| Schema | Table | Purpose |
|--------|-------|---------|
| MARTS | FCT_INVENTORY_HEALTH | Stock inventory details |
| MARTS | FCT_PROCUREMENT_SUMMARY | Supplier Performance |


**Actions:**
1. Present the team's available tables
2. Let user select/deselect schemas (all pre-selected by default)


**STOP**: Confirm final schema selection before proceeding.

### Step 3: sandbox Configuration

**Ask** user for:

1. **sandbox name** — suggest default: `sandbox_frostbyte_{TEAM}_{PURPOSE}` (e.g., `sandbox_frostbyte_procurement_poc`)
2. **Warehouse** — default: current warehouse or `FROSTBYTE_XS_WH`

**Present summary:**
```
sandbox Database: sandbox_frostbyte_procurement_poc
Schemas to clone: Schema(s) and number of tables
Warehouse: FROSTBYTE_XS_WH
```

**STOP**: MANDATORY approval before any DDL. Do NOT proceed without explicit confirmation.

### Step 4: Provision sandbox Database

**Pre-flight checks:**
```sql
SHOW DATABASES LIKE '<sandbox_name>';
```
If database exists, warn user and ask to pick a different name or confirm overwrite.

**Create database:**
```sql
CREATE DATABASE <sandbox_name> COMMENT = 'sandbox - {team} ';
```

**Clone each selected schema:**
```sql
CREATE SCHEMA <sandbox_name>.<schema_name> CLONE FROSTBYTE_DB.<schema_name>;
```

**Verify:**
```sql
SHOW SCHEMAS IN DATABASE <sandbox_name>;
```

Present summary: number of schemas created, total tables available.

**If any clone fails:**
- Report which schemas succeeded and which failed
- Ask user: continue with partial sandbox, retry failed schemas, or rollback (DROP DATABASE)

### Step 5: Choose Prototyping Track

Present tracks with team-specific recommendations:

```
Your sandbox database is ready! What would you like to do next?

A. Explore Sandbox     - Browse tables, sample data, profile columns
B. Prototype Pipeline  - Build a data pipeline (dbt / Dynamic Tables)
C. Prototype App       - Scaffold a Streamlit dashboard
D. AI/ML Experiments   - Try Cortex AI functions or train models
E. Analytics Prototype - Build semantic views / Cortex Analyst models
F. Document AI         - Extract structured data from PDFs using AI_EXTRACT
G. Open-ended sandboxes     - Freeform — tell me what you want to explore

Recommended for your team: {recommendation}
```


---

## Track A: Explore Sandbox

**Goal:** Familiarize with the sandbox data before building anything.

**Actions:**
1. List all schemas and tables in the sandbox database:
   ```sql
   SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT FROM <sandbox_name>.INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA != 'INFORMATION_SCHEMA' ORDER BY TABLE_SCHEMA, TABLE_NAME;
   ```
2. For tables user is interested in, show sample rows:
   ```sql
   SELECT * FROM <sandbox_name>.<schema>.<table> LIMIT 5;
   ```
3. Offer profiling: row counts, null rates, distinct value counts, min/max for numeric columns
4. Suggest which prototyping track to try next based on what they discovered

**Exit:** Offer to switch to any other track (B-F).

---

## Track B: Prototype Pipeline

**Goal:** Scaffold a data transformation pipeline in the sandbox database.

**Actions:**
1. **Ask** user: What transformation do you want to build? (e.g., "raw bookings -> daily revenue summary")
2. **Ask** approach preference:
   - **dbt project** — SQL-based transformations with testing and documentation
   - **Dynamic Tables** — Snowflake-native incremental pipelines
   - **Stored Procedures** — Procedural SQL logic
3. Based on choice:
   - **dbt**: Create a new dbt project targeting the sandbox database. Define staging models over cloned schemas, create mart/transform models. Use `dbt run` to materialize.
   - **Dynamic Tables**: Write CREATE DYNAMIC TABLE statements with appropriate TARGET_LAG. Source from sandbox schemas.
   - **Stored Procedures**: Write CREATE PROCEDURE with transformation logic.
4. **STOP**: Present generated code for approval before executing.
5. Execute and verify results.

**Suggested pipelines by team:**
- Customer: Booking funnel analysis, customer journey aggregation
- Commercial: Revenue by route/date, pricing elasticity views
- Corporate: OTP calculation, fleet utilization metrics, disruption impact
- Operations: Flight schedule analysis, disruption response pipelines, crew utilization

---

## Track C: Prototype App

**Goal:** Scaffold a Streamlit app connected to sandbox data and deploy to Snowflake on SPCS.

**CRITICAL: ALWAYS deploy Streamlit apps to Snowflake on SPCS container runtime. Never run locally.**

### Step C1: Gather Requirements

**Ask** user what they want to visualize. Suggest based on team:
- **Customer**: Customer journey funnel, NPS trends, booking volume dashboard
- **Commercial**: Pricing analysis, revenue by route, ancillary revenue breakdown
- **Corporate**: On-time performance, fleet utilization, sustainability metrics
- **Operations**: Flight ops dashboard (OCC Mission Watch style), disruption tracker, baggage performance
- **CoE**: Data quality dashboard, schema explorer, model performance monitor

If the user provides a reference image/screenshot, match the layout, color scheme, and component types as closely as possible.

### Step C2: Explore Data

Before writing any app code, **always query the sandbox data** to understand what's avaisandboxle:
```sql
SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT 
FROM <sandbox_name>.INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA != 'INFORMATION_SCHEMA' 
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

Then sample key tables (LIMIT 5) to understand columns, data types, and value ranges. This avoids writing queries against non-existent columns.

### Step C3: Check Infrastructure

Before deployment, verify avaisandboxle compute pools and external access integrations:
```sql
SHOW COMPUTE POOLS;
SHOW EXTERNAL ACCESS INTEGRATIONS;
```

**Required resources:**
- **Compute pool**: Look for an existing pool owned by SYSADMIN (e.g., `JOCC_COMPUTE_POOL`). If none exists, create one:
  ```sql
  CREATE COMPUTE POOL <pool_name> MIN_NODES = 1 MAX_NODES = 3 INSTANCE_FAMILY = CPU_X64_XS AUTO_SUSPEND_SECS = 900 AUTO_RESUME = TRUE;
  ```
- **External access integration**: Need `PYPI_ACCESS_INTEGRATION` for pip installs in SPCS runtime.

Also check Snow CLI version (must be >= 3.14.0):
```bash
snow --version
```

### Step C4: Create Project Structure

Create this file structure in the working directory:

```
<app_directory>/
  .streamlit/
    config.toml          # Dark theme config
  streamlit_app.py       # Main entry point (MUST be this filename)
  pyproject.toml         # Python dependencies
  snowflake.yml          # SPCS deployment manifest
```

#### `.streamlit/config.toml` — Dark theme (default for ops dashboards):
```toml
[theme]
base = "dark"
primaryColor = "#29B5E8"
backgroundColor = "#0a0e14"
secondaryBackgroundColor = "#151b23"
textColor = "#e0e0e0"
```

#### `pyproject.toml` — Always include snowflake-connector-python explicitly:
```toml
[project]
name = "<app-name>"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "snowflake-connector-python>=3.3.0",
    "streamlit[snowflake]>=1.54.0",
    "pandas>=2.0.0",
]
```

#### `snowflake.yml` — SPCS container runtime deployment:
```yaml
definition_version: 2
entities:
  <entity_name>:
    type: streamlit
    identifier:
      name: <APP_NAME>
      database: <sandbox_DATABASE>
      schema: <PRIMARY_SCHEMA>
    query_warehouse: ADMIN_WH
    runtime_name: SYSTEM$ST_CONTAINER_RUNTIME_PY3_11
    compute_pool: <COMPUTE_POOL_NAME>
    external_access_integrations:
      - PYPI_ACCESS_INTEGRATION
    main_file: streamlit_app.py
    artifacts:
      - streamlit_app.py
      - pyproject.toml
      - .streamlit/config.toml
```

### Step C5: Write the Streamlit App

**Connection pattern for SiS (MANDATORY — never use snowflake.connector directly):**
```python
import streamlit as st

conn = st.connection("snowflake")

@st.cache_data(ttl=300)
def run_query(sql):
    return conn.query(sql)
```

**App code conventions:**
- Use `st.set_page_config(layout="wide")` for dashboards
- Use `st.html()` for custom HTML/CSS rendering (donut charts, Gantt bars, grids)
- Use `st.columns()` for layout — match reference image proportions
- Use `@st.cache_data(ttl=300)` for all SQL queries (5-min cache)
- Use fully-qualified table names: `<sandbox_DB>.<SCHEMA>.<TABLE>`
- Use `st.html(CSS)` for custom styling — JetBrains Mono font for ops dashboards
- Generate SVG donuts/charts in Python, render via `st.html()`
- For complex UI (Gantt charts, grid matrices), build HTML strings in Python

**STOP**: Present app code for review before proceeding to deploy.

### Step C6: Deploy to Snowflake SPCS

```bash
cd <app_directory>
snow streamlit deploy --replace -c <CONNECTION_NAME>
```

The `--replace` flag updates an existing app. The CLI will output the Snowsight URL.

**Post-deploy verification:**
- Confirm the URL is accessible
- Present the URL to the user

**If deployment fails:**
- Check compute pool is ACTIVE (not SUSPENDED): `SHOW COMPUTE POOLS;`
- Check `snowflake.yml` has `compute_pool` field (required for SPCS runtime)
- Verify all files listed in `artifacts` exist
- Ensure external access integration exists and is enabled

---

## Track D: AI/ML Experiments

**Goal:** Run AI/ML experiments using Cortex AI functions or Snowpark ML on sandbox data.

**Actions:**
1. **Present** avaisandboxle experiment types:
   - **Cortex AI Functions**: COMPLETE, CLASSIFY, EXTRACT, SENTIMENT, SUMMARIZE, EMBED
   - **Snowpark ML**: Model training, feature engineering, model registry
2. **Suggest** experiments based on team data:
   - **Customer**: Sentiment on NPS surveys, customer segmentation via embeddings, churn prediction
   - **Commercial**: Demand forecasting, price sensitivity modeling, ancillary propensity
   - **Corporate**: Predictive maintenance from sensor data, disruption pattern detection, fuel optimization
   - **Operations**: Disruption prediction, crew scheduling optimization, baggage mishandling patterns
   - **CoE**: Any of the above + custom model training workflows
3. **Generate** starter SQL or Python:
   - Cortex AI: `SELECT SNOWFLAKE.CORTEX.SENTIMENT(review_text) FROM <sandbox_table>;`
   - ML: Snowpark ML training notebook scaffold
4. **STOP**: Approve before running expensive operations (large table scans, model training).
5. Execute and present results.

---

## Track E: Analytics Prototyping

**Goal:** Build a semantic layer or analytics model over sandbox data.

**Actions:**
1. **Ask** what business questions users want to answer with natural language
2. **Suggest** semantic view scope based on team:
   - **Supply Chain**: Stock reorder alerts, inventory distribution by region/tier, stock valuation
   - **Procurement**: Supplier performance, delivery delays, spend analysis
   - **Retail**: Cross-domain combining inventory and procurement for seasonal planning
3. **Build** a semantic model YAML file (see format below)
4. **STOP**: Review semantic model before deploying.
5. Deploy to a stage and test with natural language queries via Cortex Analyst.

### Semantic Model Deployment Method

**Use `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML` to create a native Semantic View object.**

This creates a first-class schema object visible in Snowsight under Semantic Views.

**Correct syntax:**
```sql
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  '<DATABASE>.<SCHEMA>',    -- target schema ONLY (view name comes from YAML name: field)
  $$ <yaml_content> $$,     -- YAML as dollar-quoted string
  FALSE                     -- FALSE = create, TRUE = verify only
);
```

**Common mistakes that will FAIL:**
- `CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML('DB.SCHEMA.VIEW_NAME', ...)` — first arg must be `DB.SCHEMA` only, NOT the view name
- `SELECT SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(...)` — must use CALL, not SELECT
- `CREATE SEMANTIC VIEW ... AS '...'` — wrong DDL syntax
- `CREATE OR REPLACE SEMANTIC VIEW ... YAML = $$...$$` — not valid syntax
- `CREATE SEMANTIC VIEW ... DIMENSIONS(...) METRICS(...)` — DDL has undocumented separator requirements

**Step-by-step deployment:**
1. Write a YAML file locally
2. Validate with `cortex reflect <path-to-yaml> --target-schema <DB.SCHEMA>`
3. Deploy with the CALL statement above (paste YAML content between `$$` markers)
4. Verify: `SHOW SEMANTIC VIEWS IN SCHEMA <sandbox_name>.MARTS;`
5. Test: `cortex analyst query "<question>" --view <DATABASE>.<SCHEMA>.<VIEW_NAME>`

**Fallback (stage-based approach):** If `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML` is unavailable:
1. Create a stage: `CREATE OR REPLACE STAGE <sandbox_name>.MARTS.SEMANTIC_MODELS;`
2. Upload: `PUT file:///<local_path>/model.yaml @<sandbox_name>.MARTS.SEMANTIC_MODELS AUTO_COMPRESS=FALSE;`
3. Query: `cortex analyst query "<question>" --model @<sandbox_name>.MARTS.SEMANTIC_MODELS/model.yaml`

### Semantic Model YAML Format

```yaml
name: <model_name>
description: >
  Description of what this semantic model covers and what questions it answers.

tables:
  - name: <logical_table_name>
    description: >
      Description of the table and its grain.
    base_table:
      database: <SANDBOX_DATABASE>
      schema: <SCHEMA>
      table: <PHYSICAL_TABLE_NAME>

    dimensions:
      - name: <dimension_name>
        expr: <COLUMN_NAME>
        data_type: VARCHAR | BOOLEAN | DATE | NUMBER
        description: <what this dimension represents>

    measures:
      - name: <measure_name>
        expr: <COLUMN_NAME or SQL expression>
        default_aggregation: sum | avg | count | count_distinct | min | max
        data_type: NUMBER
        description: <what this measure calculates>
```

**Key rules for the YAML:**
- `expr` must reference actual column names in the physical table (UPPERCASE to match Snowflake defaults)
- `data_type` must be one of: VARCHAR, BOOLEAN, DATE, NUMBER
- `default_aggregation` for measures: sum, avg, count, count_distinct, min, max
- For derived measures use SQL expressions in `expr`, e.g.: `"CASE WHEN COL = TRUE THEN 1 ELSE 0 END"`
- Wrap SQL expressions containing special characters in double quotes
- Avoid special characters (`&`, `/`) in description fields — use plain text equivalents

### Testing with Cortex Analyst

```bash
cortex analyst query "<natural language question>" --model @<sandbox_name>.MARTS.SEMANTIC_MODELS/model.yaml
```

The response includes generated SQL. Execute the SQL to verify results are correct.

**Test at least 2 questions** covering different dimensions/measures before confirming success.

---

## Track F: Document AI

**Goal:** Extract structured data from unstructured PDF documents using Cortex AI_EXTRACT, materialize into a dimension table that joins to existing MARTS tables.

### Step F1: Get PDF Location

**Ask** user for the local filesystem path containing supplier contract PDFs:

```
Provide the path to the directory containing your supplier contract PDFs:
(e.g., /Users/username/documents/supplier_contracts)
```

Validate the directory exists and contains `.pdf` files. Report the number of PDFs found.

### Step F2: Create Stage & Upload

**Create a named stage** in the sandbox database:
```sql
CREATE OR REPLACE STAGE <sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  DIRECTORY = (ENABLE = TRUE);
```

**Upload PDFs** using Snow CLI:
```bash
snow stage copy <pdf_directory>/ @<sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE --connection <connection> --overwrite
```

**Refresh directory:**
```sql
ALTER STAGE <sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE REFRESH;
```

**Verify upload:**
```sql
SELECT * FROM DIRECTORY(@<sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE);
```

Report number of files uploaded successfully.

### Step F3: Extract Structured Data with AI_EXTRACT

**Create the DIM_SUPPLIER_CONTRACTS table** by running AI_EXTRACT directly on each PDF file:

```sql
CREATE OR REPLACE TRANSIENT TABLE <sandbox_name>.MARTS.DIM_SUPPLIER_CONTRACTS AS
WITH extracted AS (
    SELECT
        RELATIVE_PATH AS file_name,
        AI_EXTRACT(
            file => TO_FILE('@<sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE', RELATIVE_PATH),
            responseFormat => {
                'supplier_name': 'The name of the supplier company',
                'supplier_id': 'The supplier ID code starting with SUP_',
                'contract_reference': 'The contract reference number starting with CTR-',
                'payment_terms': 'The payment terms such as Net 30 or Net 45',
                'lead_time_days': 'Maximum lead time in calendar days as a number only',
                'on_time_delivery_sla_pct': 'On-time delivery target percentage as a number only',
                'max_defect_rate_pct': 'Maximum defect rate percentage as a number only',
                'volume_discount_pct': 'Volume discount percentage as a number only',
                'volume_discount_threshold_units': 'Minimum units to qualify for volume discount as a number only',
                'minimum_order_qty': 'Minimum order quantity in units as a number only',
                'penalty_clause': 'The full penalty description for SLA non-compliance',
                'product_categories': 'Comma-separated list of product categories the supplier provides'
            }
        ) AS extracted_data
    FROM DIRECTORY(@<sandbox_name>.MARTS.SUPPLIER_CONTRACTS_STAGE)
)
SELECT
    extracted_data:"response":"supplier_id"::VARCHAR AS SUPPLIER_ID,
    extracted_data:"response":"supplier_name"::VARCHAR AS SUPPLIER_NAME,
    extracted_data:"response":"contract_reference"::VARCHAR AS CONTRACT_REFERENCE,
    extracted_data:"response":"payment_terms"::VARCHAR AS PAYMENT_TERMS,
    TRY_CAST(extracted_data:"response":"lead_time_days"::VARCHAR AS NUMBER) AS LEAD_TIME_DAYS,
    TRY_CAST(extracted_data:"response":"on_time_delivery_sla_pct"::VARCHAR AS NUMBER(5,2)) AS ON_TIME_DELIVERY_SLA_PCT,
    TRY_CAST(extracted_data:"response":"max_defect_rate_pct"::VARCHAR AS NUMBER(5,2)) AS MAX_DEFECT_RATE_PCT,
    TRY_CAST(extracted_data:"response":"volume_discount_pct"::VARCHAR AS NUMBER(5,2)) AS VOLUME_DISCOUNT_PCT,
    TRY_CAST(extracted_data:"response":"volume_discount_threshold_units"::VARCHAR AS NUMBER) AS VOLUME_DISCOUNT_THRESHOLD_UNITS,
    TRY_CAST(extracted_data:"response":"minimum_order_qty"::VARCHAR AS NUMBER) AS MINIMUM_ORDER_QTY,
    extracted_data:"response":"penalty_clause"::VARCHAR AS PENALTY_CLAUSE,
    extracted_data:"response":"product_categories"::VARCHAR AS PRODUCT_CATEGORIES,
    file_name AS SOURCE_FILE
FROM extracted;
```

**Key notes about AI_EXTRACT:**
- Uses `file => TO_FILE(...)` syntax (named parameter) to process PDFs directly
- The `responseFormat` is a JSON object where keys = output field names, values = extraction prompts
- Response is nested under `extracted_data:"response":"field_name"` path
- Use `TRY_CAST` for numeric fields to handle extraction edge cases gracefully

### Step F4: Verify & Present Results

**Show extracted results:**
```sql
SELECT * FROM <sandbox_name>.MARTS.DIM_SUPPLIER_CONTRACTS ORDER BY SUPPLIER_NAME;
```

Present a summary: number of PDFs processed, number of rows created, any NULL fields that may need attention.

**Show join capability** — contract SLA vs actual procurement performance:
```sql
SELECT
    c.SUPPLIER_NAME,
    c.ON_TIME_DELIVERY_SLA_PCT AS CONTRACTED_SLA,
    ROUND(AVG(p.ON_TIME_DELIVERY_RATE), 2) AS ACTUAL_ON_TIME_PCT,
    CASE
        WHEN AVG(p.ON_TIME_DELIVERY_RATE) < c.ON_TIME_DELIVERY_SLA_PCT THEN 'BREACH'
        ELSE 'COMPLIANT'
    END AS SLA_STATUS
FROM <sandbox_name>.MARTS.DIM_SUPPLIER_CONTRACTS c
JOIN <sandbox_name>.MARTS.FCT_PROCUREMENT_SUMMARY p
    ON c.SUPPLIER_ID = p.SUPPLIER_ID
WHERE p.ON_TIME_DELIVERY_RATE IS NOT NULL
GROUP BY c.SUPPLIER_NAME, c.ON_TIME_DELIVERY_SLA_PCT
ORDER BY ACTUAL_ON_TIME_PCT ASC;
```

### Step F5: Next Track

**Ask** user:
```
Document AI extraction complete! Your DIM_SUPPLIER_CONTRACTS table is ready and joins to existing MARTS tables.

What would you like to do next?

A. Explore Sandbox     - Browse the new table alongside existing data
B. Prototype Pipeline  - Build a transformation pipeline
C. Prototype App       - Build a Streamlit dashboard over the combined data
D. AI/ML Experiments   - Run more Cortex AI experiments
E. Analytics Prototype - Build a semantic view covering all 3 tables
G. Open-ended          - Freeform exploration
```

**Recommended next step:** Track E (Analytics Prototyping) — build a semantic view over all three MARTS tables (FCT_INVENTORY_HEALTH, FCT_PROCUREMENT_SUMMARY, DIM_SUPPLIER_CONTRACTS) to enable natural language queries like "Which suppliers are breaching their delivery SLA?" or "Show me stores with low stock from underperforming suppliers."

---

## Track G: Open-ended sandboxes

**Goal:** Freeform exploration — user describes what they want to build or investigate.

**Actions:**
1. **Ask** user: "What do you want to explore or build?"
2. Based on response, route to the most appropriate track (A-F) or handle ad-hoc
3. Support combining tracks: "Build a pipeline (Track B) then visualize it (Track C)"
4. Allow switching between tracks at any time
5. If request doesn't fit any track, work with user to prototype directly using SQL and available tools

---

## Stopping Points Summary

- **Step 1**: After team identification (confirm team)
- **Step 2**: After dataset discovery (confirm schema selection)
- **Step 3**: After sandbox configuration (MANDATORY — approve before DDL)
- **Step 4**: After provisioning if errors occur
- **Track B**: Before executing pipeline code
- **Track C**: Before deploying Streamlit app
- **Track D**: Before running expensive AI/ML operations
- **Track E**: Before deploying semantic model
- **Track F**: Before running AI_EXTRACT (confirm PDF directory and stage name)

**Resume rule:** On user approval, proceed directly to next step without re-asking.

## Error Handling

| Error | Action |
|-------|--------|
| Database name conflict | Warn, suggest alternative name or confirm overwrite |
| Permission denied on CREATE | Report error, suggest user check role/grants |
| Schema clone fails | Report partial success, offer continue/retry/rollback |
| Large table warning | Warn if cloning schemas with 50M+ row tables, suggest subset |
| Warehouse suspended | Attempt RESUME, or ask user to specify active warehouse |

## Cleanup

When user is done experimenting, offer:
```sql
DROP DATABASE <sandbox_name>;
```
**STOP**: Confirm before dropping.

## Output

- New sandbox database with cloned schemas from FROSTBYTE_DB
- Prototyping artifacts based on chosen track (pipeline code, Streamlit app, ML experiments, semantic views)
- Summary of what was built and suggested next steps
