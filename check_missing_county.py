import csv
from pathlib import Path

import requests


cdc_file = Path(
    "data/texas_county_diabetes_prevalence.csv"
)


with cdc_file.open("r", encoding="utf-8") as file:
    cdc_rows = list(csv.DictReader(file))


cdc_counties = {
    row["countyfips"].zfill(5): row["countyname"]
    for row in cdc_rows
}


census_url = (
    "https://tigerweb.geo.census.gov/"
    "arcgis/rest/services/TIGERweb/"
    "State_County/MapServer/7/query"
)


parameters = {
    "where": "STATE='48'",
    "outFields": (
        "BASENAME,"
        "STATE,"
        "COUNTY,"
        "GEOID"
    ),
    "returnGeometry": "false",
    "f": "json",
}


response = requests.get(
    census_url,
    params=parameters,
    timeout=30,
)

response.raise_for_status()
census_data = response.json()


features = census_data.get("features", [])
census_counties = {}


for feature in features:
    attributes = feature.get("attributes", {})

    county_name = attributes.get(
        "BASENAME",
        "Unknown",
    )

    state_code = attributes.get("STATE", "")
    county_code = attributes.get("COUNTY", "")

    full_fips = attributes.get(
        "GEOID",
        state_code + county_code,
    )

    census_counties[full_fips] = county_name


missing_fips = (
    set(census_counties) - set(cdc_counties)
)


print(f"CDC county records: {len(cdc_counties)}")
print(f"Census county records: {len(census_counties)}")


print("\nCounties missing from CDC PLACES:")

for fips in sorted(missing_fips):
    name = census_counties[fips]
    print(f"{name}, FIPS {fips}")