-- Task 2.2: clinic-level appointment and no-show rates.
USE noshowguard;

-- Clinics with at least 95 appointments.
SELECT
  c.clinic_name,
  c.city,
  COUNT(*) AS appointments,
  SUM(a.no_show) AS no_shows,
  ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments AS a
JOIN clinics AS c
  ON a.clinic_id = c.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
HAVING COUNT(*) >= 95
ORDER BY no_show_pct DESC;

-- Repeat without HAVING to include all 8 clinics and identify the highest rate.
SELECT
  c.clinic_name,
  c.city,
  COUNT(*) AS appointments,
  SUM(a.no_show) AS no_shows,
  ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments AS a
JOIN clinics AS c
  ON a.clinic_id = c.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
ORDER BY no_show_pct DESC;
