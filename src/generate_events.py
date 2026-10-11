from pathlib import Path
import numpy as np
import pandas as pd

# Reproducible synthetic dataset. These are NOT real patient records.
SEED = 42
NUM_PATIENTS = 500

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "hospital_events.csv"

rng = np.random.default_rng(SEED)

ACTIVITY_DEPARTMENTS = {
    "Registration": "Reception",
    "Triage": "Emergency",
    "Doctor Consultation": "Outpatient",
    "X-Ray": "Radiology",
    "Lab Test": "Laboratory",
    "Treatment": "Treatment",
    "Discharge": "Reception",
}

# Existing ranges are preserved as wait time before each activity.
# Activity durations below are synthetic assumptions for demonstration only.
ACTIVITY_DURATION_RANGES = {
    "Registration": (2, 6),
    "Triage": (5, 12),
    "Doctor Consultation": (10, 25),
    "X-Ray": (10, 20),
    "Lab Test": (10, 30),
    "Treatment": (10, 25),
    "Discharge": (2, 6),
}

PRIORITIES = ["Routine", "Urgent", "Emergency"]
PRIORITY_PROBABILITIES = [0.55, 0.32, 0.13]

COLUMNS = [
    "Case_ID",
    "Activity_Name",
    "Timestamp",
    "Department",
    "Event_ID",
    "Activity_Status",
    "Priority",
    "Start_Time",
    "End_Time",
]


def generate_patient_events(case_number, arrival_time, priority):
    """Generate one synthetic visit with all nine agreed event-log columns."""
    case_id = f"CF{case_number:04d}"
    current_time = pd.Timestamp(arrival_time)
    events = []

    def add_event(activity, wait_minutes):
        nonlocal current_time

        # Wait until this activity begins.
        activity_start = current_time + pd.Timedelta(minutes=int(wait_minutes))
        duration_min, duration_max = ACTIVITY_DURATION_RANGES[activity]
        duration_minutes = int(rng.integers(duration_min, duration_max + 1))
        activity_end = activity_start + pd.Timedelta(minutes=duration_minutes)

        events.append({
            "Case_ID": case_id,
            "Activity_Name": activity,
            # Defined consistently as the event/activity completion timestamp.
            "Timestamp": activity_end,
            "Department": ACTIVITY_DEPARTMENTS[activity],
            "Activity_Status": "Completed",
            "Priority": priority,
            "Start_Time": activity_start,
            "End_Time": activity_end,
        })
        current_time = activity_end

    # Registration starts at arrival; subsequent delays preserve the original
    # generator's transition-delay ranges.
    add_event("Registration", 0)
    add_event("Triage", int(rng.integers(5, 21)))

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
        arrival = base_time + pd.Timedelta(minutes=(patient_number - 1) * 4)
        priority = str(rng.choice(PRIORITIES, p=PRIORITY_PROBABILITIES))
        all_events.extend(generate_patient_events(patient_number, arrival, priority))

    df = pd.DataFrame(all_events)

    # Deterministic unique event identifiers assigned before shuffling.
    df.insert(4, "Event_ID", [f"EVT{i:07d}" for i in range(1, len(df) + 1)])
    df = df[COLUMNS]

    # Keep the original behaviour of producing an unordered source extract.
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False, date_format="%Y-%m-%d %H:%M:%S")

    print(f"Generated {len(df)} synthetic event rows")
    print(f"Unique cases: {df['Case_ID'].nunique()}")
    print(f"Columns: {', '.join(df.columns)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nSample records:")
    print(df.head(10).to_string(index=False))
    print("\nNote: durations and priorities are synthetic demo assumptions.")


if __name__ == "__main__":
    main()
