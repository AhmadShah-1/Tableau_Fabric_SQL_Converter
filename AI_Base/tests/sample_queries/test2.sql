-- Tableau-style SQL (ANSI-like)

SELECT
    INT([order_id])                        AS order_id_int,
    SPLIT([customer_name], ' ', 1)         AS first_name,
    STR([sales_amount])                    AS sales_text
FROM orders
WHERE INT([order_id]) > 1000
ORDER BY order_id_int;

