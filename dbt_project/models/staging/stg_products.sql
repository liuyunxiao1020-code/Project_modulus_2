SELECT
  product_id,
  product_category_name         AS category_portuguese,
  product_weight_g              AS weight_grams,
  product_length_cm             AS length_cm,
  product_height_cm             AS height_cm,
  product_width_cm              AS width_cm,
  product_photos_qty            AS photo_count
FROM {{ source('ecommerce_raw', 'raw_products') }}
WHERE product_id IS NOT NULL