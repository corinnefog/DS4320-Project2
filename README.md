# DS4320-Project2 - Predicting Tide Levels

**Executive Summary** -

**Name** - Corinne Fogarty
**NetID** - qfr4cu
**DOI** - 

**Press Release** -

**Pipeline** - 

**License** - 

## Problem Definition 

**General Problem** - Wildfires in California cause billions of dollars in damage, destroy ecosystems, and threaten human lives every year. Land managers and emergency responders need tools to anticipate how large a fire will grow once ignited in order to allocate suppression resources effectively.

**Refined specific problem:** -  Given weather conditions, topographic features, and proximity to human infrastructure at the time and location of ignition, can we classify a California wildfire as small (< 100 acres), medium (100–999 acres), or large (≥ 1,000 acres)?

**Motivation** - California has experienced a dramatic increase in the frequency and severity of wildfires over the past two decades, driven by prolonged drought, rising temperatures, and expanding development into fire-prone wildland areas. The 2018 Camp Fire, the 2020 August Complex Fire, and the 2021 Dixie Fire each burned over 900,000 acres and caused devastating loss of life and property. Despite advances in satellite monitoring and weather forecasting, fire managers still struggle to anticipate which ignitions will remain small and containable versus which will escalate into landscape-scale disasters. Early and accurate size prediction, even a coarse small/medium/large classification, could meaningfully improve how crews and aircraft are pre-positioned in the critical first hours of a fire, when suppression has the greatest chance of success.

**Rationale** - The general problem of wildfire risk is vast and encompasses ignition
probability, spread rate, smoke dispersion, and community exposure. We refined our focus to fire size classification in California for three reasons. First, California has the richest publicly available historical fire record in the country, giving us sufficient labeled examples across all size categories. Second, size at containment is a well-defined, objectively measurable outcome that is recorded consistently in the USFS Fire Occurrence Database, making it a reliable target variable. Third, classifying into three categories rather than predicting exact acreage sidesteps the extreme skewness of fire size distributions  while still producing decision-relevant output for emergency managers choosing between a single engine crew versus a full multi-agency response.

[From Small Spark to Catastrophe: Machine Learning Predicts Which California Wildfires Will Explode in Size](#press-release)

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

**Data Provenance** - 

**Code** -

**Rationale** -

**Bias Identification** -

**Bias Mitigation** -

## Metadata

**Implicit Schema** -

**Data Summary** -

**Data Dictionary** -

**Data Dictionary** -
