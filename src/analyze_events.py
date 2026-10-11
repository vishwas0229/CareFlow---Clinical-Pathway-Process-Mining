
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw/hospital_events.csv"
OUT = ROOT / "reports"

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="raise")

    # Chronological order within each patient case
    df = df.sort_values(
        ["Case_ID", "Timestamp", "Event_ID"]
    ).copy()

    # 1. Activity frequency
    activity_counts = (
        df.groupby("Activity_Name")
        .agg(
            Event_Count=("Event_ID", "count"),
            Unique_Cases=("Case_ID", "nunique")
        )
        .reset_index()
        .sort_values("Event_Count", ascending=False)
    )
    activity_counts.to_csv(
        OUT / "activity_frequency.csv", index=False
    )

    # 2. Patient-level pathway summary
    pathways = (
        df.groupby("Case_ID")
        .agg(
            Event_Count=("Activity_Name", "size"),
            First_Event=("Timestamp", "min"),
            Last_Event=("Timestamp", "max"),
            Unique_Activities=("Activity_Name", "nunique")
        )
        .reset_index()
    )

    pathways["Case_Duration_Minutes"] = (
        pathways["Last_Event"] - pathways["First_Event"]
    ).dt.total_seconds() / 60

    pathways.to_csv(
        OUT / "case_summary.csv", index=False
    )

    # 3. Activity transitions
    df["Next_Activity"] = (
        df.groupby("Case_ID")["Activity_Name"].shift(-1)
    )

    transitions = (
        df.dropna(subset=["Next_Activity"])
        .groupby(["Activity_Name", "Next_Activity"])
        .size()
        .reset_index(name="Transition_Count")
        .sort_values("Transition_Count", ascending=False)
    )

    transitions.to_csv(
        OUT / "activity_transitions.csv", index=False
    )

    # 4. Repeated activities within a case
    repeated = (
        df.groupby(["Case_ID", "Activity_Name"])
        .size()
        .reset_index(name="Occurrences")
    )
    repeated = repeated[repeated["Occurrences"] > 1]

    repeated.to_csv(
        OUT / "repeated_activities.csv", index=False
    )

    # 5. Gaps between consecutive recorded events
    df["Previous_Timestamp"] = (
        df.groupby("Case_ID")["Timestamp"].shift(1)
    )

    df["Inter_Event_Gap_Minutes"] = (
        df["Timestamp"] - df["Previous_Timestamp"]
    ).dt.total_seconds() / 60

    df[[
        "Case_ID",
        "Activity_Name",
        "Timestamp",
        "Previous_Timestamp",
        "Inter_Event_Gap_Minutes"
    ]].to_csv(
        OUT / "inter_event_gaps.csv", index=False
    )

    print("PASS: Analysis completed")
    print(f"Cases: {df['Case_ID'].nunique()}")
    print(f"Events: {len(df)}")
    print(f"Activities: {df['Activity_Name'].nunique()}")
    print(f"Repeated case-activity combinations: {len(repeated)}")
    print("\nReports saved to:", OUT)

    print("\nTop activities:")
    print(activity_counts.head(10).to_string(index=False))

    print("\nTop transitions:")
    print(transitions.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
