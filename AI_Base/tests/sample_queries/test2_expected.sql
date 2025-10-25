-- Microsoft Fabric SQL (T-SQL)

SELECT
    CAST(order_id AS INT) AS order_id_int,
    SUBSTRING(customer_name, 1, CHARINDEX(' ', customer_name) - 1) AS first_name,
    CAST(sales_amount AS VARCHAR(20)) AS sales_text
FROM orders
WHERE CAST(order_id AS INT) > 1000
ORDER BY order_id_int;
