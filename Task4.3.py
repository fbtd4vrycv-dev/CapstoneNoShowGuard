"""Task 4.3: test validation and compare simple versus CRAFT prompts."""

# In Colab, install once with: !pip install -q google-genai pydantic pandas

import importlib.util
import json
import sys
from getpass import getpass
from pathlib import Path

import pandas as pd
from google import genai
from google.genai import types
from pydantic import ValidationError


PROJECT_DIR = Path(__file__).resolve().parent
TASK_41_FILE = PROJECT_DIR / "Task4.1.py"
TASK_42_FILE = PROJECT_DIR / "Task4.2.py"
NOTES_FILE = PROJECT_DIR / "data" / "followup_notes.csv"
ANALYSED_FILE = PROJECT_DIR / "notes_analysed.csv"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {file_path}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def show_validation_failures(FollowupInsight):
    bad_replies = [
        (
            "Confidence above 1",
            {
                "root_cause": "other",
                "confidence": 1.7,
                "summary": "The note gives no clear cause.",
                "recommended_action": "Call the patient again.",
            },
        ),
        (
            "Missing recommended_action",
            {
                "root_cause": "other",
                "confidence": 0.5,
                "summary": "The note gives no clear cause.",
            },
        ),
    ]

    print("Pydantic validation failures:")
    for label, data in bad_replies:
        try:
            FollowupInsight(**data)
        except ValidationError as error:
            print(f"\n{label}:\n{error}")
        else:
            print(f"\n{label}: unexpectedly passed validation")


def build_craft_prompt(note_text):
    return f"""Context: A clinic is reviewing short call-centre notes about missed appointments.
Role: You are a careful classifier of the reason stated in each note.
Action: Select the single best root cause, estimate confidence from 0 to 1, summarize
the evidence in no more than 25 words, and recommend one practical clinic action.
Tone: Neutral, concise, and grounded only in the note. If the reason is unclear, use
other and state that the note gives insufficient detail.
Format: Return exactly the four fields defined by the JSON response schema. The
root_cause must be exactly one of: forgot_or_no_reminder, distance_or_transport,
cost_or_fee, illness_or_emergency, work_or_schedule, other.
Use forgot_or_no_reminder when the patient forgot or missed a reminder; distance_or_transport
for travel barriers; cost_or_fee for affordability; illness_or_emergency for health issues;
work_or_schedule for job or timing conflicts. Use other if no cause is stated, including
when the note only says the patient could not be reached by phone.

Follow-up note:
{note_text}
"""


def parse_json_object(raw_response):
    if not isinstance(raw_response, str) or not raw_response.strip():
        return None
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def make_result(note_id, prompt_version, raw_response, data, allowed_causes):
    root_cause = data.get("root_cause", "") if isinstance(data, dict) else ""
    return {
        "note_id": note_id,
        "prompt": prompt_version,
        "root_cause": root_cause,
        "allowed": root_cause in allowed_causes,
        "raw_response": raw_response,
    }


def main():
    task41 = load_module("task4_1", TASK_41_FILE)
    task42 = load_module("task4_2", TASK_42_FILE)
    FollowupInsight = task42.FollowupInsight
    allowed_causes = task42.ALLOWED_CAUSES

    show_validation_failures(FollowupInsight)

    notes = pd.read_csv(NOTES_FILE).set_index("note_id")
    previous_results = pd.read_csv(ANALYSED_FILE).set_index("note_id")
    api_key = getpass("Paste your Gemini API key (input hidden): ")
    client = genai.Client(api_key=api_key)

    # V1 and V2 use the same model, schema, system text, and generation settings.
    config = types.GenerateContentConfig(
        system_instruction=task41.SYSTEM_TEXT,
        temperature=0,
        max_output_tokens=1000,
        response_mime_type="application/json",
        response_schema=task41.SCHEMA,
        thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    def call_model(prompt):
        response = client.models.generate_content(
            model=task41.MODEL_NAME,
            contents=prompt,
            config=config,
        )
        raw_response = response.text or ""
        return raw_response, parse_json_object(raw_response)

    results = []
    calls_in_task_43 = 0
    for note_id in ("N007", "N009"):
        note_text = str(notes.loc[note_id, "note_text"]).strip()

        # V1: deliberately minimal prompt; schema and generation settings stay fixed.
        v1_raw, v1_data = call_model(f"Classify this note:\n\n{note_text}")
        calls_in_task_43 += 1
        results.append(make_result(note_id, "V1", v1_raw, v1_data, allowed_causes))

        # Reuse the matching CRAFT reply saved by Task 4.2 when available.
        saved_raw = previous_results.loc[note_id, "raw_response"]
        saved_data = parse_json_object(saved_raw)
        if saved_data is None:
            v2_raw, v2_data = call_model(build_craft_prompt(note_text))
            calls_in_task_43 += 1
        else:
            v2_raw, v2_data = saved_raw, saved_data
        results.append(
            make_result(note_id, "V2 (CRAFT)", v2_raw, v2_data, allowed_causes)
        )

    table = pd.DataFrame(results)
    print("\nPrompt comparison:")
    print(table[["note_id", "prompt", "root_cause", "allowed"]].to_string(index=False))
    print(
        "\nI would deploy V2 (CRAFT): it names the allowed labels and tells the model "
        "to use 'other' when the note does not support a clear cause."
    )

    first_ten = pd.read_csv(NOTES_FILE).head(10)
    calls_in_task_42 = sum(
        not task42.is_blank_note(note_text) for note_text in first_ten["note_text"]
    )
    calls_in_task_41 = 1  # One N001 call in the completed first pass.
    total_calls = calls_in_task_41 + calls_in_task_42 + calls_in_task_43
    print(
        f"API calls: Task 4.1 = {calls_in_task_41}, Task 4.2 = {calls_in_task_42}, "
        f"Task 4.3 = {calls_in_task_43}; total = {total_calls}."
    )


if __name__ == "__main__":
    main()
