# CareFlow — Clinical Pathway Process Mining

## Project Overview
CareFlow is a hospital process-mining and delay-analysis project that uses simulated patient event data to understand patient journeys, activity transitions, and waiting times.

## Objectives
- Prepare a standardized patient event log.
- Validate event timestamps and patient activity sequences.
- Discover hospital workflows using PM4Py.
- Analyze waiting time between triage and doctor consultation.
- Identify patient pathways and activities associated with longer gaps.

## Technologies Used
- Python
- pandas
- PM4Py
- Jupyter Notebook
- Git and GitHub

## Dataset Overview
The project uses simulated hospital patient data.

- Total patient cases: 500
- Total patient events: 2,607
- Main event fields: Case_ID, Activity_Name, Timestamp, Doctor_ID, Department

## Data Validation
The following checks were performed:
- Patient events are chronologically ordered.
- Activity sequences were validated.
- Previous activity and timestamp fields were checked.
- Gap calculations were validated.
- Required event-log fields have no missing values.

## Process Mining
PM4Py was used to discover the hospital process and generate:
- Process Tree: `careflow_process_tree.png`
- Directly-Follows Graph: `careflow_dfg.png`

These diagrams visualize patient activity sequences and common transitions.

## Delay Analysis Findings
- Average waiting time between triage and doctor consultation: 31.21 minutes
- Median waiting time: 29 minutes
- Maximum observed waiting time: 102 minutes
- Patients waiting more than 30 minutes: 233 (46.6%)
- Patients waiting more than 45 minutes: 68 (13.6%)

The findings are descriptive and do not prove that doctor availability caused patient delays.

## Project Outputs
- `healthcare_project.ipynb` — analysis notebook
- `careflow_process_tree.png` — discovered process tree
- `careflow_dfg.png` — Directly-Follows Graph
- `careflow_delay_analysis.csv` — patient-level waiting-time analysis
- `careflow_waiting_summary.csv` — waiting-time category summary
- `top_10_waiting_cases.csv` — ten longest waiting cases
- `careflow_pipeline_audit.csv` — pipeline validation results

## Pipeline Audit
The Python pipeline audit verified:
- 500 patient cases
- 2,607 events
- No missing values in Case_ID, Activity_Name, or Timestamp
- Chronological ordering within every patient case

## Limitations and Future Work
- The dataset is simulated and may not represent real hospital operations.
- Further verification is needed before drawing conclusions about the causes of delays.
- dbt models and BigQuery integration have not been implemented in the current version.
- Future work may include dashboard development and additional process-mining metrics.

## Conclusion
CareFlow demonstrates how Python, pandas, and PM4Py can be used to validate hospital event logs, discover patient pathways, and analyze patient waiting times.

## Patient Pathway Conformance Audit
A rule-based audit was run on the 500 patient cases to check:
- Whether each pathway starts with Registration
- Whether Triage occurs before Doctor_Consultation
- Whether the final activity is Discharge or Admission
- Whether timestamps are chronological within each case
- Whether consecutive duplicate activities occur

**Result:** All 500 cases passed all five checks; no cases were flagged for review. The detailed case-level results are in `careflow_conformance_audit.csv`.

This is a rule-based validation audit, not a formal PM4Py model-conformance measurement.

