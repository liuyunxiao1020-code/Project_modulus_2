-- test fails if any delivered_at is BEFORE purchased_at
SELECT
  order_id,
  purchased_at,
  delivered_at
FROM {{ ref('fact_orders') }}
WHERE
  delivered_at IS NOT NULL
  AND purchased_at IS NOT NULL
  AND delivered_at < purchased_at