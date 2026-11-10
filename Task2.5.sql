-- Task 2.5: rank clinics by no-show rate within each city.
USE noshowguard;

WITH clinic_rates AS (
  SELECT
    c.clinic_id,
    c.clinic_name,
    c.city,
    ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
  FROM appointments AS a
  JOIN clinics AS c
    ON a.clinic_id = c.clinic_id
  GROUP BY c.clinic_id, c.clinic_name, c.city
)
SELECT
  clinic_name,
  city,
  no_show_pct,
  RANK() OVER (
    PARTITION BY city
    ORDER BY no_show_pct DESC
  ) AS rank_in_city,
  CASE
    WHEN no_show_pct > (
      SELECT 100.0 * SUM(no_show) / COUNT(*)
      FROM appointments
    ) THEN 'above'
    WHEN no_show_pct < (
      SELECT 100.0 * SUM(no_show) / COUNT(*)
      FROM appointments
    ) THEN 'below'
    ELSE 'equal'
  END AS vs_overall
FROM clinic_rates
ORDER BY city, rank_in_city;
