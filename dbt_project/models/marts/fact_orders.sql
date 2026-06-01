-- models/marts/fact_orders.sql

WITH deduplicated_reviews AS (
  SELECT
    order_id,
    review_score,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY review_creation_date DESC
    ) AS rn
  FROM {{ source('ecommerce_raw', 'raw_order_reviews') }}
),

latest_reviews AS (
  SELECT
    order_id,
    review_score
  FROM deduplicated_reviews
  WHERE rn = 1
)

SELECT
  o.order_id,
  o.customer_id                                         AS customer_key,
  i.product_id                                          AS product_key,
  i.seller_id                                           AS seller_key,
  FORMAT_DATE('%Y%m%d', DATE(o.purchased_at))           AS time_key,
  o.order_status,
  o.purchased_at,
  o.delivered_at,
  i.price                                               AS item_price,
  i.freight_value,
  i.total_item_amount,
  i.order_item_id                                       AS item_sequence,
  r.review_score
FROM {{ ref('stg_orders') }}            o
INNER JOIN {{ ref('stg_order_items') }} i ON o.order_id = i.order_id
LEFT JOIN latest_reviews                r ON o.order_id = r.order_id
WHERE
  i.product_id    IS NOT NULL
  AND i.seller_id IS NOT NULL
  AND i.price     IS NOT NULL