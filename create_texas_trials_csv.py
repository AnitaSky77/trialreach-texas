import csv
import json
from pathlib import Path


input_file = Path("data/texas_type_2_diabetes_trials.json")
output_file = Path("data/texas_type_2_diabetes_trials.csv")


with input_file.open("r", encoding="utf-8") as file:
    data = json.load(file)


studies = data.get("studies", [])
rows = []


for study in studies:
    protocol = study.get("protocolSection", {})

    identification = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    sponsors = protocol.get("sponsorCollaboratorsModule", {})
    contacts = protocol.get("contactsLocationsModule", {})

    nct_id = identification.get("nctId", "")
    title = identification.get("briefTitle", "")
    status = status_module.get("overallStatus", "")
    study_type = design.get("studyType", "")

    phases = design.get("phases", [])
    phase = ", ".join(phases)

    enrollment = design.get("enrollmentInfo", {}).get("count", "")

    sponsor = sponsors.get("leadSponsor", {}).get("name", "")

    start_date = (
        status_module
        .get("startDateStruct", {})
        .get("date", "")
    )

    completion_date = (
        status_module
        .get("completionDateStruct", {})
        .get("date", "")
    )

    locations = contacts.get("locations", [])
    texas_cities = []

    for location in locations:
        state = location.get("state", "")
        country = location.get("country", "")
        city = location.get("city", "")

        if state.lower() == "texas" and country.lower() == "united states":
            if city:
                texas_cities.append(city)

    texas_cities = sorted(set(texas_cities))

    row = {
        "nct_id": nct_id,
        "title": title,
        "status": status,
        "study_type": study_type,
        "phase": phase,
        "enrollment": enrollment,
        "sponsor": sponsor,
        "texas_cities": ", ".join(texas_cities),
        "start_date": start_date,
        "completion_date": completion_date,
    }

    rows.append(row)


fieldnames = [
    "nct_id",
    "title",
    "status",
    "study_type",
    "phase",
    "enrollment",
    "sponsor",
    "texas_cities",
    "start_date",
    "completion_date",
]


with output_file.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print(f"Created CSV with {len(rows)} studies.")
print(f"Saved it to {output_file}.")