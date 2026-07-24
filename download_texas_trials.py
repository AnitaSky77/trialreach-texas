import json
from pathlib import Path

import requests


url = "https://clinicaltrials.gov/api/v2/studies"

base_parameters = {
    "query.cond": "Type 2 Diabetes",
    "query.locn": "Texas, United States",
    "pageSize": 1000,
    "format": "json",
    "countTotal": "true",
}

all_studies = []
next_page_token = None
page_number = 1


while True:
    parameters = base_parameters.copy()

    if next_page_token:
        parameters["pageToken"] = next_page_token

    response = requests.get(
        url,
        params=parameters,
        timeout=60,
    )

    response.raise_for_status()
    page_data = response.json()

    page_studies = page_data.get("studies", [])
    all_studies.extend(page_studies)

    print(
        f"Page {page_number}: "
        f"downloaded {len(page_studies)} studies."
    )

    next_page_token = page_data.get("nextPageToken")

    if not next_page_token:
        break

    page_number += 1


output_data = {
    "totalCount": len(all_studies),
    "studies": all_studies,
}

data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

output_file = data_folder / "texas_type_2_diabetes_trials.json"

with output_file.open("w", encoding="utf-8") as file:
    json.dump(output_data, file, indent=2)


print(f"\nDownloaded {len(all_studies)} studies in total.")
print(f"Saved them to {output_file}.")


print("\nFirst five studies:")

for study in all_studies[:5]:
    protocol = study.get("protocolSection", {})

    identification = protocol.get(
        "identificationModule",
        {},
    )

    status_module = protocol.get(
        "statusModule",
        {},
    )

    nct_id = identification.get("nctId", "Unknown")
    title = identification.get("briefTitle", "Unknown")
    status = status_module.get("overallStatus", "Unknown")

    print(f"\nStudy ID: {nct_id}")
    print(f"Title: {title}")
    print(f"Status: {status}")