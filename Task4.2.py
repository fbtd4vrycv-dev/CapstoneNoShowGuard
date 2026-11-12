"""Task 4.2: validate the first ten follow-up notes and save all replies."""

# In Colab, install once with: !pip install -q google-genai pydantic pandas

import importlib.util
import sys
import time
from getpass import getpass
from pathlib import Path

import pandas as pd
from google import genai
from pydantic import BaseModel, Field


PROJECT_DIR = Path(__file__).resolve().parent
NOTES_FILE = PROJECT_DIR / "data" / "followup_notes.csv"
OUTPUT_FILE = PROJECT_DIR / "notes_analysed.csv"
TASK_41_FILE = PROJECT_DIR / "Task4.1.py"

ALLOWED_CAUSES = [
    "forgot_or_no_reminder",
    "distance_or_transport",
    "cost_or_fee",
    "illness_or_emergency",
    "work_or_schedule",
    "other",
]
INSIGHT_FIELDS = ["root_cause", "confidence", "summary", "recommended_action"]
OUTPUT_COLUMNS = [
    "note_id",
    "appointment_id",
    *INSIGHT_FIELDS,
    "validation_status",
    "raw_response",
]


class FollowupInsight(BaseModel):
    root_cause: str = Field(min_length=3)
    confidence: float = Field(ge=0, le=1)
    summary: str = Field(min_length=5)
    recommended_action: str = Field(min_length=5)


def load_task_41_module():
    spec = importlib.util.spec_from_file_location("task4_1", TASK_41_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {TASK_41_FILE}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def is_blank_note(note_text) -> bool:
    if pd.isna(note_text):
        return True
    return str(note_text).strip() == ""


def main():
    task41 = load_task_41_module()
    notes = pd.read_csv(NOTES_FILE).head(10)
    api_call_total = sum(
        not is_blank_note(note_text) for note_text in notes["note_text"]
    )

    api_key = getpass("Paste your Gemini API key (input hidden): ")
    task41._client = genai.Client(api_key=api_key)

    results = []
    api_calls_made = 0

    for _, row in notes.iterrows():
        record = {
            "note_id": row["note_id"],
            "appointment_id": row["appointment_id"],
            "root_cause": "",
            "confidence": "",
            "summary": "",
            "recommended_action": "",
            "validation_status": "invalid",
            "raw_response": "",
        }

        note_text = row["note_text"]
        if is_blank_note(note_text):
            record.update(
                {
                    "root_cause": "other",
                    "confidence": 0.0,
                    "summary": "No note recorded",
                    "recommended_action": "Re-call patient",
                    "validation_status": "skipped_blank",
                }
            )
            results.append(record)
            print(f"{row['note_id']}: skipped_blank (no API call)")
            continue

        api_calls_made += 1
        data = None
        try:
            task41.analyse_note(str(note_text).strip())
            data = task41.LAST_PARSED_RESPONSE
            record["raw_response"] = task41.LAST_RAW_RESPONSE

            if not isinstance(data, dict):
                raise ValueError("Response JSON must be an object.")

            insight = FollowupInsight(**data)
            if insight.root_cause not in ALLOWED_CAUSES:
                raise ValueError("root_cause is not in the allowed list.")
            record["validation_status"] = "valid"
        except Exception:
            # Keep the original response and parsed fields even when validation fails.
            data = task41.LAST_PARSED_RESPONSE
            record["raw_response"] = task41.LAST_RAW_RESPONSE
            record["validation_status"] = "invalid"

        if isinstance(data, dict):
            for field in INSIGHT_FIELDS:
                if field in data:
                    record[field] = data[field]

        results.append(record)
        print(f"{row['note_id']}: {record['validation_status']}")

        if api_calls_made < api_call_total:
            time.sleep(13)

    output = pd.DataFrame(results, columns=OUTPUT_COLUMNS)
    output.to_csv(OUTPUT_FILE, index=False)
    print(
        f"Saved {len(output)} notes ({api_calls_made} API calls) to "
        f"{OUTPUT_FILE.name}."
    )


if __name__ == "__main__":
    main()
