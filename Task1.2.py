import pandas as pd

# Start fresh from the original file, as Task 1.2 requires.
df = pd.read_csv("data/appointments.csv")

# Inspect the raw data before making changes.
print("Raw shape:", df.shape)
df.info()
print("\nMissing values by column:")
print(df.isnull().sum())
print("\nExact duplicate rows:", df.duplicated().sum())
print("Distinct booking_channel values before cleaning:", df["booking_channel"].nunique())

# (a) Remove rows that are exact duplicates.
df = df.drop_duplicates()
print("\nRows after removing duplicates:", len(df))

# (b) Trim extra spaces and standardize capitalization in the labels.
df["booking_channel"] = df["booking_channel"].str.strip().str.title()
print("Rows after cleaning booking_channel:", len(df))
print("Distinct booking_channel values after cleaning:", df["booking_channel"].nunique())

# (c) Convert text dates to datetime values. Unreadable appointment dates become NaT.
df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")
df["booked_on"] = pd.to_datetime(df["booked_on"])
print("Rows after converting dates:", len(df))

# (d) Remove rows missing the appointment date or attendance status.
df = df.dropna(subset=["appt_date", "status"])
print("Rows after dropping missing appt_date or status:", len(df))