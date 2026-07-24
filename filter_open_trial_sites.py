import csv
from collections import Counter
from pathlib import Path


input_file = Path(
    "data/texas_type_2_diabetes_trial_sites.csv"
)

output_file = Path(
    "data/texas_open_type_2_diabetes_trial_sites.csv"
)


open_statuses = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
}


with input_file.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    all_sites = list(reader)


open_sites = [
    row
    for row in all_sites
    if row["facility_status"] in open_statuses
]


with output_file.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(open_sites)


unique_studies = {
    row["nct_id"]
    for row in open_sites
}


sites_with_coordinates = [
    row
    for row in open_sites
    if row["latitude"]
    and row["longitude"]
]


city_counts = Counter(
    row["city"]
    for row in open_sites
    if row["city"]
)


print(f"All Texas sites: {len(all_sites)}")
print(f"Open Texas sites: {len(open_sites)}")
print(f"Open unique studies: {len(unique_studies)}")

print(
    "Open sites with coordinates: "
    f"{len(sites_with_coordinates)}"
)


print("\nTop cities with open sites:")

for city, count in city_counts.most_common(10):
    print(f"{city}: {count}")


print(f"\nSaved CSV to {output_file}.")