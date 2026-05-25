SELECT
  ROW_NUMBER() OVER ()    AS payment_key,
  order_id,
  payment_type,
  installments,
  amount,
  sequence
FROM {{ ref('stg_order_payments') }}