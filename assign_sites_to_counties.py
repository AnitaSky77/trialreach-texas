import csv
from pathlib import Path

import requests


input_file = Path(
    "data/texas_open_type_2_diabetes_trial_sites.csv"
)

output_file = Path(
    "data/"
    "texas_open_type_2_diabetes_trial_sites_with_counties.csv"
)


with input_file.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    original_fields = reader.fieldnames
    site_rows = list(reader)


census_url = (
    "https://tigerweb.geo.census.gov/"
    "arcgis/rest/services/TIGERweb/"
    "State_County/MapServer/7/query"
)


coordinate_cache = {}
session = requests.Session()


for index, row in enumerate(site_rows, start=1):
    latitude = row["latitude"]
    longitude = row["longitude"]

    coordinate_key = (
        latitude,
        longitude,
    )

    if coordinate_key in coordinate_cache:
        county_data = coordinate_cache[
            coordinate_key
        ]

    else:
        parameters = {
            "where": "1=1",
            "geometry": (
                f"{longitude},{latitude}"
            ),
            "geometryType": (
                "esriGeometryPoint"
            ),
            "inSR": "4326",
            "spatialRel": (
                "esriSpatialRelIntersects"
            ),
            "outFields": (
                "BASENAME,GEOID"
            ),
            "returnGeometry": "false",
            "f": "json",
        }

        response = session.get(
            census_url,
            params=parameters,
            timeout=30,
        )

        response.raise_for_status()
        result = response.json()

        features = result.get("features", [])

        if features:
            attributes = features[0].get(
                "attributes",
                {},
            )

            county_data = {
                "county_name": attributes.get(
                    "BASENAME",
                    "",
                ),
                "county_fips": attributes.get(
                    "GEOID",
                    "",
                ),
            }

        else:
            county_data = {
                "county_name": "",
                "county_fips": "",
            }

        coordinate_cache[
            coordinate_key
        ] = county_data

        print(
            f"Matched location "
            f"{len(coordinate_cache)}: "
            f"{row['city']}"
        )

    row["county_name"] = county_data[
        "county_name"
    ]

    row["county_fips"] = county_data[
        "county_fips"
    ]


fieldnames = original_fields + [
    "county_name",
    "county_fips",
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


matched_sites = sum(
    1
    for row in site_rows
    if row["county_fips"]
)

unmatched_sites = (
    len(site_rows) - matched_sites
)


print(f"\nTotal sites: {len(site_rows)}")
print(f"Matched sites: {matched_sites}")
print(f"Unmatched sites: {unmatched_sites}")

print(
    "Unique coordinate lookups: "
    f"{len(coordinate_cache)}"
)

print(f"Saved CSV to {output_file}.")