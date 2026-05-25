SELECT
  order_id,
  payment_sequential        AS sequence,
  payment_type,
  payment_installments      AS installments,
  payment_value             AS amount
FROM {{ source('ecommerce_raw', 'raw_order_payments') }}
WHERE order_id IS NOT NULL