-- Tableau SQL Query with String Functions

SELECT 
    product_id,
    UPPER(product_name) AS product_upper,
    LOWER(product_name) AS product_lower,
    LEN(product_description) AS desc_length,
    SUBSTR(product_code, 1, 3) AS category_code,
    LEFT(product_name, 10) AS short_name,
    RIGHT(product_code, 4) AS item_code,
    TRIM(product_name) AS trimmed_name,
    REPLACE(product_name, 'Old', 'New') AS updated_name
FROM 
    products
WHERE 
    LEN(product_name) > 3;

