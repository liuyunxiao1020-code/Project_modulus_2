SELECT
  order_id,
  order_item_id,
  product_id,
  seller_id,
  price,
  freight_value,
  price + freight_value   AS total_item_amount
FROM {{ source('ecommerce_raw', 'raw_order_items') }}
WHERE order_id IS NOT NULL