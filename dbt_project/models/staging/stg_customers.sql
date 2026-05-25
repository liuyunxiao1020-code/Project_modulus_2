SELECT
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix  AS zip_code,
  LOWER(customer_city)      AS city,
  customer_state            AS state
FROM {{ source('ecommerce_raw', 'raw_customers') }}
WHERE customer_id IS NOT NULL