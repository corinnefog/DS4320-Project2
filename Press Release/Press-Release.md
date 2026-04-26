<a name="press-release"></a>

# From Small Spark to Catastrophe: Machine Learning Predicts Which California Wildfires Will Explode in Size

## Hook

Most California wildfires start the same way, a spark. What happens next determines whether a fire crew puts it out in an afternoon or whether it burns for months and makes national headlines. A new data-driven model can classify that outcome within minutes of ignition.

## Problem Statement

California experienced over 8,000 wildfires per year on average over the past decade, but a tiny fraction of those fires, less than 5%, account for over 95% of total acres burned. The core challenge for fire managers is that in the first critical hours, every fire looks the same. Responders must decide how many resources to commit before they know whether a fire will stay small and containable or erupt into a landscape-scale disaster. Current decision tools rely heavily on expert judgment and broad regional risk ratings, rather than fire-specific, data-driven predictions. Misallocating resources, sending too little to a fire that becomes catastrophic, or overwhelming a small fire with unnecessary assets, costs lives and millions of dollars.

## Solution Description

## Solution Description

Using historical wildfire records from California spanning 2000 to 2020, combined with topographic characteristics and the day of year and location of each ignition, we trained a Random Forest model to classify whether a newly reported fire will grow into a small (under 100 acres), medium (100–999 acres), or large (1,000+ acres) fire. The model identified day of year and geographic location as the strongest predictors of fire size — fires discovered later in the fire season and in certain regions of California are significantly more likely to become large. The model gives emergency managers an early signal at the time of ignition, before size is known, so resources can be pre-positioned accordingly.
