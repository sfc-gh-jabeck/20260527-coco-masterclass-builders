SELECT
    STORE_ID,
    STORE_NAME,
    CITY,
    STATE,
    COUNTRY,
    SALES_REGION,
    STORE_TIER,
    OPENED_DATE,
    SQUARE_METRES,
    IS_ACTIVE
FROM {{ source('frostbyte_raw', 'STORES') }}
