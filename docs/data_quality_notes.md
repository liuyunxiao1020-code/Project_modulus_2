# Data Quality Notes

## Known Issues in Olist Dataset

### 1. Orders without items (778 rows)
- Some orders in raw_orders have no matching rows in raw_order_items
- These are likely cancelled or failed orders
- Resolution: filtered out using INNER JOIN in fact_orders

### 2. Duplicate reviews (661 rows)
- Some orders have multiple reviews in raw_order_reviews
- Resolution: kept only the most recent review per order using ROW_NUMBER()

## Test Results Summary
- Total tests run: 40
- Passed: 35 → 40 (after fixes)
- Failed: 5 → 0 (after fixes)
- These issues are documented as known data quality findings