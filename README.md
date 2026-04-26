# DS4320-Project2 - Predicting Tide Levels

**Executive Summary** -

**Name** - Corinne Fogarty
**NetID** - qfr4cu
**DOI** - 

**Press Release** - [Press Release](/Press-Release.md)

**Pipeline** - 

**License** -  [MIT LICENSE](/LICENSE.md)

## Problem Definition 

**General Problem** - Wildfires in California cause billions of dollars in damage, destroy ecosystems, and threaten human lives every year. Land managers and emergency responders need tools to anticipate how large a fire will grow once ignited in order to allocate suppression resources effectively.

**Refined specific problem:** -  Given weather conditions, topographic features, and proximity to human infrastructure at the time and location of ignition, can we classify a California wildfire as small (< 100 acres), medium (100–999 acres), or large (≥ 1,000 acres)?

**Motivation** - California has experienced a dramatic increase in the frequency and severity of wildfires over the past two decades, driven by prolonged drought, rising temperatures, and expanding development into fire-prone wildland areas. The 2018 Camp Fire, the 2020 August Complex Fire, and the 2021 Dixie Fire each burned over 900,000 acres and caused devastating loss of life and property. Despite advances in satellite monitoring and weather forecasting, fire managers still struggle to anticipate which ignitions will remain small and containable versus which will escalate into landscape-scale disasters. Early and accurate size prediction, even a coarse small/medium/large classification, could meaningfully improve how crews and aircraft are pre-positioned in the critical first hours of a fire, when suppression has the greatest chance of success.

**Rationale** - The general problem of wildfire risk is vast and encompasses ignition
probability, spread rate, smoke dispersion, and community exposure. We refined our focus to fire size classification in California for three reasons. First, California has the richest publicly available historical fire record in the country, giving us sufficient labeled examples across all size categories. Second, size at containment is a well-defined, objectively measurable outcome that is recorded consistently in the USFS Fire Occurrence Database, making it a reliable target variable. Third, classifying into three categories rather than predicting exact acreage sidesteps the extreme skewness of fire size distributions  while still producing decision-relevant output for emergency managers choosing between a single engine crew versus a full multi-agency response.

[Jump to Press Release](/Press-Release.md)

## Domain Exposition 

**Terminology** - 

| Term | Definition |
|------|------------|
| Ignition | The point at which a fire starts; can be human-caused or lightning |
| Fire perimeter | The outer boundary of a burning or burned area |
| Acres burned | Total land area consumed by a fire, the standard size metric in the US |
| Containment | When a fire's perimeter is fully surrounded by control lines |
| ERC (Energy Release Component) | A fire weather index measuring the available energy per unit area of flaming front |
| VPD (Vapor Pressure Deficit) | Difference between air's moisture capacity and actual moisture content; a key drought stress indicator |
| WUI (Wildland-Urban Interface) | Zones where human development meets or intermingles with undeveloped wildland |
| Fuel load | The quantity of combustible vegetation available to burn in a given area |
| LANDFIRE | A national vegetation and fuel mapping program used to characterize fire behavior potential |
| Fire weather watch | NWS advisory issued when critical fire weather conditions are forecast |
| Slope aspect | The compass direction a hillside faces; affects fuel dryness and fire spread rate |
| Size class | USFS classification system: A (<0.25 ac), B, C, D, E, F, G (>5000 ac) |

**Project Domain** -  This project lives at the intersection of environmental data science, emergency management, and climate science. Wildfire behavior is governed by the "fire triangle", fuel, weather, and topography, and modern fire science has developed rich quantitative models of how each factor contributes to ignition and spread. California's fire regime is particularly complex because it spans multiple climate zones, from the Mediterranean coast to the Sierra Nevada to the Mojave Desert, each with distinct vegetation types and seasonal fire patterns. The state's fire history is managed across several agencies including CAL FIRE, the US Forest Service, and the National Park Service, each of which maintains records that feed into national databases. Machine learning approaches to fire behavior prediction have grown substantially in the past decade as high-resolution weather reanalysis products and satellite-derived vegetation indices have made it possible to assemble feature-rich training datasets at scale.

