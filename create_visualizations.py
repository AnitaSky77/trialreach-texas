import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def read_csv(file_path):
    with file_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


data_folder = Path("data")
figures_folder = Path("reports") / "figures"
figures_folder.mkdir(
    parents=True,
    exist_ok=True,
)

priority_file = (
    data_folder
    / "texas_county_priority_scores.csv"
)

trial_sites_file = (
    data_folder
    / "texas_open_type_2_diabetes_trial_sites_with_counties.csv"
)

county_rows = read_csv(priority_file)
trial_sites = read_csv(trial_sites_file)

for row in county_rows:
    row["priority_score_number"] = float(
        row["priority_score"]
    )
    row["prevalence_number"] = float(
        row["diabetes_crude_prevalence"]
    )
    row["distance_number"] = float(
        row["nearest_trial_distance_miles"]
    )
    row["latitude_number"] = float(
        row["county_latitude"]
    )
    row["longitude_number"] = float(
        row["county_longitude"]
    )


# Figure 1: Top 15 priority counties

top_15 = county_rows[:15]
top_15_reversed = list(reversed(top_15))

county_names = [
    row["county_name"]
    for row in top_15_reversed
]

priority_scores = [
    row["priority_score_number"]
    for row in top_15_reversed
]

fig, ax = plt.subplots(
    figsize=(10, 7),
)

bars = ax.barh(
    county_names,
    priority_scores,
    color="#C44E52",
)

ax.set_title(
    "Top 15 Texas Counties by Trial-Access Priority Score"
)

ax.set_xlabel(
    "Priority score, 0 to 100"
)

ax.set_xlim(0, 105)

ax.grid(
    axis="x",
    alpha=0.25,
)

for bar, score in zip(
    bars,
    priority_scores,
):
    ax.text(
        score + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{score:.1f}",
        va="center",
    )

fig.tight_layout()

bar_chart_file = (
    figures_folder
    / "top_15_priority_counties.png"
)

fig.savefig(
    bar_chart_file,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


# Figure 2: Prevalence and distance

fig, ax = plt.subplots(
    figsize=(10, 7),
)

lower_priority = [
    row
    for row in county_rows
    if row["priority_group"] != "Highest priority"
]

highest_priority = [
    row
    for row in county_rows
    if row["priority_group"] == "Highest priority"
]

ax.scatter(
    [
        row["distance_number"]
        for row in lower_priority
    ],
    [
        row["prevalence_number"]
        for row in lower_priority
    ],
    color="#4C78A8",
    alpha=0.55,
    label="Other counties",
)

ax.scatter(
    [
        row["distance_number"]
        for row in highest_priority
    ],
    [
        row["prevalence_number"]
        for row in highest_priority
    ],
    color="#E45756",
    edgecolor="black",
    linewidth=0.5,
    label="Highest priority",
)

for row in county_rows[:5]:
    ax.annotate(
        row["county_name"],
        (
            row["distance_number"],
            row["prevalence_number"],
        ),
        xytext=(5, 5),
        textcoords="offset points",
    )

ax.set_title(
    "Diabetes Prevalence and Distance to an Open Trial Site"
)

ax.set_xlabel(
    "Straight-line distance to nearest open site, miles"
)

ax.set_ylabel(
    "Adult diagnosed diabetes prevalence, percent"
)

ax.grid(alpha=0.25)
ax.legend()

fig.tight_layout()

scatter_file = (
    figures_folder
    / "prevalence_vs_trial_distance.png"
)

fig.savefig(
    scatter_file,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


# Figure 3: Geographic distribution

fig, ax = plt.subplots(
    figsize=(11, 8),
)

county_plot = ax.scatter(
    [
        row["longitude_number"]
        for row in county_rows
    ],
    [
        row["latitude_number"]
        for row in county_rows
    ],
    c=[
        row["priority_score_number"]
        for row in county_rows
    ],
    cmap="YlOrRd",
    s=45,
    alpha=0.85,
    edgecolor="gray",
    linewidth=0.3,
)

valid_sites = [
    site
    for site in trial_sites
    if site["latitude"]
    and site["longitude"]
]

ax.scatter(
    [
        float(site["longitude"])
        for site in valid_sites
    ],
    [
        float(site["latitude"])
        for site in valid_sites
    ],
    marker="^",
    color="#222222",
    s=18,
    alpha=0.55,
    label="Open trial site",
)

for row in county_rows[:5]:
    ax.annotate(
        row["county_name"],
        (
            row["longitude_number"],
            row["latitude_number"],
        ),
        xytext=(5, 5),
        textcoords="offset points",
    )

colorbar = fig.colorbar(
    county_plot,
    ax=ax,
    shrink=0.8,
)

colorbar.set_label(
    "Priority score"
)

ax.set_title(
    "Geographic Distribution of Trial-Access Priority"
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend(loc="lower left")
ax.grid(alpha=0.2)

fig.tight_layout()

geographic_file = (
    figures_folder
    / "texas_trial_access_geographic_distribution.png"
)

fig.savefig(
    geographic_file,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


print("Created three figures:")
print(bar_chart_file)
print(scatter_file)
print(geographic_file)