
**Data description**

| Parameter     | Description |
| ---      | ---       |
| 2D Variables         |    T2m, Ts, Precip, Evapor, Potential Evapor, SWC, LH, SH, Solar Rad, 10m UV winds|
| 3D Variables         | Geopotential(Z), Wind speed(U,V,omega), Cloud cover| 
| Temporal resolution  |    hourly(for temp only), daily(for other vars)      |
| Spatial resolution   |    0.25 degree |
| Temporal coverage    |    1990-2022, MJJA  |
| Spatial coverage     |    [15N, 70N], [150W, 40E]                 |
| Projection           |    EU Heatwave          |
| Download URL         |   https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset|
| Avaliable downloaded |    /burg/glab/users/yh3019/era5_raw  |
| File format          |    netcdf                 |



**Scripts description**
| Scripts     | Description |
| ---      | ---       |
|hw_download.py  | Downloading ERA5 data at hourly resolution (and extract the min, mean, max), using multiprocessing of python|

