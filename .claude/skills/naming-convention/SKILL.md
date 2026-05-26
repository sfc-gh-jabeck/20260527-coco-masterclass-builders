# Frostbyte Naming Convention

## Trigger
This skill MUST be used whenever creating, renaming, or referencing Snowflake objects, dbt models, or data values within the Frostbyte project.

---

## Part 1: Snowflake Object Naming

### Prefix Rule
All Snowflake objects MUST use the prefix **FROSTBYTE**. This prefix identifies resources belonging to this project and ensures consistent naming across the account.

### Naming Patterns

| Object Type | Pattern | Example |
|---|---|---|
| Database | `FROSTBYTE_DB` | `FROSTBYTE_DB` |
| Schema | `<LAYER>` inside the FROSTBYTE database | `RAW`, `STAGING`, `MARTS` |
| Warehouse | `FROSTBYTE_<SIZE>_WH` | `FROSTBYTE_XS_WH` |
| Role | `FROSTBYTE_<FUNCTION>` | `FROSTBYTE_ADMIN`, `FROSTBYTE_ANALYST` |
| Table | `<ENTITY>` (uppercase, underscores) | `PRODUCTS`, `STORE_LOCATIONS` |
| View | `V_<ENTITY>` | `V_STOCK_SUMMARY` |
| Stage | `FROSTBYTE_<PURPOSE>_STG` | `FROSTBYTE_LOAD_STG` |
| File Format | `FROSTBYTE_<TYPE>_FF` | `FROSTBYTE_CSV_FF` |

### Snowflake General Rules
- All names MUST be uppercase with underscores as separators.
- No special characters, hyphens, or spaces.
- Abbreviations should be avoided unless they are industry standard (e.g., `WH`, `STG`, `FF`).
- Database layer schemas follow medallion architecture: `RAW` -> `STAGING` -> `MARTS`.

### Infrastructure Setup
When asked to create infrastructure for this project, create the following objects:

1. **Database**: `FROSTBYTE_DB`
2. **Schemas**: `RAW`, `STAGING`, `MARTS` (inside `FROSTBYTE_DB`)
3. **Warehouse**: `FROSTBYTE_XS_WH` (X-Small, auto-suspend 60s, auto-resume)
4. **Roles**: `FROSTBYTE_ADMIN` (owns all objects), `FROSTBYTE_ANALYST` (read on MARTS)

Grant the appropriate privileges so that `FROSTBYTE_ADMIN` can create and manage objects in all schemas, and `FROSTBYTE_ANALYST` has SELECT on the MARTS schema.

---

## Part 2: dbt Object Naming

### dbt Project
- **Project name**: `frostbyte`
- **Profile name**: Match the active Snowflake connection name

### dbt Models

| Layer | Prefix | Materialisation | Example |
|---|---|---|---|
| Staging | `stg_` | view | `stg_stores`, `stg_products` |
| Intermediate | `int_` | ephemeral | `int_stock_with_products` |
| Marts (fact) | `fct_` | table | `fct_inventory_health` |
| Marts (dimension) | `dim_` | table | `dim_stores` |

### dbt Sources
- Source name: `frostbyte_raw`
- Source schema: `RAW`
- Source database: `FROSTBYTE_DB`
- Table names in the source YAML must match the Snowflake table names exactly (uppercase).

### dbt File & Directory Layout
```
frostbyte/
├── dbt_project.yml
├── models/
│   ├── staging/
│   │   ├── _stg_sources.yml
│   │   ├── _stg_models.yml
│   │   ├── stg_stores.sql
│   │   ├── stg_products.sql
│   │   └── ...
│   └── marts/
│       ├── _marts_models.yml
│       ├── fct_inventory_health.sql
│       └── fct_procurement_summary.sql
└── tests/               (custom singular tests if needed)
```

### dbt General Rules
- All model file names are **lowercase with underscores**.
- Schema YAML files are prefixed with `_` and named by layer (e.g., `_stg_models.yml`, `_marts_models.yml`).
- Source definitions live alongside the staging models in `_stg_sources.yml`.
- Every model MUST have a description in its YAML file.
- Use `ref()` for model-to-model references, `source()` for raw table references.
- Column names inside SQL should be uppercase to match Snowflake defaults.

---

## Part 3: Standard Data Values & Abbreviations

The following standard codes and abbreviations MUST be used consistently across all raw data, transformations, and reporting.

### Country Codes

| Full Name | Standard Code |
|---|---|
| Australia | `AUS` |
| New Zealand | `NZL` |

### Australian State & Territory Codes

| State / Territory | Code |
|---|---|
| New South Wales | `NSW` |
| Victoria | `VIC` |
| Queensland | `QLD` |
| Western Australia | `WA` |
| South Australia | `SA` |
| Tasmania | `TAS` |
| Northern Territory | `NT` |
| Australian Capital Territory | `ACT` |

### Sales Regions
Each store belongs to a sales region based on geography. Use these standard region codes:

| Region Code | Region Name | States Covered |
|---|---|---|
| `ALPINE` | Alpine Region | VIC, NSW |
| `SOUTHERN` | Southern Region | TAS, VIC |
| `HIGHLANDS` | Highlands Region | NSW, ACT |

### Store Tiers
Stores are classified into tiers based on annual revenue and floor area:

| Tier Code | Tier Name | Criteria |
|---|---|---|
| `T1` | Flagship Resort Store | >= 800 sqm AND top 20% revenue |
| `T2` | Resort Standard | >= 400 sqm |
| `T3` | Village Store | < 400 sqm |
| `T4` | Pop-up / Seasonal | < 150 sqm (seasonal only) |

### Product Category Codes

| Full Category | Short Code |
|---|---|
| Skis & Boards | `SKI` |
| Boots & Bindings | `BOO` |
| Outerwear & Apparel | `APP` |
| Helmets & Goggles | `HEL` |
| Accessories | `ACC` |
| Tuning & Maintenance | `TUN` |

### Order Status Codes
These are the only valid purchase order statuses:

| Status | Description |
|---|---|
| `PENDING` | Order placed, not yet shipped |
| `SHIPPED` | In transit from supplier |
| `DELIVERED` | Received at store |
| `CANCELLED` | Order cancelled before delivery |
