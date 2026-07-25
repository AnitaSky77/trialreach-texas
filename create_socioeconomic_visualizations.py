import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


input_file = Path(
    "data/texas_county_trial_access_socioeconomic.csv"
)

figures_folder = Path("reports/figures")
figures_folder.mkdir(parents=True, exist_ok=True)


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

    return statistics.mean(clean_values)


def median(values):
    clean_values = [
        value
        for value in values
        if value is not None
    ]

    return statistics.median(clean_values)


with input_file.open(
    "r",
    encoding="utf-8-sig",
) as file:
    rows = list(csv.DictReader(file))


for row in rows:
    row["income"] = to_number(
        row.get("median_household_income")
    )

    row["poverty"] = to_number(
        row.get("poverty_percent")
    )

    row["no_vehicle"] = to_number(
        row.get("households_without_vehicle_percent")
    )

    row["distance"] = to_number(
        row.get("nearest_trial_distance_miles")
    )

    row["open_sites"] = to_number(
        row.get("open_trial_sites")
    )


counties_with_sites = [
    row
    for row in rows
    if row["open_sites"] and row["open_sites"] > 0
]

counties_without_sites = [
    row
    for row in rows
    if not row["open_sites"] or row["open_sites"] == 0
]


income_values = []
distance_values = []

for row in rows:
    if row["income"] is not None and row["distance"] is not None:
        income_values.append(row["income"])
        distance_values.append(row["distance"])


plt.figure(figsize=(10, 7))

plt.scatter(
    income_values,
    distance_values,
    color="#2f6f9f",
    alpha=0.65,
    edgecolor="white",
    linewidth=0.4,
)

plt.title(
    "Household Income and Distance to an Open Type 2 Diabetes Trial Site"
)

plt.xlabel("Median household income, U.S. dollars")
plt.ylabel("Straight-line distance to nearest open site, miles")

plt.grid(
    axis="both",
    color="#d9d9d9",
    linewidth=0.7,
    alpha=0.7,
)

plt.tight_layout()

income_figure = (
    figures_folder
    / "income_vs_trial_distance.png"
)

plt.savefig(
    income_figure,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


group_names = [
    "Counties with\nopen sites",
    "Counties without\nopen sites",
]

income_comparison = [
    median(
        [
            row["income"]
            for row in counties_with_sites
        ]
    ),
    median(
        [
            row["income"]
            for row in counties_without_sites
        ]
    ),
]

poverty_comparison = [
    mean(
        [
            row["poverty"]
            for row in counties_with_sites
        ]
    ),
    mean(
        [
            row["poverty"]
            for row in counties_without_sites
        ]
    ),
]

vehicle_comparison = [
    mean(
        [
            row["no_vehicle"]
            for row in counties_with_sites
        ]
    ),
    mean(
        [
            row["no_vehicle"]
            for row in counties_without_sites
        ]
    ),
]


figure, axes = plt.subplots(
    1,
    3,
    figsize=(15, 6),
)

colors = [
    "#2f6f9f",
    "#c95b5b",
]


charts = [
    (
        income_comparison,
        "Median household income",
        "U.S. dollars",
        "${:,.0f}",
    ),
    (
        poverty_comparison,
        "Mean poverty rate",
        "Percent",
        "{:.1f}%",
    ),
    (
        vehicle_comparison,
        "Mean households without a vehicle",
        "Percent",
        "{:.1f}%",
    ),
]


for axis, chart in zip(axes, charts):
    values, title, ylabel, label_format = chart

    bars = axis.bar(
        group_names,
        values,
        color=colors,
        edgecolor="#333333",
        linewidth=0.6,
    )

    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.set_ylim(
        0,
        max(values) * 1.25,
    )

    axis.grid(
        axis="y",
        color="#d9d9d9",
        linewidth=0.7,
        alpha=0.7,
    )

    axis.set_axisbelow(True)

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            label_format.format(value),
            ha="center",
            va="bottom",
            fontsize=10,
        )


figure.suptitle(
    "Socioeconomic Characteristics by Open Trial-Site Availability",
    fontsize=15,
)

figure.tight_layout()

comparison_figure = (
    figures_folder
    / "socioeconomic_open_site_comparison.png"
)

figure.savefig(
    comparison_figure,
    dpi=300,
    bbox_inches="tight",
)

plt.close(figure)


print("Created two figures:")
print(income_figure)
print(comparison_figure)