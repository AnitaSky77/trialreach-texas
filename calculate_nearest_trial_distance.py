import csv
import math
import statistics
from pathlib import Path


def read_csv(file_path):
    with file_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def distance_in_miles(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2,
):
    earth_radius_miles = 3958.8

    latitude_1 = math.radians(latitude_1)
    longitude_1 = math.radians(longitude_1)
    latitude_2 = math.radians(latitude_2)
    longitude_2 = math.radians(longitude_2)

    latitude_difference = latitude_2 - latitude_1
    longitude_difference = longitude_2 - longitude_1

    value = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(latitude_1)
        * math.cos(latitude_2)
        * math.sin(longitude_difference / 2) ** 2
    )

    return (
        2
        * earth_radius_miles
        * math.asin(math.sqrt(value))
    )


data_folder = Path("data")

county_access_file = (
    data_folder / "texas_county_trial_access.csv"
)

county_centroids_file = (
    data_folder / "texas_county_centroids.csv"
)

trial_sites_file = (
    data_folder
    / "texas_open_type_2_diabetes_trial_sites_with_counties.csv"
)

output_file = (
    data_folder
    / "texas_county_trial_access_with_distance.csv"
)

county_rows = read_csv(county_access_file)
centroid_rows = read_csv(county_centroids_file)
trial_site_rows = read_csv(trial_sites_file)

centroids_by_fips = {
    row["county_fips"]: row
    for row in centroid_rows
}

valid_trial_sites = []

for site in trial_site_rows:
    if site["latitude"] and site["longitude"]:
        valid_trial_sites.append(
            {
                **site,
                "latitude_number": float(site["latitude"]),
                "longitude_number": float(site["longitude"]),
            }
        )

results = []

for county in county_rows:
    county_fips = county["county_fips"]
    centroid = centroids_by_fips[county_fips]

    county_latitude = float(centroid["latitude"])
    county_longitude = float(centroid["longitude"])

    nearest_site = None
    nearest_distance = None

    for site in valid_trial_sites:
        distance = distance_in_miles(
            county_latitude,
            county_longitude,
            site["latitude_number"],
            site["longitude_number"],
        )

        if (
            nearest_distance is None
            or distance < nearest_distance
        ):
            nearest_distance = distance
            nearest_site = site

    results.append(
        {
            **county,
            "county_latitude": county_latitude,
            "county_longitude": county_longitude,
            "nearest_trial_distance_miles": round(
                nearest_distance,
                1,
            ),
            "nearest_trial_nct_id": nearest_site["nct_id"],
            "nearest_trial_facility": nearest_site["facility"],
            "nearest_trial_city": nearest_site["city"],
            "nearest_trial_county": nearest_site["county_name"],
        }
    )

fieldnames = list(results[0].keys())

with output_file.open(
    "w",
    newline="",
    encoding="utf-8",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(results)

distances = [
    row["nearest_trial_distance_miles"]
    for row in results
]

count_over_50 = sum(
    distance > 50
    for distance in distances
)

count_over_100 = sum(
    distance > 100
    for distance in distances
)

farthest_counties = sorted(
    results,
    key=lambda row: row["nearest_trial_distance_miles"],
    reverse=True,
)

print(f"Counties analyzed: {len(results)}")
print(
    "Median distance to nearest open site: "
    f"{statistics.median(distances):.1f} miles"
)
print(f"Counties over 50 miles away: {count_over_50}")
print(f"Counties over 100 miles away: {count_over_100}")

print("\nTen farthest counties:")

for county in farthest_counties[:10]:
    print(
        f"{county['county_name']}: "
        f"{county['nearest_trial_distance_miles']} miles"
    )

print(f"\nSaved CSV to {output_file}.")