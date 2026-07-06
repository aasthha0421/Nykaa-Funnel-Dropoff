USE NykaaAnalytics;
GO

CREATE VIEW vw_cart_abandonment AS
SELECT
    category,
    SUM(CAST(reached_cart AS INT)) AS cart_adds,
    SUM(CAST(reached_checkout AS INT)) AS checkouts,
    ROUND(
        100.0 * (
            SUM(CAST(reached_cart AS INT))
            - SUM(CAST(reached_checkout AS INT))
        ) / SUM(CAST(reached_cart AS INT)),
        1
    ) AS cart_abandon_pct
FROM sessions
GROUP BY category;