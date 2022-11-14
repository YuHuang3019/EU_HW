This repository contains info about the collaborative project on European heatwave in Prof Gentine's lab.

**ERA5 Data description**
| Parameter     | Description |
| ---      | ---       |
| 2D Variables         |    T2m, Ts, Precip, Evapor, Potential Evapor, SWC, LH, SH, Solar Rad, 10m UV winds|
| 3D Variables         |    Geopotential(Z), Wind speed(U,V,omega), Cloud cover| 
| Temporal resolution  |    hourly(for temp only), daily(for other vars)      |
| Spatial resolution   |    0.25 degree |
| Temporal coverage    |    1990-2022, MJJA  |
| Spatial coverage     |    [15N, 70N], [150W, 40E]                 |
| Projection           |    EU Heatwave          |
| Download URL         |    https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset|
| Avaliable downloaded |    /burg/glab/users/yh3019/era5_raw  |
| File format          |    netcdf                 |

* For SMAP data, please see https://github.com/os2328/GlabData/tree/main/data_cards


**Scripts description**
| Scripts     | Description |
| ---      | ---       |
|era5_download.py       | Download ERA5 data at hourly resolution (and extract the min, mean, max).|
|localhw_detect_mp.py   | Collect T2m_max in a centered N-day window from 1990-2022, get the 95%th percentile threshold and define local extremes based on it. Using multiprocess. |
|time_series.py         | Plot the temporal evolution of vars in three panels.|



**Links to method source**
| Description | Links |
| ---      | ---       |
|Lagrangian trajectories                     | https://github.com/Novarizark/easy-era5-trck|
|Eulerian decomposition                      | https://www.nature.com/articles/s43247-020-00048-9.pdf|
|Dry static energy convergence decomposition | https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2021AV000619
