-- Tableau SQL Query with Unsupported/Complex Functions
-- This file tests error handling and user alerting functionality
-- Expected: Multiple flagged items and user warnings

-- Test 1: MEDIAN function (requires WITHIN GROUP clause - manual review)
SELECT 
    department_id,
    MEDIAN(salary) AS median_salary,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;

-- Test 2: Custom User-Defined Function (unsupported)
SELECT 
    customer_id,
    CUSTOM_ENCRYPT(ssn) AS encrypted_ssn,
    MY_UDF_FUNCTION(data) AS processed_data
FROM customers;

-- Test 3: Complex CAST operations (flagged for manual review)
SELECT 
    STR(employee_id) AS emp_id_string,
    INT(salary_string) AS salary_integer,
    FLOAT(commission_rate) AS commission_float,
    DATE(hire_date_string) AS hire_date
FROM temp_employee_data;

-- Test 4: Unsupported window functions
SELECT 
    employee_id,
    salary,
    PERCENTILE(0.75) OVER (PARTITION BY department_id) AS percentile_75,
    NTILE(4) OVER (ORDER BY salary) AS salary_quartile
FROM employees;

-- Test 5: Complex nested functions
SELECT 
    order_id,
    IF(
        MEDIAN(
            IF(status = 'COMPLETE', 
               DATEDIFF('day', order_date, ship_date), 
               NULL)
        ) > 5,
        'SLOW',
        'FAST'
    ) AS shipping_speed
FROM orders;

-- Test 6: STARTSWITH and ENDSWITH (require special parameter handling)
SELECT 
    product_id,
    product_name
FROM products
WHERE STARTSWITH(product_name, 'Premium')
   OR ENDSWITH(product_code, 'XL');

-- Test 7: Complex CONTAINS with multiple parameters
SELECT 
    document_id,
    title
FROM documents
WHERE CONTAINS(content, 'keyword1', 'keyword2', 'keyword3');

-- Test 8: Tableau-specific calculation functions
SELECT 
    sales_id,
    WINDOW_AVG(sales_amount) AS moving_avg,
    RUNNING_SUM(quantity) AS cumulative_quantity,
    INDEX() AS row_index
FROM sales;

-- Test 9: Complex string manipulation
SELECT 
    customer_id,
    SPLIT(full_address, ',', 2) AS state,
    REGEXP_EXTRACT(email, '@(.+)$') AS email_domain,
    FINDNTH(description, 'error', 3) AS third_error_position
FROM customer_data;

-- Test 10: Tableau LOD expressions (Level of Detail)
SELECT 
    order_id,
    sales_amount,
    {FIXED [Region]: SUM([Sales])} AS region_total,
    {INCLUDE [Category]: AVG([Profit])} AS category_avg_profit
FROM orders;

-- Test 11: Tableau table calculations
SELECT 
    month,
    revenue,
    LOOKUP(revenue, -1) AS previous_month_revenue,
    PREVIOUS_VALUE(revenue) AS prev_value,
    FIRST() AS is_first_row,
    LAST() AS is_last_row
FROM monthly_revenue;

-- Test 12: Unbalanced parentheses (syntax error)
SELECT 
    customer_id,
    UPPER(customer_name AS name_upper,
    LOWER(email)) AS email_lower
FROM customers;

-- Test 13: Invalid function names
SELECT 
    order_id,
    NOTAREALFUNCTION(order_date) AS invalid_result,
    FAKEFUNC(amount) AS fake_calculation
FROM orders;

-- Test 14: Multiple complex issues in one statement
SELECT 
    a.customer_id,
    MEDIAN(a.purchase_amount) AS median_purchase,
    STR(b.total_orders) AS orders_string,
    CUSTOM_RANKING_FUNC(a.score) AS custom_rank,
    IF(
        WINDOW_AVG(a.amount) > MEDIAN(b.threshold),
        SPLIT(a.category, '|', 3),
        UNKNOWN_FUNCTION(a.data)
    ) AS complex_result
FROM 
    purchases a
    JOIN summary b ON a.customer_id = b.customer_id
WHERE 
    STARTSWITH(a.product_name, 'Pro')
    AND CONTAINS(a.description, 'premium', 'deluxe');

-- Test 15: TODAY() function (requires special handling but should work)
-- This should partially work but might need review
SELECT 
    order_id,
    order_date,
    TODAY() AS current_date,
    DATEDIFF('day', order_date, TODAY()) AS days_since_order
FROM orders;

