-- Tableau SQL Query with Date Functions

SELECT 
    transaction_id,
    transaction_date,
    YEAR(transaction_date) AS trans_year,
    MONTH(transaction_date) AS trans_month,
    DAY(transaction_date) AS trans_day,
    DATEADD('day', 30, transaction_date) AS due_date,
    DATEDIFF('day', transaction_date, NOW()) AS days_since_transaction
FROM 
    transactions
WHERE 
    transaction_date >= MAKEDATE(2024, 1, 1);

