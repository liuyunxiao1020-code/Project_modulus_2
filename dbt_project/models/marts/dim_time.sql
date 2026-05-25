SELECT DISTINCT
  FORMAT_DATE('%Y%m%d', DATE(purchased_at))   AS time_key,
  DATE(purchased_at)                          AS full_date,
  EXTRACT(DAY     FROM purchased_at)          AS day,
  EXTRACT(MONTH   FROM purchased_at)          AS month,
  EXTRACT(YEAR    FROM purchased_at)          AS year,
  EXTRACT(QUARTER FROM purchased_at)          AS quarter,
  FORMAT_DATE('%A', DATE(purchased_at))       AS day_of_week,
  FORMAT_DATE('%B', DATE(purchased_at))       AS month_name
FROM {{ ref('stg_orders') }}
WHERE purchased_at IS NOT NULL