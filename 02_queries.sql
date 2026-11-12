-- Part 2 queries for the noshowguard database.
-- First run Task2.1_setup.sql, then load_data.sql, then run these queries.

USE noshowguard;

-- Task 2.1: verify the loaded row counts.
SELECT COUNT(*) AS clinic_count FROM clinics;
SELECT COUNT(*) AS appointment_count FROM appointments;
SELECT SUM(no_show) AS no_show_count FROM appointments;

-- Expected: 8 clinics, 990 appointments, and 218 no-shows.

-- Duplicate primary-key test: run separately; it should fail because A0001 exists.
-- INSERT INTO appointments (
--   appointment_id, patient_id, clinic_id, booked_on, appt_date, age, gender,
--   distance_km, fee_inr, booking_channel, visit_type, reminder_sent,
--   prior_no_shows, status, lead_days, no_show
-- )
-- VALUES (
--   'A0001', 'P999', 'C01', '2025-01-01', '2025-01-02', 30, 'F',
--   5.0, 500, 'App', 'Consultation', 'Yes', 0, 'Attended', 1, 0
-- );
-- Recorded MySQL Workbench error:
-- Error Code: 1062. Duplicate entry 'A0001' for key 'appointments.PRIMARY'

-- Task 2.2: clinic rates for clinics with at least 95 appointments.
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

-- Task 2.2: include all clinics to identify the highest overall rate.
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

-- Task 2.3: compare no-show rates across appointment lead-time bands.
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

-- Task 2.4: monthly appointment and no-show-rate trend.
WITH monthly AS (
  SELECT
    SUBSTR(appt_date, 1, 7) AS month,
    COUNT(*) AS appointments,
    ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
  FROM appointments
  GROUP BY SUBSTR(appt_date, 1, 7)
)
SELECT
  month,
  appointments,
  no_show_pct,
  ROUND(no_show_pct - LAG(no_show_pct) OVER (ORDER BY month), 1) AS change_pp
FROM monthly
ORDER BY month;

-- Task 2.5: rank clinics by no-show rate within each city and compare with overall.
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
