SELECT
    'Homepage' AS stage, SUM(CAST(reached_homepage AS INT)) AS users
FROM sessions

UNION ALL

SELECT
    'Search', SUM(CAST(reached_search AS INT))
FROM sessions

UNION ALL

SELECT
    'Product View', SUM(CAST(reached_product AS INT))
FROM sessions

UNION ALL

SELECT
    'Add to Cart', SUM(CAST(reached_cart AS INT))
FROM sessions

UNION ALL

SELECT
    'Checkout', SUM(CAST(reached_checkout AS INT))
FROM sessions

UNION ALL

SELECT
    'Payment', SUM(CAST(reached_payment AS INT))
FROM sessions

UNION ALL

SELECT
    'Order Placed', SUM(CAST(reached_order AS INT))
FROM sessions;




