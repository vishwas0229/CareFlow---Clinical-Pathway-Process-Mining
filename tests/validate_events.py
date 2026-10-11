
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data" / "raw" / "hospital_events.csv"

REQUIRED_COLUMNS = {
    "Case_ID",
    "Activity_Name",
    "Timestamp",
}


def main():
    assert FILE.exists(), f"Missing file: {FILE}"

    df = pd.read_csv(FILE)

    # Schema validation
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    assert not missing_columns, f"Missing columns: {missing_columns}"

    # Basic completeness checks
    assert len(df) > 0, "Event log is empty"
    assert df["Case_ID"].notna().all(), "Missing Case_ID values"
    assert df["Activity_Name"].notna().all(), "Missing activity names"

    # Parse timestamps
    timestamps = pd.to_datetime(df["Timestamp"], errors="coerce")
    assert timestamps.notna().all(), "Invalid timestamps found"

    # Dataset-level checks
    case_count = df["Case_ID"].nunique()
    assert case_count == 500, f"Expected 500 cases, got {case_count}"

    assert not df.duplicated().any(), "Exact duplicate rows found"

    # Check loop-back scenarios after chronological sorting
    ordered = df.assign(_timestamp=timestamps).sort_values(
        ["Case_ID", "_timestamp"]
    )

    loop_cases = 0

    for _, case in ordered.groupby("Case_ID"):
        activities = case["Activity_Name"].tolist()

        # A case with multiple Triage events has a repeated Triage.
        if activities.count("Triage") > 1:
            loop_cases += 1

    assert loop_cases > 0, "No repeated-Triage cases found"

    print("PASS: CSV exists")
    print(f"PASS: Rows = {len(df)}")
    print(f"PASS: Unique cases = {case_count}")
    print("PASS: Required columns and timestamps are valid")
    print("PASS: No exact duplicate rows")
    print(f"PASS: Repeated-Triage cases = {loop_cases}")


if __name__ == "__main__":
    main()
