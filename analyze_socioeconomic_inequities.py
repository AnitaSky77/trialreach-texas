import csv
import math
import statistics
from pathlib import Path


input_file = Path(
    "data/texas_county_trial_access_socioeconomic.csv"
)

output_file = Path(
    "data/texas_socioeconomic_analysis_summary.csv"
)


def to_number(value):
    try:
        number = float(value)

        if number < 0:
            return None

        return number
    except (TypeError, ValueError):
        return None


def mean(values):
    clean_values = [
        value
        for value in values
        if value is not None
    ]

    if not clean_values:
        return None

    return statistics.mean(clean_values)


def median(values):
    clean_values = [
        value
        for value in values
        if value is not None
    ]

    if not clean_values:
        return None

    return statistics.median(clean_values)


def correlation(x_values, y_values):
    pairs = [
        (x, y)
        for x, y in zip(x_values, y_values)
        if x is not None and y is not None
    ]

    if len(pairs) < 2:
        return None

    x_clean = [pair[0] for pair in pairs]
    y_clean = [pair[1] for pair in pairs]

    x_mean = statistics.mean(x_clean)
    y_mean = statistics.mean(y_clean)

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in pairs
    )

    x_squared = sum(
        (x - x_mean) ** 2
        for x in x_clean
    )

    y_squared = sum(
        (y - y_mean) ** 2
        for y in y_clean
    )

    denominator = math.sqrt(
        x_squared * y_squared
    )

    if denominator == 0:
        return None

    return numerator / denominator


def format_number(value):
    if value is None:
        return "NA"

    return f"{value:.2f}"


with input_file.open(
    "r",
    encoding="utf-8-sig",
) as file:
    rows = list(csv.DictReader(file))


for row in rows:
    row["open_trial_sites_number"] = to_number(
        row.get("open_trial_sites")
    )

    row["distance_number"] = to_number(
        row.get("nearest_trial_distance_miles")
    )

    row["income_number"] = to_number(
        row.get("median_household_income")
    )

    row["poverty_number"] = to_number(
        row.get("poverty_percent")
    )

    row["no_vehicle_number"] = to_number(
        row.get("households_without_vehicle_percent")
    )


counties_with_sites = [
    row
    for row in rows
    if row["open_trial_sites_number"]
    and row["open_trial_sites_number"] > 0
]

counties_without_sites = [
    row
    for row in rows
    if not row["open_trial_sites_number"]
    or row["open_trial_sites_number"] == 0
]


summary_rows = []


def add_summary(group_name, group_rows):
    summary_rows.append(
        {
            "group": group_name,
            "county_count": len(group_rows),
            "median_household_income": format_number(
                median(
                    [
                        row["income_number"]
                        for row in group_rows
                    ]
                )
            ),
            "mean_poverty_rate": format_number(
                mean(
                    [
                        row["poverty_number"]
                        for row in group_rows
                    ]
                )
            ),
            "mean_households_without_vehicle_rate": (
                format_number(
                    mean(
                        [
                            row["no_vehicle_number"]
                            for row in group_rows
                        ]
                    )
                )
            ),
            "median_distance_to_open_site": (
                format_number(
                    median(
                        [
                            row["distance_number"]
                            for row in group_rows
                        ]
                    )
                )
            ),
        }
    )


add_summary("All counties", rows)
add_summary(
    "Counties with open trial sites",
    counties_with_sites,
)
add_summary(
    "Counties without open trial sites",
    counties_without_sites,
)


fieldnames = [
    "group",
    "county_count",
    "median_household_income",
    "mean_poverty_rate",
    "mean_households_without_vehicle_rate",
    "median_distance_to_open_site",
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
    writer.writerows(summary_rows)


income_distance_correlation = correlation(
    [
        row["income_number"]
        for row in rows
    ],
    [
        row["distance_number"]
        for row in rows
    ],
)

poverty_distance_correlation = correlation(
    [
        row["poverty_number"]
        for row in rows
    ],
    [
        row["distance_number"]
        for row in rows
    ],
)

vehicle_distance_correlation = correlation(
    [
        row["no_vehicle_number"]
        for row in rows
    ],
    [
        row["distance_number"]
        for row in rows
    ],
)


print(f"Counties analyzed: {len(rows)}")
print(
    "Counties with open trial sites: "
    f"{len(counties_with_sites)}"
)
print(
    "Counties without open trial sites: "
    f"{len(counties_without_sites)}"
)

print("\nGroup comparison:")

for summary in summary_rows:
    print(f"\n{summary['group']}")
    print(
        "Median household income: "
        f"${summary['median_household_income']}"
    )
    print(
        "Mean poverty rate: "
        f"{summary['mean_poverty_rate']}%"
    )
    print(
        "Mean households without vehicle: "
        f"{summary['mean_households_without_vehicle_rate']}%"
    )
    print(
        "Median distance to open site: "
        f"{summary['median_distance_to_open_site']} miles"
    )

print("\nCorrelations with distance:")

print(
    "Median household income: "
    f"{format_number(income_distance_correlation)}"
)

print(
    "Poverty rate: "
    f"{format_number(poverty_distance_correlation)}"
)

print(
    "Households without a vehicle: "
    f"{format_number(vehicle_distance_correlation)}"
)

print(f"\nSaved summary to {output_file}.")