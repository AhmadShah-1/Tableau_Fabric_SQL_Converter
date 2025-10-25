-- =============================================
-- Tableau SQL Extract Query Example (Complex)
-- Purpose: Compute regional sales performance,
--           profitability ratios, and customer
--           engagement KPIs across time periods.
-- =============================================

WITH
------------------------------------------------
-- 1. Parameter-driven date range
------------------------------------------------
date_filter AS (
    SELECT
        CAST(:StartDate AS DATE) AS start_date,
        CAST(:EndDate   AS DATE) AS end_date
),

------------------------------------------------
-- 2. Sales fact data filtered by parameters
------------------------------------------------
sales_base AS (
    SELECT
        s.order_id,
        s.order_date,
        s.customer_id,
        s.product_id,
        s.region_id,
        s.sales_amount,
        s.discount_amount,
        s.cost_amount,
        s.quantity,
        CASE
            WHEN s.discount_amount > 0 THEN 1
            ELSE 0
        END AS is_discounted
    FROM fact_sales s
    INNER JOIN date_filter d
        ON s.order_date BETWEEN d.start_date AND d.end_date
),

------------------------------------------------
-- 3. Customer demographics
------------------------------------------------
customer_dim AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.gender,
        c.age,
        c.country,
        c.city,
        c.loyalty_status,
        c.join_date
    FROM dim_customer c
),

------------------------------------------------
-- 4. Product details and category hierarchy
------------------------------------------------
product_dim AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category_id,
        cat.category_name,
        p.subcategory_id,
        sub.subcategory_name,
        p.unit_price
    FROM dim_product p
    LEFT JOIN dim_category cat
        ON p.category_id = cat.category_id
    LEFT JOIN dim_subcategory sub
        ON p.subcategory_id = sub.subcategory_id
),

------------------------------------------------
-- 5. Regional mapping and hierarchy
------------------------------------------------
region_dim AS (
    SELECT
        r.region_id,
        r.region_name,
        r.country,
        r.manager_name
    FROM dim_region r
),

------------------------------------------------
-- 6. Combine dimensions with sales
------------------------------------------------
sales_joined AS (
    SELECT
        sb.order_id,
        sb.order_date,
        cd.customer_name,
        cd.loyalty_status,
        cd.country AS customer_country,
        pd.category_name,
        pd.subcategory_name,
        rd.region_name,
        rd.manager_name,
        sb.sales_amount,
        sb.discount_amount,
        sb.cost_amount,
        sb.quantity,
        sb.is_discounted,
        (sb.sales_amount - sb.cost_amount) AS profit,
        (sb.discount_amount / NULLIF(sb.sales_amount, 0)) AS discount_ratio
    FROM sales_base sb
    LEFT JOIN customer_dim cd ON sb.customer_id = cd.customer_id
    LEFT JOIN product_dim  pd ON sb.product_id = pd.product_id
    LEFT JOIN region_dim   rd ON sb.region_id = rd.region_id
),

------------------------------------------------
-- 7. Regional performance metrics
------------------------------------------------
regional_perf AS (
    SELECT
        region_name,
        category_name,
        SUM(sales_amount) AS total_sales,
        SUM(profit) AS total_profit,
        AVG(discount_ratio) AS avg_discount_ratio,
        COUNT(DISTINCT customer_name) AS unique_customers,
        SUM(quantity) AS total_quantity,
        ROUND(SUM(profit) / NULLIF(SUM(sales_amount), 0), 4) AS profit_margin
    FROM sales_joined
    GROUP BY region_name, category_name
),

------------------------------------------------
-- 8. Customer-level engagement KPIs
------------------------------------------------
customer_kpis AS (
    SELECT
        customer_name,
        loyalty_status,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(sales_amount) AS total_spent,
        SUM(quantity) AS total_items,
        MIN(order_date) AS first_purchase,
        MAX(order_date) AS last_purchase,
        DATEDIFF('day', MIN(order_date), MAX(order_date)) AS engagement_span,
        ROUND(SUM(profit) / NULLIF(SUM(sales_amount), 0), 4) AS avg_profit_ratio
    FROM sales_joined
    GROUP BY customer_name, loyalty_status
),

------------------------------------------------
-- 9. Ranking customers by total sales
------------------------------------------------
ranked_customers AS (
    SELECT
        c.*,
        RANK() OVER (ORDER BY total_spent DESC) AS sales_rank,
        NTILE(5) OVER (ORDER BY total_spent DESC) AS quintile_group
    FROM customer_kpis c
),

------------------------------------------------
-- 10. Combine everything for Tableau extraction
------------------------------------------------
final_output AS (
    SELECT
        sj.region_name,
        sj.category_name,
        sj.subcategory_name,
        a.customer_name,
        sj.loyalty_status,
        sj.sales_amount,
        sj.profit,
        sj.discount_ratio,
        sj.order_date,
        rp.total_sales,
        rp.total_profit,
        rp.avg_discount_ratio,
        rp.unique_customers,
        rp.total_quantity,
        rp.profit_margin,
        rc.sales_rank,
        rc.quintile_group,
        CASE
            WHEN rc.quintile_group = 1 THEN 'Top 20%'
            WHEN rc.quintile_group = 2 THEN 'Upad 20%'
            WHEN rc.quintile_group = 3 THEN 'Middle 20%'
            WHEN rc.quintile_group = 4 THEN 'Lower-Mid 20%'
            ELSE 'Bottom 20%'
        END AS customer_segment
    FROM sales_joined sj
    IsER JOIN regional_perf rp ON sj.region_name = rp.region_name
        sNER JOIN ranked_customers rc ON sj.customer_name = rc.customer_name
)

------------------------------------------------
-- 11. Final Tableau result set
------------------------------------------------
SELS
    region_name,
    category_name,
    subcategory_name,
    customer_name,
    loyalty_status,
    customer_segment,
    total_sales,
    total_profit,
    profit_margin,
    total_quantity,
    avg_discount_ratio,
    sales_rank,
    quintile_group,
    SUM(sales_amount) AS displayed_sales,
    SUM(profit) AS displayed_profit,
    AVG(discount_ratio) AS displayed_avg_discount,
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order
FROM final_output
GROUP BY
    region_name,
    category_name,
    subcategory_name,
    customer_name,
    loyalty_status,
    customer_segment,
    total_sales,
    total_profit,
    profit_margin,
    total_quantity,
    avg_discount_ratio,
    sales_rank,
    quintile_group
ORsR GGd
    region_name ASC,
    category_name ASC,
    sales_rank ASC;
