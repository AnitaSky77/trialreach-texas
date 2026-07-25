import csv
from pathlib import Path


INPUT_FILE = Path(
    "data/texas_county_trial_access_with_distance.csv"
)

OUTPUT_FILE = Path(
    "data/texas_sensitivity_analysis.csv"
)


SCENARIOS = [
    {
        "name": "Baseline",
        "prevalence_weight": 0.50,
        "distance_weight": 0.50,
        "threshold": 75,
    },
    {
        "name": "Prevalence emphasis",
        "prevalence_weight": 0.70,
        "distance_weight": 0.30,
        "threshold": 75,
    },
    {
        "name": "Distance emphasis",
        "prevalence_weight": 0.30,
        "distance_weight": 0.70,
        "threshold": 75,
    },
    {
        "name": "Lower threshold",
        "prevalence_weight": 0.50,
        "distance_weight": 0.50,
        "threshold": 70,
    },
    {
        "name": "Higher threshold",
        "prevalence_weight": 0.50,
        "distance_weight": 0.50,
        "threshold": 80,
    },
]


def percentile_rank(value, values):
    lower_values = [
        item
        for item in values
        if item < value
    ]

    if len(values) <= 1:
        return 100.0

    return (
        len(lower_values)
        / (len(values) - 1)
        * 100
    )


with INPUT_FILE.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:
    reader = csv.DictReader(file)
    rows = list(reader)


valid_rows = []

for row in rows:
    try:
        prevalence = float(
            row["diabetes_crude_prevalence"]
        )

        distance = float(
            row["nearest_trial_distance_miles"]
        )

    except (ValueError, TypeError):
        continue

    row["prevalence_value"] = prevalence
    row["distance_value"] = distance

    valid_rows.append(row)


prevalence_values = [
    row["prevalence_value"]
    for row in valid_rows
]

distance_values = [
    row["distance_value"]
    for row in valid_rows
]


for row in valid_rows:
    row["prevalence_percentile"] = percentile_rank(
        row["prevalence_value"],
        prevalence_values,
    )

    row["distance_percentile"] = percentile_rank(
        row["distance_value"],
        distance_values,
    )


output_rows = []
scenario_top_counties = {}


for scenario in SCENARIOS:
    eligible_rows = []

    for row in valid_rows:
        has_open_site = (
            row["has_open_trial_site"]
            .strip()
            .lower()
            == "yes"
        )

        prevalence_percentile = row[
            "prevalence_percentile"
        ]

        distance_percentile = row[
            "distance_percentile"
        ]

        if has_open_site:
            continue

        if (
            prevalence_percentile
            < scenario["threshold"]
        ):
            continue

        if (
            distance_percentile
            < scenario["threshold"]
        ):
            continue

        score = (
            prevalence_percentile
            * scenario["prevalence_weight"]
            + distance_percentile
            * scenario["distance_weight"]
        )

        eligible_rows.append(
            {
                "scenario": scenario["name"],
                "county_fips": row["county_fips"],
                "county_name": row["county_name"],
                "diabetes_prevalence": (
                    row["prevalence_value"]
                ),
                "nearest_trial_distance_miles": (
                    row["distance_value"]
                ),
                "prevalence_percentile": round(
                    prevalence_percentile,
                    1,
                ),
                "distance_percentile": round(
                    distance_percentile,
                    1,
                ),
                "priority_score": round(score, 1),
            }
        )

    eligible_rows.sort(
        key=lambda item: item["priority_score"],
        reverse=True,
    )

    top_rows = eligible_rows[:15]

    scenario_top_counties[
        scenario["name"]
    ] = {
        row["county_name"]
        for row in top_rows
    }

    for rank, row in enumerate(
        top_rows,
        start=1,
    ):
        row["rank"] = rank
        output_rows.append(row)


fieldnames = [
    "scenario",
    "rank",
    "county_fips",
    "county_name",
    "diabetes_prevalence",
    "nearest_trial_distance_miles",
    "prevalence_percentile",
    "distance_percentile",
    "priority_score",
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
    writer.writerows(output_rows)


baseline_counties = scenario_top_counties[
    "Baseline"
]


print("Sensitivity analysis completed.")

for scenario in SCENARIOS:
    name = scenario["name"]
    counties = scenario_top_counties[name]

    overlap = len(
        baseline_counties.intersection(counties)
    )

    print(
        f"{name}: "
        f"{len(counties)} counties, "
        f"{overlap} also in the baseline top 15"
    )


print(f"\nSaved results to {OUTPUT_FILE}.")