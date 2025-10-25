-- Expected Fabric SQL Output for tableau_simple.sql

SELECT customer_id,
       UPPER(customer_name) AS customer_name_upper,
       LEN(customer_email) AS email_length,
       YEAR(order_date) AS order_year,
       MONTH(order_date) AS order_month,
       order_amount
FROM customers
WHERE order_date >= DATEADD('year', -1, GETDATE())
  AND LEN(customer_email) > 5
ORDER BY order_date DESC;

