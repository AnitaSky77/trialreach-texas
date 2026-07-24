import csv
from pathlib import Path


def read_csv(file_path):
    with file_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def percentile_rank(values, selected_value):
    values_at_or_below = sum(
        value <= selected_value
        for value in values
    )

    return (
        values_at_or_below
        / len(values)
        * 100
    )


data_folder = Path("data")

input_file = (
    data_folder
    / "texas_county_trial_access_with_distance.csv"
)

output_file = (
    data_folder
    / "texas_county_priority_scores.csv"
)

county_rows = read_csv(input_file)

prevalence_values = [
    float(row["diabetes_crude_prevalence"])
    for row in county_rows
]

distance_values = [
    float(row["nearest_trial_distance_miles"])
    for row in county_rows
]

scored_rows = []

for row in county_rows:
    prevalence = float(
        row["diabetes_crude_prevalence"]
    )

    distance = float(
        row["nearest_trial_distance_miles"]
    )

    prevalence_percentile = percentile_rank(
        prevalence_values,
        prevalence,
    )

    distance_percentile = percentile_rank(
        distance_values,
        distance,
    )

    priority_score = (
        prevalence_percentile
        + distance_percentile
    ) / 2

    has_open_site = row["has_open_trial_site"]

    if (
        prevalence_percentile >= 75
        and distance_percentile >= 75
        and has_open_site == "No"
    ):
        priority_group = "Highest priority"

    elif (
        priority_score >= 75
        and has_open_site == "No"
    ):
        priority_group = "High priority"

    elif (
        priority_score >= 50
        and has_open_site == "No"
    ):
        priority_group = "Moderate priority"

    else:
        priority_group = "Lower priority"

    scored_rows.append(
        {
            **row,
            "prevalence_percentile": round(
                prevalence_percentile,
                1,
            ),
            "distance_percentile": round(
                distance_percentile,
                1,
            ),
            "priority_score": round(
                priority_score,
                1,
            ),
            "priority_group": priority_group,
        }
    )

scored_rows.sort(
    key=lambda row: row["priority_score"],
    reverse=True,
)

for rank, row in enumerate(
    scored_rows,
    start=1,
):
    row["priority_rank"] = rank

fieldnames = [
    "priority_rank",
    *[
        field
        for field in scored_rows[0].keys()
        if field != "priority_rank"
    ],
]

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
    writer.writerows(scored_rows)

highest_priority = [
    row
    for row in scored_rows
    if row["priority_group"] == "Highest priority"
]

print(
    "Highest-priority counties: "
    f"{len(highest_priority)}"
)

print("\nTop 15 priority counties:")

for row in scored_rows[:15]:
    print(
        f"{row['priority_rank']}. "
        f"{row['county_name']}: "
        f"score {row['priority_score']}, "
        f"prevalence "
        f"{row['diabetes_crude_prevalence']}%, "
        f"distance "
        f"{row['nearest_trial_distance_miles']} miles"
    )

print(f"\nSaved CSV to {output_file}.")