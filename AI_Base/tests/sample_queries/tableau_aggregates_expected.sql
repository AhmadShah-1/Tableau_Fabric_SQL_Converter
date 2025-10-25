-- Expected Fabric SQL Output for tableau_aggregates.sql

SELECT department_id,
       COUNT(*) AS employee_count,
       SUM(salary) AS total_salary,
       AVG(salary) AS avg_salary,
       MIN(salary) AS min_salary,
       MAX(salary) AS max_salary,
       STDEV(salary) AS salary_stdev
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5
ORDER BY total_salary DESC;

