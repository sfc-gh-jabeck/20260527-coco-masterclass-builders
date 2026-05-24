SELECT
    SUPPLIER_ID,
    SUPPLIER_NAME,
    CONTACT_EMAIL,
    PHONE,
    CITY,
    STATE,
    COUNTRY,
    LEAD_TIME_DAYS
FROM {{ source('frostbyte_raw', 'SUPPLIERS') }}
