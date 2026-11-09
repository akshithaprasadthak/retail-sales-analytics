SELECT category, COUNT(*) AS orders,
       SUM(gross_cents - refund_cents) AS net_cents,
       ROUND(100.0 * AVG(refund_cents > 0), 1) AS refunded_orders_pct
FROM records GROUP BY category ORDER BY net_cents DESC;
