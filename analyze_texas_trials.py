import csv
import json
from collections import Counter
from pathlib import Path


input_file = Path("data/texas_type_2_diabetes_trials.csv")
output_file = Path("data/texas_trials_summary.json")


with input_file.open("r", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))


active_statuses = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
}


status_counts = Counter()
city_counts = Counter()
sponsor_counts = Counter()
phase_counts = Counter()

confirmed_texas_locations = 0
missing_texas_locations = 0
active_studies = 0


for row in rows:
    status = row["status"].strip() or "MISSING"
    status_counts[status] += 1

    if status in active_statuses:
        active_studies += 1

    texas_cities = row["texas_cities"].strip()

    if texas_cities:
        confirmed_texas_locations += 1

        for city in texas_cities.split(","):
            clean_city = city.strip()

            if clean_city:
                city_counts[clean_city] += 1
    else:
        missing_texas_locations += 1

    sponsor = row["sponsor"].strip()

    if sponsor:
        sponsor_counts[sponsor] += 1

    phases = row["phase"].strip()

    if phases:
        for phase in phases.split(","):
            clean_phase = phase.strip()

            if clean_phase:
                phase_counts[clean_phase] += 1


summary = {
    "total_studies": len(rows),
    "active_studies": active_studies,
    "confirmed_texas_locations": confirmed_texas_locations,
    "missing_texas_locations": missing_texas_locations,
    "status_counts": dict(status_counts),
    "top_texas_cities": dict(city_counts.most_common(10)),
    "top_sponsors": dict(sponsor_counts.most_common(10)),
    "phase_counts": dict(phase_counts),
}


with output_file.open("w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2)


print("\nTRIALREACH TEXAS SUMMARY")
print("------------------------")
print(f"Total studies: {len(rows)}")
print(f"Active studies: {active_studies}")
print(
    "Studies with confirmed Texas cities: "
    f"{confirmed_texas_locations}"
)
print(
    "Studies missing Texas cities: "
    f"{missing_texas_locations}"
)

print("\nStudies by status:")

for status, count in status_counts.most_common():
    print(f"{status}: {count}")

print("\nTop 10 Texas cities:")

for city, count in city_counts.most_common(10):
    print(f"{city}: {count}")

print("\nTop 10 sponsors:")

for sponsor, count in sponsor_counts.most_common(10):
    print(f"{sponsor}: {count}")

print("\nStudies by phase:")

for phase, count in phase_counts.most_common():
    print(f"{phase}: {count}")

print(f"\nSaved summary to {output_file}.")