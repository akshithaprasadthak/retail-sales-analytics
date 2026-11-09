SELECT COUNT(*) AS orders, SUM(gross_cents) AS gross_cents,
       SUM(refund_cents) AS refund_cents, SUM(gross_cents - refund_cents) AS net_cents,
       ROUND(100.0 * AVG(refund_cents > 0), 1) AS refunded_orders_pct
FROM records;
