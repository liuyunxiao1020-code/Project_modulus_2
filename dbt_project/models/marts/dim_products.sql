SELECT
  p.product_id                AS product_key,
  COALESCE(t.product_category_name_english,
           p.category_portuguese,
           'unknown')         AS category_english,
  p.category_portuguese,
  p.weight_grams,
  p.length_cm,
  p.height_cm,
  p.width_cm,
  p.photo_count
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ source('ecommerce_raw', 'raw_category_translation') }} t
  ON p.category_portuguese = t.product_category_name