
SELECT
    device,
    COUNT(*) AS total_sessions,
    SUM(CAST(reached_order AS INT)) AS orders,
    ROUND(
        100.0 * SUM(CAST(reached_order AS INT)) / COUNT(*),
        2
    ) AS conversion_rate,
    ROUND(
        100.0 * SUM(CAST(reached_order AS INT))
        / SUM(SUM(CAST(reached_order AS INT))) OVER (),
        2
    ) AS pct_of_total_orders
FROM sessions
GROUP BY device
ORDER BY conversion_rate DESC;