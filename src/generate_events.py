
from pathlib import Path
import numpy as np
import pandas as pd

# Reproducible synthetic dataset
SEED = 42
NUM_PATIENTS = 500

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "hospital_events.csv"

rng = np.random.default_rng(SEED)

ACTIVITIES = [
    "Registration",
    "Triage",
    "Doctor Consultation",
    "X-Ray",
    "Lab Test",
    "Treatment",
    "Discharge",
]


def generate_patient_events(case_number, start_time):
    """Generate one synthetic hospital visit."""

    case_id = f"CF{case_number:04d}"
    current_time = pd.Timestamp(start_time)
    events = []

    def add_event(activity, delay_minutes):
        nonlocal current_time

        current_time += pd.Timedelta(minutes=delay_minutes)

        events.append({
            "Case_ID": case_id,
            "Activity_Name": activity,
            "Timestamp": current_time,
        })

    # Registration and triage
    add_event("Registration", 0)
    add_event("Triage", int(rng.integers(5, 21)))

    # Choose a pathway type
    pathway = rng.choice(
        ["normal", "xray_loop", "lab_path", "delayed_doctor"],
        p=[0.40, 0.30, 0.15, 0.15],
    )

    if pathway == "normal":
        add_event("Doctor Consultation", int(rng.integers(5, 31)))

    elif pathway == "xray_loop":
        add_event("X-Ray", int(rng.integers(5, 16)))
        add_event("Triage", int(rng.integers(10, 31)))
        add_event("Doctor Consultation", int(rng.integers(10, 36)))

    elif pathway == "lab_path":
        add_event("Doctor Consultation", int(rng.integers(5, 21)))
        add_event("Lab Test", int(rng.integers(10, 41)))
        add_event("Doctor Consultation", int(rng.integers(5, 26)))

    else:
        add_event("Doctor Consultation", int(rng.integers(45, 91)))

    add_event("Treatment", int(rng.integers(5, 31)))
    add_event("Discharge", int(rng.integers(5, 21)))

    return events


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_events = []

    base_time = pd.Timestamp("2026-10-01 09:00:00")

    for patient_number in range(1, NUM_PATIENTS + 1):
        # Stagger patient arrivals across the simulation.
        arrival = base_time + pd.Timedelta(
            minutes=int((patient_number - 1) * 4)
        )

        all_events.extend(
            generate_patient_events(patient_number, arrival)
        )

    df = pd.DataFrame(all_events)

    # Shuffle rows to simulate unordered source extracts.
    # Week 2 will normalize and sort them chronologically.
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(df)} event rows")
    print(f"Unique cases: {df['Case_ID'].nunique()}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nSample records:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
