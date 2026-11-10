-- Task 2.1: run these checks after executing load_data.sql.
USE noshowguard;

SELECT COUNT(*) AS clinic_count FROM clinics;
SELECT COUNT(*) AS appointment_count FROM appointments;
SELECT SUM(no_show) AS no_show_count FROM appointments;

-- Expected results: 8 clinics, 990 appointments, and 218 no-shows.

-- Duplicate primary-key test: run this statement separately to confirm that
-- appointment_id is unique. It is commented out so it does not interrupt the
-- verification queries when this file is executed as a whole.
-- INSERT INTO appointments (
--   appointment_id, patient_id, clinic_id, booked_on, appt_date, age, gender,
--   distance_km, fee_inr, booking_channel, visit_type, reminder_sent,
--   prior_no_shows, status, lead_days, no_show
-- )
-- VALUES (
--   'A0001', 'P999', 'C01', '2025-01-01', '2025-01-02', 30, 'F',
--   5.0, 500, 'App', 'Consultation', 'Yes', 0, 'Attended', 1, 0
-- );

-- Recorded MySQL Workbench result:
-- Error Code: 1062. Duplicate entry 'A0001' for key 'appointments.PRIMARY'
