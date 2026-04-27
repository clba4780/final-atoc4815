# Cloud cover effect on surface solar radition and 2m temperature
A Python package for visualizing cloud effects on surface temperature and net solar radiation. Uses data from ERA5 reanalysis 2-meter temperature, cloud cover, surface net solar radiation, and surface net solar radiation clear sky. 

# background
Cloud effects vary depending on the time of day, season, location, and elevation. This package takes ERA5 observations and creates visualizations and comparisons to understand cloud effects at the surface. 


# installation

```
pip install -e .
```
for plotting support
```
pip install -e ".[plot]"
```

# quickstart
```
from grab_era5 import load, open_era5
from analysis import get_era5_variables, cloud_stats, mapping

# 1. Open era5 and download the variables: 2m_temperature, cloud_cover, surface_net_solar_radiation, surface_net_solar_radiation_clear_sky

# The function get_era5_variables loads all four variables into a NetCDF file then seperates them for analysis
ds = get_era5_variables(
        time_slice = ("2025-06-01", "2025-08-31"),
        lat = (25, 50),
        lon = (-125, -65), 
        name = 'summer2025_contigUSA'
    )
# compute the necessary cloud statistics and add them to the date set
cloud_stats(ds)

# plot the Cloud Radiative Effect, Solar Efficiency, and 2-meter Temperature on side by side maps for visual analysis
mapping(
        "Cloud, Solar Radiation, & Temperature Analysis - Summer 2025", 
        filename = "analysis",
        ds = ds, 
    )
```
