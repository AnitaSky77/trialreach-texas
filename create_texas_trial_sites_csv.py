import csv
import json
from pathlib import Path


input_file = Path(
    "data/texas_type_2_diabetes_trials.json"
)

output_file = Path(
    "data/texas_type_2_diabetes_trial_sites.csv"
)


with input_file.open("r", encoding="utf-8") as file:
    data = json.load(file)


studies = data.get("studies", [])
site_rows = []
seen_sites = set()


for study in studies:
    protocol = study.get("protocolSection", {})

    identification = protocol.get(
        "identificationModule",
        {},
    )

    status_module = protocol.get(
        "statusModule",
        {},
    )

    design = protocol.get(
        "designModule",
        {},
    )

    locations_module = protocol.get(
        "contactsLocationsModule",
        {},
    )

    nct_id = identification.get("nctId", "")
    title = identification.get("briefTitle", "")
    study_status = status_module.get(
        "overallStatus",
        "",
    )

    study_type = design.get("studyType", "")
    phase = ", ".join(design.get("phases", []))

    locations = locations_module.get(
        "locations",
        [],
    )

    for location in locations:
        state = location.get("state", "")
        country = location.get("country", "")

        if state.lower() != "texas":
            continue

        if country.lower() != "united states":
            continue

        facility = location.get("facility", "")
        facility_status = location.get("status", "")
        city = location.get("city", "")
        zip_code = location.get("zip", "")

        geo_point = location.get("geoPoint", {})
        latitude = geo_point.get("lat", "")
        longitude = geo_point.get("lon", "")

        site_key = (
            nct_id,
            facility,
            city,
            zip_code,
            latitude,
            longitude,
        )

        if site_key in seen_sites:
            continue

        seen_sites.add(site_key)

        row = {
            "nct_id": nct_id,
            "title": title,
            "study_status": study_status,
            "study_type": study_type,
            "phase": phase,
            "facility": facility,
            "facility_status": facility_status,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "latitude": latitude,
            "longitude": longitude,
        }

        site_rows.append(row)


site_rows.sort(
    key=lambda row: (
        row["city"],
        row["nct_id"],
    )
)


fieldnames = [
    "nct_id",
    "title",
    "study_status",
    "study_type",
    "phase",
    "facility",
    "facility_status",
    "city",
    "state",
    "zip_code",
    "latitude",
    "longitude",
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
    writer.writerows(site_rows)


unique_studies = {
    row["nct_id"]
    for row in site_rows
}

sites_with_coordinates = sum(
    1
    for row in site_rows
    if row["latitude"] != ""
    and row["longitude"] != ""
)


print(f"Texas trial sites: {len(site_rows)}")
print(f"Unique studies: {len(unique_studies)}")
print(
    "Sites with coordinates: "
    f"{sites_with_coordinates}"
)