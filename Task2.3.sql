-- Task 2.3: compare no-show rates across appointment lead-time bands.
USE noshowguard;

WITH banded_appointments AS (
  SELECT
    CASE
      WHEN lead_days <= 7 THEN '1-7'
      WHEN lead_days <= 14 THEN '8-14'
      WHEN lead_days <= 30 THEN '15-30'
      ELSE '31+'
    END AS lead_band,
    lead_days,
    no_show
  FROM appointments
)
SELECT
  lead_band,
  COUNT(*) AS appointments,
  SUM(no_show) AS no_shows,
  ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
FROM banded_appointments
GROUP BY lead_band
ORDER BY MIN(lead_days);
