SELECT
    sl.STORE_ID,
    st.STORE_NAME,
    sl.PRODUCT_ID,
    p.PRODUCT_NAME,
    p.CATEGORY,
    p.CATEGORY_CODE,
    st.SALES_REGION,
    st.STORE_TIER,
    sup.SUPPLIER_NAME,
    sl.QUANTITY_ON_HAND,
    sl.REORDER_POINT,
    sl.IS_BELOW_REORDER,
    DATEDIFF('day', sl.LAST_COUNTED_DATE, CURRENT_DATE()) AS DAYS_SINCE_LAST_COUNT,
    sl.QUANTITY_ON_HAND * p.UNIT_COST AS STOCK_VALUE
FROM {{ ref('stg_stock_levels') }} sl
INNER JOIN {{ ref('stg_stores') }} st ON sl.STORE_ID = st.STORE_ID
INNER JOIN {{ ref('stg_products') }} p ON sl.PRODUCT_ID = p.PRODUCT_ID
INNER JOIN {{ ref('stg_suppliers') }} sup ON p.SUPPLIER_ID = sup.SUPPLIER_ID
