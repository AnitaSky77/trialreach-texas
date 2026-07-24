import csv
import json
from pathlib import Path

import requests


url = "https://data.cdc.gov/resource/i46a-9kgh.json"

parameters = {
    "$select": (
        "stateabbr,"
        "countyname,"
        "countyfips,"
        "totalpopulation,"
        "diabetes_crudeprev,"
        "diabetes_crude95ci,"
        "diabetes_adjprev,"
        "diabetes_adj95ci"
    ),
    "$where": "stateabbr='TX'",
    "$limit": 500,
}


response = requests.get(
    url,
    params=parameters,
    timeout=30,
)

response.raise_for_status()
counties = response.json()


print(f"Downloaded {len(counties)} Texas counties.")

for county in counties[:5]:
    name = county.get("countyname", "Unknown")
    prevalence = county.get("diabetes_crudeprev", "Unknown")

    print(f"{name}: {prevalence}%")

data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

json_file = data_folder / "texas_county_diabetes_prevalence.json"
csv_file = data_folder / "texas_county_diabetes_prevalence.csv"


with json_file.open("w", encoding="utf-8") as file:
    json.dump(counties, file, indent=2)


fieldnames = [
    "stateabbr",
    "countyname",
    "countyfips",
    "totalpopulation",
    "diabetes_crudeprev",
    "diabetes_crude95ci",
    "diabetes_adjprev",
    "diabetes_adj95ci",
]


with csv_file.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )

    writer.writeheader()
    writer.writerows(counties)


print(f"\nSaved JSON to {json_file}.")
print(f"Saved CSV to {csv_file}.")    