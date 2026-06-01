-- test fails if duplicate order_id + item_sequence combinations exist
SELECT
  order_id,
  item_sequence,
  COUNT(*) AS duplicate_count
FROM {{ ref('fact_orders') }}
GROUP BY order_id, item_sequence
HAVING COUNT(*) > 1