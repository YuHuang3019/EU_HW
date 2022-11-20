import cdsapi
import argparse
from urllib.request import urlopen
import os
import glob
import time
import datetime
import random
random.seed(3019)
import warnings
import itertools
warnings.simplefilter(action='ignore')
#import dask.array as da
#from dask.distributed import Client
import xarray as xr
import numpy as np
import pandas as pd
import multiprocess as mp
import os.path, time

out_dir = '/burg/glab/users/yh3019/era5_daily/'

num_start = 1991
num_end = 2022
years = np.arange(num_start,num_end)
var_names = ['10m_u_component_of_wind','10m_v_component_of_wind','potential_evaporation','evaporation','precipitation', 'volumetric_soil_water_layer_1','volumetric_soil_water_layer_2','volumetric_soil_water_layer_3','volumetric_soil_water_layer_4', 'surface_net_solar_radiation','surface_sensible_heat_flux','surface_latent_heat_flux']

# single levels
for year in years:
    for var_name in var_names:
        year = str(year)
        file = out_dir+var_name+'_'+year+'_dailymean.nc'
        c = cdsapi.Client()
        print('loading hourly '+file+' now')
        fl = c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type':'reanalysis',
                    'variable': var_name,
                    'year': year,
                    'month': [
                            '05', '06',
                            '07', '08', 
                        ],
                    'day': [
                            '01', '02', '03',
                            '04', '05', '06',
                            '07', '08', '09',
                            '10', '11', '12',
                            '13', '14', '15',
                            '16', '17', '18',
                            '19', '20', '21',
                            '22', '23', '24',
                            '25', '26', '27',
                            '28', '29', '30',
                            '31',
                        ],
                    'time': [
                            '00:00', '01:00', '02:00',
                            '03:00', '04:00', '05:00',
                            '06:00', '07:00', '08:00',
                            '09:00', '10:00', '11:00',
                            '12:00', '13:00', '14:00',
                            '15:00', '16:00', '17:00',
                            '18:00', '19:00', '20:00',
                            '21:00', '22:00', '23:00',
                        ],
                    'format': 'netcdf',
                    'area': [
                            70, -30, 15,40,
                        ],
                    },
                )
        with urlopen(fl.location) as f:
            ds = xr.open_dataset(f.read())
        print('calculating mean now')
        ds = ds.resample(time='1D').mean('time')
        print('storing data now')
        ds.to_netcdf(file)
