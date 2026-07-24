import csv
from collections import Counter
from collections import defaultdict
from pathlib import Path


prevalence_file = Path(
    "data/texas_county_diabetes_prevalence.csv"
)

sites_file = Path(
    "data/"
    "texas_open_type_2_diabetes_trial_sites_with_counties.csv"
)

output_file = Path(
    "data/texas_county_trial_access.csv"
)


with prevalence_file.open(
    "r",
    encoding="utf-8",
) as file:
    prevalence_rows = list(
        csv.DictReader(file)
    )


with sites_file.open(
    "r",
    encoding="utf-8",
) as file:
    site_rows = list(
        csv.DictReader(file)
    )


site_counts = Counter()
studies_by_county = defaultdict(set)


for site in site_rows:
    county_fips = site["county_fips"].zfill(5)
    nct_id = site["nct_id"]

    site_counts[county_fips] += 1
    studies_by_county[county_fips].add(nct_id)


county_rows = []


for county in prevalence_rows:
    county_fips = county[
        "countyfips"
    ].zfill(5)

    population_text = county.get(
        "totalpopulation",
        "",
    )

    population = (
        int(float(population_text))
        if population_text
        else 0
    )

    prevalence_text = county.get(
        "diabetes_crudeprev",
        "",
    )

    prevalence = (
        float(prevalence_text)
        if prevalence_text
        else 0.0
    )

    open_site_count = site_counts[
        county_fips
    ]

    open_study_count = len(
        studies_by_county[county_fips]
    )

    if population > 0:
        sites_per_100k = (
            open_site_count
            / population
            * 100_000
        )
    else:
        sites_per_100k = 0.0

    row = {
        "county_fips": county_fips,
        "county_name": county[
            "countyname"
        ],
        "total_population": population,
        "diabetes_crude_prevalence": (
            prevalence
        ),
        "diabetes_crude_95ci": county.get(
            "diabetes_crude95ci",
            "",
        ),
        "diabetes_adjusted_prevalence": (
            county.get(
                "diabetes_adjprev",
                "",
            )
        ),
        "open_trial_sites": open_site_count,
        "open_unique_studies": (
            open_study_count
        ),
        "open_sites_per_100k": round(
            sites_per_100k,
            3,
        ),
        "has_open_trial_site": (
            "Yes"
            if open_site_count > 0
            else "No"
        ),
    }

    county_rows.append(row)


county_rows.sort(
    key=lambda row: (
        row["diabetes_crude_prevalence"]
    ),
    reverse=True,
)


fieldnames = [
    "county_fips",
    "county_name",
    "total_population",
    "diabetes_crude_prevalence",
    "diabetes_crude_95ci",
    "diabetes_adjusted_prevalence",
    "open_trial_sites",
    "open_unique_studies",
    "open_sites_per_100k",
    "has_open_trial_site",
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
    writer.writerows(county_rows)


counties_with_sites = sum(
    1
    for row in county_rows
    if row["open_trial_sites"] > 0
)

counties_without_sites = (
    len(county_rows) - counties_with_sites
)


high_prevalence_without_sites = [
    row
    for row in county_rows
    if row["open_trial_sites"] == 0
]


print(f"Counties analyzed: {len(county_rows)}")

print(
    "Counties with open trial sites: "
    f"{counties_with_sites}"
)

print(
    "Counties without open trial sites: "
    f"{counties_without_sites}"
)


print(
    "\nHighest-prevalence counties "
    "without open sites:"
)

for row in high_prevalence_without_sites[:10]:
    print(
        f"{row['county_name']}: "
        f"{row['diabetes_crude_prevalence']}%"
    )


print(f"\nSaved CSV to {output_file}.")