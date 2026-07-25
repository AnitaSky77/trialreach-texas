import csv
from pathlib import Path


data_folder = Path("data")

access_file = data_folder / "texas_county_trial_access_with_distance.csv"
socioeconomic_file = data_folder / "texas_county_socioeconomic.csv"
output_file = data_folder / "texas_county_trial_access_socioeconomic.csv"


with access_file.open("r", encoding="utf-8-sig") as file:
    access_rows = list(csv.DictReader(file))


with socioeconomic_file.open("r", encoding="utf-8-sig") as file:
    socioeconomic_reader = csv.DictReader(file)
    socioeconomic_rows = list(socioeconomic_reader)
    socioeconomic_fields = socioeconomic_reader.fieldnames or []


socioeconomic_by_fips = {
    row["county_fips"].zfill(5): row
    for row in socioeconomic_rows
}


merged_rows = []
matched_counties = 0
unmatched_counties = []


for access_row in access_rows:
    county_fips = access_row["county_fips"].zfill(5)
    socioeconomic_row = socioeconomic_by_fips.get(county_fips)

    merged_row = access_row.copy()

    if socioeconomic_row:
        matched_counties += 1

        for field in socioeconomic_fields:
            if field not in {"county_fips", "county_name"}:
                merged_row[field] = socioeconomic_row.get(field, "")
    else:
        unmatched_counties.append(access_row["county_name"])

        for field in socioeconomic_fields:
            if field not in {"county_fips", "county_name"}:
                merged_row[field] = ""

    merged_rows.append(merged_row)


output_fields = list(access_rows[0].keys())

for field in socioeconomic_fields:
    if field not in output_fields and field != "county_name":
        output_fields.append(field)


with output_file.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=output_fields,
    )
    writer.writeheader()
    writer.writerows(merged_rows)


print(f"Trial-access counties: {len(access_rows)}")
print(f"Socioeconomic counties: {len(socioeconomic_rows)}")
print(f"Successfully matched counties: {matched_counties}")
print(f"Unmatched counties: {len(unmatched_counties)}")

if unmatched_counties:
    print("Unmatched county names:")
    for county_name in unmatched_counties:
        print(county_name)

print(f"Saved merged CSV to {output_file}.")