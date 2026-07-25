import csv
import os
from pathlib import Path

import requests


URL = "https://api.census.gov/data/2024/acs/acs5"

PARAMETERS = {
    "get": (
        "NAME,"
        "B19013_001E,"
        "B17001_001E,"
        "B17001_002E,"
        "B08201_001E,"
        "B08201_002E"
    ),
    "for": "county:*",
    "in": "state:48",
    "key": os.environ["CENSUS_API_KEY"],
}

OUTPUT_FILE = Path(
    "data/texas_county_socioeconomic.csv"
)


response = requests.get(
    URL,
    params=PARAMETERS,
    timeout=30,
)

response.raise_for_status()
census_data = response.json()

headers = census_data[0]
records = census_data[1:]


rows = []

for record in records:
    county = dict(zip(headers, record))

    poverty_population = float(
        county["B17001_001E"]
    )

    population_below_poverty = float(
        county["B17001_002E"]
    )

    total_households = float(
        county["B08201_001E"]
    )

    households_without_vehicle = float(
        county["B08201_002E"]
    )

    if poverty_population > 0:
        poverty_percent = (
            population_below_poverty
            / poverty_population
            * 100
        )
    else:
        poverty_percent = ""

    if total_households > 0:
        no_vehicle_percent = (
            households_without_vehicle
            / total_households
            * 100
        )
    else:
        no_vehicle_percent = ""

    county_name = county["NAME"].split(",")[0]
    county_fips = county["state"] + county["county"]

    rows.append(
        {
            "county_fips": county_fips,
            "county_name": county_name,
            "median_household_income": (
                county["B19013_001E"]
            ),
            "poverty_percent": (
                round(poverty_percent, 1)
                if poverty_percent != ""
                else ""
            ),
            "households_without_vehicle_percent": (
                round(no_vehicle_percent, 1)
                if no_vehicle_percent != ""
                else ""
            ),
            "acs_vintage": "2024 ACS 5-year",
        }
    )


rows.sort(
    key=lambda row: row["county_name"]
)


fieldnames = [
    "county_fips",
    "county_name",
    "median_household_income",
    "poverty_percent",
    "households_without_vehicle_percent",
    "acs_vintage",
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(rows)


print(
    f"Downloaded socioeconomic data "
    f"for {len(rows)} Texas counties."
)

print(f"Saved CSV to {OUTPUT_FILE}.")