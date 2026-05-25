SELECT
  order_id,
  customer_id,
  order_status,
  TIMESTAMP(order_purchase_timestamp)       AS purchased_at,
  TIMESTAMP(order_delivered_customer_date)  AS delivered_at,
  TIMESTAMP(order_estimated_delivery_date)  AS estimated_delivery_at
FROM {{ source('ecommerce_raw', 'raw_orders') }}
WHERE order_id IS NOT NULL