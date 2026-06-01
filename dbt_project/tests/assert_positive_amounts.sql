-- test fails if any item price or freight value is negative
SELECT
  order_id,
  item_price,
  freight_value,
  total_item_amount
FROM {{ ref('fact_orders') }}
WHERE
  item_price < 0
  OR freight_value < 0
  OR total_item_amount < 0