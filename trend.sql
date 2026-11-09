SELECT substr(day, 1, 7) AS month, COUNT(*) AS orders,
       SUM(gross_cents - refund_cents) AS net_cents
FROM records GROUP BY month ORDER BY month;