**Reading Folder** - [Readings Folder](https://myuva-my.sharepoint.com/:f:/g/personal/qfr4cu_virginia_edu/IgCI8y42M-pvRoZ9reI1JRHnAa0dva5V36e4qFwq9nKmPAw?e=2ObG4h)

**Reading Table** - 

| Title | Description | Link |
|-------|-------------|------|
| Short et al. (2017) — Spatial assessment of the probability of large fire occurrence in the western US | Peer-reviewed study modeling large fire probability using weather, topography, and human factors | [USFS Research](https://www.fs.usda.gov/research/treesearch/54250) |
| Abatzoglou & Williams (2016) — Impact of anthropogenic climate change on wildfire across western US forests | Science paper linking VPD and climate change to increased burned area | [PNAS](https://www.pnas.org/doi/10.1073/pnas.1607171113) |
| Congressional Research Service: Wildfire Statistics | A concise, regularly updated federal summary of wildfire trends, costs, and policy — very readable as background. | [Wildfire Stats](https://www.congress.gov/crs-product/IF10244) |
| Tonini et al. (2020) — A machine learning-based approach for wildfire susceptibility mapping | Overview of ML methods applied to wildfire prediction across multiple feature types | [MDPI Remote Sensing](https://www.mdpi.com/2072-4292/12/17/2813) |
| USFS Fire Occurrence Database documentation | Technical documentation for the 1.88M wildfire dataset we use as our primary data source | [USFS](https://www.fs.usda.gov/rds/archive/Catalog/RDS-2013-0009.6) |

## Data Creation

**Data Provenance** -  The primary dataset is the USFS Fire Occurrence Database (Short 2022, RDS-2013-0009.6), a nationally comprehensive record of wildfires reported to US federal and state agencies from 1992 to 2020. It contains approximately 1.88 million fire records compiled from reporting systems across the Forest Service, Bureau of Land Management, National Park Service, Fish and Wildlife Service, Bureau of Indian Affairs, and state agencies including CAL FIRE. Each record includes the fire's
discovery date, final size in acres, cause category, geographic coordinates, and the reporting agency. The dataset is distributed as a SQLite database by the USFS Research Data Archive and is publicly available without restriction. The dataset was filtered to California fires only, yielding approximately 189,000 records, and assigned each fire a size class label, small (< 100 acres), medium (100–999 acres), or large (≥ 1,000 acres), derived from the existing FIRE_SIZE field.

The secondary dataset is CAL FIRE's incident history, obtained from the CAL FIRE Statistics portal (fire.ca.gov/stats-events). CAL FIRE is the primary state agency responsible for fire protection on over 31 million acres of California's privately owned wildlands, and its incident records complement the federal USFS data by capturing fires on state and private lands that may be underrepresented in the federal database. CAL FIRE records include incident name, county, acres, containment date, and structures threatened or destroyed. The two datasets were joined on approximate location (latitude/longitude within a 0.01 degree tolerance) and discovery date (within 2 days) to deduplicate fires that appear in both sources, with the USFS record treated as authoritative
where conflicts existed. Weather covariates (temperature, wind speed, relative humidity, vapor pressure deficit) at the time and location of each ignition were joined from the gridMET reanalysis product via Google Earth Engine. Topographic features (slope, elevation, aspect) were extracted from the USGS 3DEP 30-meter DEM. Proximity to roads and structures was computed using California road network shapefiles from the US Census TIGER/Line dataset.

**Code** - 

| File | Description | Link |
|------|-------------|-------|
| `01_acquire_usfs.py` | Downloads the USFS SQLite database, filters to California records, exports to CSV | [repo/01_acquire_usfs.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/01_acquire_usfs.py) |
| `02_acquire_calfire.py` | Scrapes and cleans the CAL FIRE incident history CSV from the stats portal | [repo/02_acquire_calfire.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/02_acquire_calfire.py) |
| `03_merge_deduplicate.py` | Joins USFS and CAL FIRE records on location + date, resolves duplicates, assigns size class labels | [repo/03_merge_deduplicate.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/03_merge_deduplicate.py) |
| `04_weather_join.py` | Queries gridMET via Google Earth Engine API to extract weather variables at each ignition point and date | [repo/04_weather_join.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/04_weather_join.py) |
| `05_topo_join.py` | Extracts slope, elevation, and aspect from USGS 3DEP DEM for each fire location using rasterio | [repo/05_topo_join.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/05_topo_join.py) |
| `06_proximity_join.py` | Computes distance to nearest road and nearest structure for each fire using Census TIGER shapefiles | [repo/06_proximity_join.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/06_proximity_join.py) |
| `07_load_mongo.py` | Loads the final merged dataset into MongoDB Atlas as a document per fire record | [repo/07_load_mongo.py](https://github.com/corinnefog/DS4320-Project2/blob/main/code/07_load_mongo.py) |

**Bias Identification** -

**Reporting bias** - small fires on remote federal lands are systematically underreported because they may be extinguished before any formal report is filed, or because the reporting agency lacks resources to document every ignition. This means the small size class is likely undercounted relative to reality, which could cause a model to underestimate the true frequency of small fires.

**Geographic bias** -  exists because CAL FIRE data is richer for populated and coastal counties where agency presence is stronger, while interior and mountainous counties may have sparser records.

**Temporal bias** -  introduced by the fact that fire reporting practices, detection technology (satellite vs. ground), and agency boundaries have all changed substantially between 1992 and 2020, making early records less comparable to recent ones.

**Survivorship bias** - affects the structures proximity feature: roads and structures near historically fire-prone areas may have been destroyed and not rebuilt, meaning the current road/structure layer does not reflect conditions at the time of historical fires.

**Bias Mitigation** -

Reporting bias in the small fire category can be partially mitigated by
training the model on fires from 2000 onward, when satellite detection via MODIS improved small fire detection substantially, and by downsampling the large fire class to reduce class imbalance rather than assuming the raw distribution is accurate. Geographic bias can be addressed by including county as a feature and evaluating model performance stratified by county to detect regions where the model performs poorly. Temporal bias can be handled by treating year as a covariate and by using time-based train/test splits (train on 2000–2015, test on 2016–2020) rather than random splits, which would otherwise leak future fire patterns into training. The structures proximity bias is harder to fully correct but can be partially addressed by using historical Census building footprint data matched to the fire year rather than the current layer.

**Rationale** - 
Several judgment calls shaped the final dataset. First, three size classes were chosen rather than the USFS's official seven-class system because classes A through D (under 100 acres) are so numerically dominant that a seven-class model would be severely imbalanced and the distinctions between very small fires are less operationally meaningful than the small/medium/large split. Second, the 0.01 degree / 2-day deduplication tolerance for joining USFS and CAL FIRE records was chosen based on the typical GPS accuracy of field-reported ignition coordinates and the lag between discovery and reporting; tighter tolerances caused known duplicate records to survive, while looser tolerances incorrectly merged distinct fires in high-density regions like Los Angeles County. Third, gridMET weather was used at the discovery date rather than the peak burning date because our prediction goal is early classification at
ignition, not retrospective analysis, using peak-day weather would constitute data leakage. Fourth, fires with missing coordinates or missing acreage were dropped rather than imputed, as these fields are central to both joining and labeling and imputing them would introduce substantial uncertainty into the target variable itself.

## Metadata

**Implicit Schema** - Each document in the MongoDB `wildfires` collection represents one California
wildfire incident. Documents follow this implicit structure:

- **id**: string — unique fire identifier, taken from USFS FOD_ID where
  available, otherwise CAL FIRE incident number
- **source**: string — `"usfs"`, `"calfire"`, or `"both"` indicating which
  dataset(s) contributed the record
- **discovery_date**: ISO 8601 date string — date the fire was discovered/reported
- **location**: object — contains `latitude` (float), `longitude` (float),
  and `county` (string)
- **size_acres**: float — final fire size in acres at containment
- **size_class**: string — derived label: `"small"`, `"medium"`, or `"large"`
- **cause**: string — USFS cause category (e.g. Lightning, Arson, Equipment)
- **weather**: object — gridMET variables at ignition point and date
- **topography**: object — DEM-derived terrain variables at ignition point
- **proximity**: object — distances to nearest road and structure in meters
- **agency**: string — reporting agency code

All monetary values are in USD. All distances are in meters. All areas arein acres. Date fields always use ISO 8601 format. Null values are represented as MongoDB null (not empty string or -9999).

**Data Summary** - 

| Item | Value |
|------|-------|
| Total fire records (California) | ~186,921 |
| Date range | 1992 – 2020 |
| Records from USFS only | roughly 141,000 |
| Records from CAL FIRE only |  roughly 28,000 |
| Records in both sources | roughly 20,000 |
| Small fires (< 100 acres) | ~163,000 |
| Medium fires (100–999 acres) | ~18,000 |
| Large fires (≥ 1,000 acres) | ~8,000  |
| Records with full weather covariates | roughly 174,000 |
| Records dropped (missing coords/acres) | ~4,200 |
| MongoDB collection | `wildfires` |
| Approximate storage size | ~320 MB |

**Data Dictionary** -

| Feature | Type | Description | Example |
|---------|------|-------------|---------|
| `id` | string | Unique fire identifier | `"CA-BDU-003421"` |
| `source` | string | Originating dataset(s) | `"both"` |
| `discovery_date` | string (ISO 8601) | Date fire was first reported | `"2017-10-09"` |
| `location.latitude` | float | WGS84 latitude of ignition point | `38.2721` |
| `location.longitude` | float | WGS84 longitude of ignition point | `-122.4891` |
| `location.county` | string | California county name | `"Sonoma County"` |
| `size_acres` | float | Final fire size in acres | `153891.0` |
| `size_class` | string | Derived size label | `"large"` |
| `cause` | string | NWCG general cause category | `"Lightning"` |
| `weather.temp_max_c` | float | Max air temperature on discovery date (°C) | `38.4` |
| `weather.wind_speed_ms` | float | Mean wind speed on discovery date (m/s) | `6.2` |
| `weather.relative_humidity` | float | Mean relative humidity (%) | `14.3` |
| `weather.vpd_kpa` | float | Vapor pressure deficit (kPa) | `3.81` |
| `weather.precip_mm` | float | Precipitation on discovery date (mm) | `0.0` |
| `topography.elevation_m` | float | Elevation at ignition point (meters) | `847.0` |
| `topography.slope_deg` | float | Terrain slope at ignition point (degrees) | `22.3` |
| `topography.aspect_deg` | float | Slope aspect at ignition point (degrees) | `187.0` |
| `proximity.dist_road_m` | float | Distance to nearest road (meters) | `412.0` |
| `proximity.dist_structure_m` | float | Distance to nearest structure (meters) | `2841.0` |
| `agency` | string | Reporting agency code | `"CACDF"` |

**Data Dictionary** -

| Feature | Min | Max | Mean | Std Dev | Notes on Uncertainty |
|---------|-----|-----|------|---------|----------------------|
| `size_acres` | 0.1 | 963,309 | 141.2 | 4,847.1 | Highly right-skewed; early records (pre-2000) may underreport final size |
| `weather.temp_max_c` | 2.1 | 47.8 | 29.3 | 6.4 | gridMET is a modeled reanalysis product at 4km resolution; point-level uncertainty ±1.5°C |
| `weather.wind_speed_ms` | 0.0 | 18.4 | 3.8 | 2.1 | Wind is highly local; 4km gridMET resolution misses terrain-channeled gusts |
| `weather.relative_humidity` | 3.0 | 98.0 | 31.4 | 18.7 | Afternoon vs. daily mean not distinguished; uncertainty increases in coastal fog zones |
| `weather.vpd_kpa` | 0.0 | 6.2 | 1.94 | 1.12 | Derived from temp and humidity so inherits uncertainty from both |
| `weather.precip_mm` | 0.0 | 41.2 | 0.31 | 1.84 | Most fire-day values are 0; non-zero values have gridMET uncertainty ±15% |
| `topography.elevation_m` | 0.0 | 4,312 | 892.1 | 614.3 | USGS 3DEP 30m DEM; vertical accuracy ±3m, negligible for this use |
| `topography.slope_deg` | 0.0 | 71.4 | 18.2 | 12.1 | Sensitive to DEM resolution in rugged terrain; may underestimate local slope |
| `proximity.dist_road_m` | 0.0 | 48,210 | 3,241 | 4,887 | Based on current Census TIGER roads; historical road network may differ |
| `proximity.dist_structure_m` | 0.0 | 92,440 | 8,104 | 11,203 | Based on current building footprints; does not reflect structures at time of fire |
