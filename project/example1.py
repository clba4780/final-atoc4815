import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from analysis import get_era5_variables

"""
Example 1: Create a scatterplot comparing the Total Cloud Cover to the Solar Efficiency over the Continuenal US for Summer 2025. 
"""

# Load climate variables from ERA5
ds = get_era5_variables(
        time_slice = ("2025-06-01", "2025-08-31"),
        lat = (25, 50),
        lon = (-125, -65), 
        name = 'analysis'
    )

# Compute derived variables
ds['eff'] = (ds['snsr']/ds['snsr_cs'])
eff = ds['eff']
cc = ds['cc']

times = ds['time'].values
months = ds['time'].dt.month.values.flatten() # get the month integers (6,7,8) to color code points

# Collapse the spatial dimensions (lat/lon) into a sinle mean/timestep
# gives one (cc,eff) pair per day (US average) 
cc = ds['cc'].mean(dim = ['latitude', 'longitude']).values.flatten()
eff = ds['eff'].mean(dim = ['latitude', 'longitude']).values.flatten()

# Mask removes any invalid data (NaN or Inf values)
mask = np.isfinite(cc) & np.isfinite(eff)
cc = cc[mask]
eff = eff[mask]
months = months[mask]


if len(cc) <2:
    print ("Skipping: not enough data")

else:
# Randomly keeps 30% to reduce over plotting for long time series
# same index array (resample) is applies to cc,eff, and months
# each point represents the same timestep
    resample = np.random.choice(len(cc), size=max(2,int(len(cc)*0.3)), replace = False)
    # use the same resample for all variables so the points still match
    # (makes the scatter plot cleaner for long term analysis)
    cc = cc[resample]
    eff = eff[resample]
    months = months[resample]

fig, ax = plt.subplots(figsize=(8,5))


# Create scatterplot
cmap = cm.get_cmap('plasma', 3)
sc = ax.scatter(cc, eff, c=months, cmap=cmap, vmin = 6, vmax =8, alpha=0.5, s=15, edgecolors='none')

cbar = fig.colorbar(sc, ax=ax, ticks=[6, 7, 8])
cbar.set_label("Month")
cbar.ax.set_yticklabels(['Jun', 'Jul', 'Aug'])


plt.xlabel("Total Cloud Cover (fraction)")
plt.ylabel("Solar Efficiency (snsr/snsr_cs)")
plt.title("Cloud Cover vs Solar Efficiency")
plt.suptitle("Continental US - Jun, Jul, Aug 2025", fontsize = 10)
plt.grid(alpha = 0.2)

plt.tight_layout()
plt.savefig("example1.png", dpi = 150)
print ("example1.png saved")
plt.show()
