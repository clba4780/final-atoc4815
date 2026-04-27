import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from core import load, open_era5

def get_era5_variables(time_slice, lat, lon, name, cache = True):
    """
    Open ERA5 variables relating to Surface Energy Balance and Cloud Effects: 
    - Surface Net Solar Radiation (snsr)
    - Surface Net Solar Radiation Clear Sky (snsr_cs)
    - Total Cloud Cover (cc)
    - 2-meter temperature (t2m)

    If cache file ``era5_{name}.nc`` exists and ``cache = True``, it is read directly from the disk. If not, the data is downloaded and saved for future calls. 

    Paramaters
    ----------
    time_slice : tuple of str
        Start and end data, ex. ``("2025-06-01", "2025-06-03")``
    lat : tuple of a float
        Latitude, ex. ``(-125, -65)``
    lon : tuple of a float 
        Longitude, ex. ``(25, 50)``
    name : str
        Label used to build cache filename, (``era5_{name}.nc``)
    cache : boolean (optional)
        Read or write to a local .nc file. Default is True

    Returns
    ----------
    tuple of xr.DataArrays
        contains: ``(snsr, snsr_cs, cc, t2m)``
        
    Example 
    ----------
    ds = get_era5_variables(
    time_slice = ("2025-06-22", "2025-06-22"),
    # lat, lon correspond to the contiguous United States
    lat = (25, 50),
    lon = (-125, -65), 
    name = '2025_Jun22_contigUS'
    )
    """
    fname = f"era5_{name}"
    
    if cache and os.path.exists(fname + ".nc"):
        print ("Loading from cache...")
        return xr.open_dataset(fname + ".nc")
    
    print ("Downloading data set...")
    # Download ERA5 variables and convert K --> °C
    snsr = load(open_era5("surface_net_solar_radiation", time_slice, lat, lon))
    snsr_cs = load(open_era5("surface_net_solar_radiation_clear_sky", time_slice, lat, lon))
    cc = load(open_era5("total_cloud_cover",time_slice, lat, lon))
    t2m = load(open_era5("2m_temperature", time_slice, lat, lon)) - 273.15
    
    ds = xr.Dataset({
        "snsr" : snsr,
        "snsr_cs": snsr_cs, 
        "cc" : cc,
        "t2m" : t2m,
    })
    
    if cache:
        print ("saving dataset...")
        ds.to_netcdf(fname + ".nc")
    
    return (xr.open_dataset(fname + ".nc"))

def cloud_stats(ds):
    """
    Calculate cloud statistics and add them to the dataset.

    Adds two derived variables:
    
    a) Cloud Radiative Effect (cre) - Reduction in the surface shortwave radiation due to the clouds. (clear sky minus all sky radiation) Shows how effective the clouds are at blocking solar radiation.
    b) Solar Efficiency (eff) - Describes the fraction clear-sky radiation that reaches the surface. 
    
    Parameters
    -----------
    ds : xr.Dataset 
        Must include:
            "snsr" : surface_net_solar_radiation
            "snsr_cs" : surface_net_solar_radiation_clear_sky

    Returns
    -----------
    xr.Dataset
        the inputted dataset with the added variables
    """
    # Cloud radiative effect
    ds['cre'] = (ds['snsr_cs'] - ds['snsr'])
    # Efficiency - how much solar radiation reaches the surface (0-1)
    ds['eff'] = (ds['snsr']/ds['snsr_cs'])

    return ds

def map_features(ax):
    """
    Adds geographic features to Cartopy GeoAxes
    
    Additional Features:
    - Coastlines (linewidth: 0.8)
    - Borders (dashed, linewidth: 0.5)
    - Land (light gray, 30% opacity)
    - US States (gray, 20% opacity)
    - Gridlines with axis label (lindwidth: 0.5, 50% opacity)

    Parameters:
    -----------
    ax : ax

    Returns:
    -----------
    None
        only adds features to the current ``ax``
    """
    # 3. Add geographic features
    ax.coastlines(linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='--')
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.STATES, edgecolor = 'gray', linewidth = 0.5, alpha = 0.2)
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)


def mapping(title, filename, ds, time = 0, n_rows = 1):
    """
    Plot CRE, solar efficiency, and 2meter temperature on a multi-paneled map figure, using a Robinson projection

    The panel are arranged in ``n_rows``, with columns filled in automatically. 
    Each panel uses ``map_features()``. 
    Then the figure is saved locally. 
    
    Parameters:
    -----------
    title: str
        Map title displayed above all panels
    filename: str
        name for the saved figure
    ds: xr.Dataset 
        must contain cre, eff, t2m with a time dimension (taken from get_era5_variables and cloud_stats)
    time: int (optional)
    n_rows: int, optional
        number of rows in the subplot grid (allows maps to be stacked on one column)

    Returns:
    ----------
    fig, ax 
        fig : matplotlib.figure.Figure
        ax : list of cartopy.mpl.geoaxes.GeoAxes
            All subplot axes in row-major order
    """
    panels = [
        {
            "data": ds['cre'].isel(time=time),
            "label": "Cloud Radiative Effect (J/m^2)",
            "subtitle": "Cloud Radiative Effect",
            "cmap": "RdBu_r"
        },
        {
            "data": ds['eff'].isel(time=time),
            "label": "Solar Efficiency",
            "subtitle": "Solar Efficiency", 
            "cmap": "plasma"
        }, 
        {
            "data": ds['t2m'].isel(time=time),
            "label": "2-meter Temperature (°C)",
            "subtitle": "2-meter Temperature",
            "cmap": "coolwarm"
        }
    ]
    n_cols = -(-len(panels)//n_rows)
    
    fig, ax = plt.subplots(
        nrows = n_rows,
        ncols = n_cols,
        figsize = (7*n_cols,4*n_rows),
        subplot_kw={'projection': ccrs.Robinson()},   # 1. Choose map projection
        constrained_layout = True
    )
    # normalizes the return value of plt.subplots so the for loop can always iterate over the axis in the same way
    axes_flat = list(ax.flat) if hasattr(ax, "flat") else [ax]

    for ax, panel in zip(axes_flat, panels):
        panel['data'].plot(
            ax = ax,
            transform = ccrs.PlateCarree(),
            cmap = panel['cmap'],
            cbar_kwargs = {'label': panel['label'], 'shrink':0.7}
        )
        map_features(ax)
        ax.set_title(panel['subtitle'], fontsize = 10)
    
    fig.suptitle(title, fontsize =15)
    plt.savefig(filename, dpi = 150)
    print (f"{filename} saved")
    plt.show()

    return fig, axes_flat

if __name__ == "__main__":
    ds = get_era5_variables(
        time_slice = ("2025-06-01", "2025-08-31"),
        lat = (25, 50),
        lon = (-125, -65), 
        name = 'analysis'
    )

    cloud_stats(ds)

    mapping(
        "Cloud Radiative Effect, Solar Radiation, & Temperature Analysis - Summer 2025", 
        filename = "analysis",
        ds = ds, 
    )