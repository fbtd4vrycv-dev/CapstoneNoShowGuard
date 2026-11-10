-- Task 2.1: create the database and tables.
-- Run this once before loading data. The load_data.sql file contains the INSERTs.

CREATE DATABASE IF NOT EXISTS noshowguard;
USE noshowguard;

CREATE TABLE clinics (
  clinic_id VARCHAR(5) PRIMARY KEY,
  clinic_name VARCHAR(40) NOT NULL,
  city VARCHAR(20) NOT NULL,
  tier VARCHAR(10),
  latitude DECIMAL(8,4),
  longitude DECIMAL(8,4),
  temp_c DECIMAL(5,1)
);

CREATE TABLE appointments (
  appointment_id VARCHAR(8) PRIMARY KEY,
  patient_id VARCHAR(8) NOT NULL,
  clinic_id VARCHAR(5) NOT NULL,
  booked_on DATE,
  appt_date DATE,
  age INT,
  gender VARCHAR(1),
  distance_km DECIMAL(5,1),
  fee_inr INT,
  booking_channel VARCHAR(10),
  visit_type VARCHAR(12),
  reminder_sent VARCHAR(3),
  prior_no_shows INT,
  status VARCHAR(10),
  lead_days INT,
  no_show INT,
  FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);
