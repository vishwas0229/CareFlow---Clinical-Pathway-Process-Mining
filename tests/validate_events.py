from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data" / "raw" / "hospital_events.csv"

REQUIRED_COLUMNS = {
    "Case_ID",
    "Activity_Name",
    "Timestamp",
}

ALL_COLUMNS = [
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

DATETIME_COLUMNS = ["Timestamp", "Start_Time", "End_Time"]


def main():
    assert FILE.exists(), f"Missing file: {FILE}"
    df = pd.read_csv(FILE)

    missing_required = REQUIRED_COLUMNS - set(df.columns)
    assert not missing_required, f"Missing required columns: {missing_required}"

    missing_all = set(ALL_COLUMNS) - set(df.columns)
    assert not missing_all, f"Missing agreed columns: {missing_all}"

    assert len(df) > 0, "Event log is empty"
    for column in ["Case_ID", "Activity_Name", "Timestamp", "Department",
                   "Event_ID", "Activity_Status", "Priority", "Start_Time", "End_Time"]:
        assert df[column].notna().all(), f"Missing values in {column}"

    parsed = {}
    for column in DATETIME_COLUMNS:
        parsed[column] = pd.to_datetime(df[column], errors="coerce")
        assert parsed[column].notna().all(), f"Invalid timestamps in {column}"

    case_count = df["Case_ID"].nunique()
    assert case_count == 500, f"Expected 500 cases, got {case_count}"

    assert df["Event_ID"].is_unique, "Event_ID values must be unique"
    assert not df.duplicated().any(), "Exact duplicate rows found"

    # Start must not be after end; Timestamp is defined as End_Time in this generator.
    assert (parsed["End_Time"] >= parsed["Start_Time"]).all(), "Negative activity duration found"
    assert (parsed["Timestamp"] == parsed["End_Time"]).all(), "Timestamp must equal End_Time"

    assert set(df["Activity_Status"].unique()) <= {"Completed", "Cancelled", "Pending"}
    assert set(df["Priority"].unique()) <= {"Routine", "Urgent", "Emergency"}

    ordered = df.assign(_timestamp=parsed["Timestamp"]).sort_values(
        ["Case_ID", "_timestamp"]
    )

    loop_cases = 0
    for _, case in ordered.groupby("Case_ID"):
        if case["Activity_Name"].tolist().count("Triage") > 1:
            loop_cases += 1

    assert loop_cases > 0, "No repeated-Triage cases found"

    print("PASS: CSV exists")
    print(f"PASS: Rows = {len(df)}")
    print(f"PASS: Unique cases = {case_count}")
    print("PASS: All nine agreed columns are present and complete")
    print("PASS: Timestamps parse and Timestamp equals End_Time")
    print("PASS: Start_Time <= End_Time for every event")
    print("PASS: Event_ID values are unique")
    print("PASS: No exact duplicate rows")
    print(f"PASS: Repeated-Triage cases = {loop_cases}")
    print("NOTE: Data and activity durations are synthetic, not real hospital records.")


if __name__ == "__main__":
    main()
