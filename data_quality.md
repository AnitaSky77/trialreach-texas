# Data Quality Report

Data collection date: July 24, 2026

## Purpose

This document records the main data checks, missing records, assumptions, and limitations for TrialReach Texas.

## ClinicalTrials.gov data

### Study records

The ClinicalTrials.gov condition and location search returned 1,231 unique study records linked to Type 2 diabetes and Texas.

The study-status counts were:

- 954 completed
- 107 terminated
- 78 recruiting
- 44 active but not recruiting
- 18 withdrawn
- 13 unknown
- 10 not yet recruiting
- 4 enrolling by invitation
- 3 suspended

All 1,231 records had a unique NCT identifier.

Source: https://clinicaltrials.gov/data-api/api

### Texas trial-site records

The study records contained 5,656 deduplicated Texas trial-site entries.

Coordinate results:

- 5,613 sites had latitude and longitude
- 43 sites lacked coordinates
- Coordinate completeness was 99.2%

The script removed duplicate site rows using the following fields:

- NCT identifier
- Facility
- City
- ZIP code
- Latitude
- Longitude

### Open-site definition

The analysis defined an open site as a facility explicitly labeled:

- `RECRUITING`
- `NOT_YET_RECRUITING`

Of the 5,656 Texas site records, 5,357 had a blank facility-status field. These records were excluded from the open-site analysis.

The final open-site dataset contained:

- 292 explicitly open site records
- 260 recruiting site records
- 32 not-yet-recruiting site records
- 81 unique studies
- 292 sites with coordinates
- 0 open sites without coordinates

The 292-site result should be interpreted as confirmed open sites under the project definition. It does not represent every site potentially accepting participants.

A study-level recruiting status does not confirm recruitment at each listed facility. The project therefore used the facility-level status field.

### Coordinate duplication

The 292 open-site records contained 56 unique coordinate pairs.

Multiple records shared coordinates. The source data do not confirm whether each coordinate represents an exact facility entrance.

Shared coordinates might represent sites located in the same city, nearby facilities, or approximate location data.

## County assignment

The Census TIGERweb point query assigned all 292 explicitly open sites to Texas counties.

Results:

- Total open sites: 292
- Matched sites: 292
- Unmatched sites: 0
- County-assignment coverage: 100%
- Unique counties with open sites: 31
- Unique coordinate lookups: 56

Source: https://tigerweb.geo.census.gov/

## CDC PLACES data

The project used the 2025 CDC PLACES county release.

Source: https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb

The Texas query returned 253 county records.

The CDC records had:

- 253 unique county FIPS codes
- 0 missing county FIPS codes
- 0 missing population values
- 0 missing crude diabetes-prevalence values
- Crude prevalence values ranging from 9.0% to 23.4%

Texas contains 254 counties. A comparison with the Census TIGERweb county list identified one missing county:

```text
Loving County
FIPS 48301
```

Loving County was not assigned a diabetes-prevalence estimate. No value was imputed.

The final prevalence, distance, and priority analyses therefore include 253 counties.

## County coordinates

The Census TIGERweb query returned:

- 254 Texas county records
- 254 unique county FIPS codes
- 254 county-center coordinate pairs
- 0 missing coordinate pairs

The project joined county datasets using five-digit county FIPS codes.

Examples:

```text
Harris County: 48201
Travis County: 48453
El Paso County: 48141
```

FIPS matching reduces errors caused by differences in county-name formatting.

## County access dataset

The final county-access dataset contained:

- 253 counties
- 31 counties with at least one explicitly open trial site
- 222 counties without an explicitly open trial site
- 292 open site records
- 87.7% of analyzed counties without an explicitly open site

The site counts represent site records, not unique physical buildings. Multiple studies might list the same facility or coordinate.

## Distance measure

Distance was calculated from each county geographic center to the nearest explicitly open trial-site coordinate.

The calculation used the Haversine formula and an Earth radius of 3,958.8 miles.

Verified results:

- Counties analyzed: 253
- Median distance: 46.6 miles
- Counties over 50 miles away: 117
- Counties over 100 miles away: 25
- Longest estimated distance: 234.5 miles
- County with the longest estimated distance: Brewster County

The distance represents straight-line geographic distance. It does not represent:

- Driving distance
- Driving time
- Public-transit access
- Travel cost
- Within-county population distribution

County-center distances are less precise for large counties and counties where residents are concentrated far from the geographic center.

## Priority score

The priority score gives equal weight to:

- Diabetes-prevalence percentile
- Distance-to-nearest-open-site percentile

The formula is:

```text
Priority score =
(prevalence percentile + distance percentile) / 2
```

A county enters the highest-priority group when:

- Its prevalence percentile is at least 75
- Its distance percentile is at least 75
- It has no explicitly open trial site

Verified results:

- 253 counties received a priority score
- 20 counties met the highest-priority definition
- All saved priority scores matched an independent recalculation

The five leading counties were:

| Rank | County | Priority score | Diabetes prevalence | Distance |
|---:|---|---:|---:|---:|
| 1 | Presidio | 99.0 | 22.2% | 180.4 miles |
| 2 | Jeff Davis | 98.0 | 21.2% | 156.3 miles |
| 3 | Culberson | 95.1 | 19.3% | 117.9 miles |
| 4 | Reeves | 94.5 | 17.6% | 167.3 miles |
| 5 | Cottle | 92.3 | 18.8% | 96.8 miles |

The score is a descriptive screening measure. It is not a validated clinical index and does not estimate causal impact.

Distance values were rounded to one decimal place before percentile ranking. This creates some tied distance ranks.

## Visualization checks

The project generated three figures:

- Top 15 priority counties
- Diabetes prevalence versus trial distance
- Geographic distribution of priority scores and trial sites

The figures contain:

- Labeled titles
- Labeled axes
- Units
- Legends where needed
- Priority-county annotations
- Zero-based bar-chart scaling

The geographic figure uses county-center points. It is not a county-boundary choropleth map.

## Reproducibility checks

The completed pipeline produced:

- 1,231 unique study records
- 5,656 deduplicated Texas site records
- 292 explicitly open site records
- 253 counties with CDC prevalence estimates
- 254 Census county-center records
- 253 counties in the final analysis
- 20 highest-priority counties
- Three visualization files

The Python scripts regenerate the derived CSV files and figures from the source data.

## Main limitations

- Study sponsors and investigators maintain ClinicalTrials.gov records.
- Recruitment status might change after the data-collection date.
- Facility status was blank for 5,357 site records.
- A recruiting label does not guarantee active enrollment when a person contacts a site.
- Site coordinates might represent approximate locations.
- Multiple site records might share a facility or coordinate.
- CDC PLACES values are modeled estimates.
- Loving County was absent from the CDC extract.
- County averages hide variation within counties.
- Straight-line distance understates road travel in some areas.
- Geographic county centers do not represent the residential location of every county resident.
- The analysis does not include individual patient data.
- The analysis does not measure clinical outcomes.
- The analysis does not establish causation.

## Planned sensitivity checks

Future sensitivity analysis will compare:

- Recruiting-only sites against recruiting plus not-yet-recruiting sites
- Crude prevalence against age-adjusted prevalence
- Equal weighting against alternative score weights
- Top 25%, top 20%, and top 10% priority thresholds
- Straight-line distance against driving distance or travel time

## Sharing assessment

The analysis is suitable for sharing as a descriptive student research project when the stated definitions and limitations accompany the findings.

The results should not be presented as evidence of healthcare-program effectiveness, patient outcomes, or causal impact.