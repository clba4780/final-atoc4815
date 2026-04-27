import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from analysis import get_era5_variables

"""
Example 3: Time series analysis of the Cloud Radiative Effect and 2m Temperature.
Plots CRE and 2m temperature over a single day (June 21, 2025)
for the continetal US and with nighttime shaded for context
"""
ds = get_era5_variables(
    time_slice = ("2025-06-21", "2025-06-21"),
    lat = (25,50),
    lon = (-125,-65),
    name = "jun21_2025"
)
# compute derived variables
cre = ds['snsr_cs'] - ds['snsr']


# calculate the spatial mean for each timestep to get one averaged value for each point
cre = cre.mean(dim = ['latitude', 'longitude'])
t2m = ds['t2m'].mean(dim = ['latitude', 'longitude'])

# remove any invalid data
mask = np.isfinite(cre) & np.isfinite(t2m)

cre = cre[mask]
t2m = t2m[mask]


fig, ax1 = plt.subplots()


# Define nighttime periods (adjust to your actual date)
night_start1 = datetime(2025, 6, 21, 0, 0)
night_end1   = datetime(2025, 6, 21, 6, 0)
night_start2 = datetime(2025, 6, 21, 21, 0)
night_end2   = datetime(2025, 6, 22, 0, 0)

# Shade nighttime periods
ax1.axvspan(night_start1, night_end1, color='navy', alpha=0.1, label='Nighttime')
ax1.axvspan(night_start2, night_end2, color='navy', alpha=0.1)  # no label to avoid duplicate in legend

ax1.plot(cre['time'], cre, linestyle = '-', marker = 'o', color = 'skyblue', label = 'Cloud Radiative Effect')
ax1.set_ylabel('Cloud Radiative Effect (J/m^2)')
ax1.set_xlabel("Hour of Day")

ax2 = ax1.twinx()
ax2.plot(t2m['time'], t2m, linestyle = '--', marker = 's', color = 'salmon', label ='2m Temperature')
ax2.set_ylabel("2m Temperature (°C)")

# custom x-axis to improve readability (using matplotlib.mdates)
ax1.xaxis.set_major_locator(mdates.HourLocator(interval =3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='best')

plt.grid(True, alpha = 0.3)
plt.title("Cloud Radiative Effect vs 2-meter Temperature (June 21,2025)")
plt.tight_layout()
plt.savefig('example2.png', dpi = 150)
plt.show()