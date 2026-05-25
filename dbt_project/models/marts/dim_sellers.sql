SELECT
  seller_id         AS seller_key,
  zip_code,
  INITCAP(city)     AS city,
  state,
  CASE
    WHEN state IN ('SP', 'RJ', 'MG', 'ES')         THEN 'Southeast'
    WHEN state IN ('PR', 'SC', 'RS')                THEN 'South'
    WHEN state IN ('BA', 'PE', 'CE', 'MA', 'PI',
                   'AL', 'SE', 'PB', 'RN')          THEN 'Northeast'
    WHEN state IN ('AM', 'PA', 'AC', 'RO', 'RR',
                   'AP', 'TO')                      THEN 'North'
    WHEN state IN ('GO', 'MT', 'MS', 'DF')          THEN 'Central-West'
    ELSE 'Unknown'
  END               AS region
FROM {{ ref('stg_sellers') }}