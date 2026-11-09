"""Enrich clinic records with the first Open-Meteo temperature reading."""

from pathlib import Path
import time

import pandas as pd
import requests


PROJECT_DIR = Path(__file__).resolve().parent
CLINICS_FILE = PROJECT_DIR / "data" / "clinics.csv"
OUTPUT_FILE = PROJECT_DIR / "clinics_enriched.csv"
API_URL = "https://api.open-meteo.com/v1/forecast"


def get_temperature(latitude, longitude):
    """Return the first hourly temperature, or None after two failed attempts."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "forecast_days": 1,
    }

    for attempt in range(2):
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            if response.status_code != 200:
                reason = f"HTTP status {response.status_code}"
            else:
                hourly = response.json().get("hourly")
                temperatures = hourly.get("temperature_2m") if hourly else None
                if temperatures:
                    return temperatures[0], None
                reason = "response is missing hourly temperature_2m data"
        except requests.exceptions.RequestException as error:
            reason = f"request failed: {error}"
        except (ValueError, AttributeError) as error:
            reason = f"invalid response JSON: {error}"

        if attempt == 0:
            time.sleep(1)

    return None, reason


def main():
    if not CLINICS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {CLINICS_FILE}. Create data/clinics.csv with one row per "
            "clinic and columns clinic_id, clinic_name, latitude, longitude."
        )

    clinics = pd.read_csv(CLINICS_FILE)
    required_columns = {"clinic_id", "clinic_name", "latitude", "longitude"}
    missing_columns = required_columns - set(clinics.columns)
    if missing_columns:
        raise ValueError(f"data/clinics.csv is missing columns: {sorted(missing_columns)}")
    if len(clinics) != 8:
        raise ValueError(f"Expected 8 clinic rows, found {len(clinics)}")

    temperatures = []
    for _, clinic in clinics.iterrows():
        temperature, reason = get_temperature(clinic["latitude"], clinic["longitude"])
        temperatures.append(temperature)
        if reason:
            print(f"{clinic['clinic_name']}: {reason}; temp_c set to None")

    clinics["temp_c"] = temperatures
    clinics.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved enriched clinic data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
