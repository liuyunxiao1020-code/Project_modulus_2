SELECT
  seller_id,
  seller_zip_code_prefix  AS zip_code,
  LOWER(seller_city)      AS city,
  seller_state            AS state
FROM {{ source('ecommerce_raw', 'raw_sellers') }}
WHERE seller_id IS NOT NULL