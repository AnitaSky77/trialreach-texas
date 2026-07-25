import csv
from pathlib import Path

import requests


url = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/"
    "TIGERweb/State_County/MapServer/7/query"
)

parameters = {
    "where": "STATE='48'",
    "outFields": "GEOID,NAME,CENTLAT,CENTLON",
    "returnGeometry": "false",
    "outSR": "4326",
    "f": "json",
}

response = requests.get(
    url,
    params=parameters,
    timeout=60,
)

response.raise_for_status()

print("Status:", response.status_code)
print("URL:", response.url)
print("Response:", response.text[:500])

census_data = response.json()

if "error" in data:
    raise RuntimeError(data["error"])

rows = []

for feature in data.get("features", []):
    attributes = feature.get("attributes", {})

    rows.append(
        {
            "county_fips": attributes.get("GEOID", ""),
            "county_name": attributes.get("NAME", ""),
            "latitude": attributes.get("CENTLAT", ""),
            "longitude": attributes.get("CENTLON", ""),
        }
    )

rows.sort(key=lambda row: row["county_name"])

data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

output_file = data_folder / "texas_county_centroids.csv"

with output_file.open(
    "w",
    encoding="utf-8",
    newline="",
) as file:
    fieldnames = [
        "county_fips",
        "county_name",
        "latitude",
        "longitude",
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(rows)

count_with_coordinates = sum(
    1
    for row in rows
    if row["latitude"] != ""
    and row["longitude"] != ""
)

print(f"Texas counties downloaded: {len(rows)}")
print(f"Counties with coordinates: {count_with_coordinates}")
print(f"Saved CSV to {output_file}.")