SELECT
  customer_id       AS customer_key,
  customer_unique_id,
  zip_code,
  INITCAP(city)     AS city,
  state
FROM {{ ref('stg_customers') }}