# Using T at 850hPa as an example, in practice, the target is 2m height air temperature 

import cdsapi
import argparse
from urllib.request import urlopen
import os
import glob
import math
import time
import datetime
import random
random.seed(3019)
from copy import deepcopy
import warnings
import itertools
import scipy.stats
import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.cm import ScalarMappable
import multiprocess as mp
import scipy.io
warnings.simplefilter(action='ignore')

print('------------------using t850, 15-d window and 95% threshold-------------------')

print('------------------read data------------------')
data2d = xr.open_mfdataset('/burg/glab/users/yh3019/era5_daily/atmos3d/temperature/temperature*.nc').sel(level=850).reset_coords('level',drop=True)
mask =  xr.open_dataset('/burg/glab/users/yh3019/data2d_dkrz/landmask.nc')

ll1 = np.arange(0,180.25,0.25)
ll2 = np.arange(-179.75,0,0.25)
ll = np.concatenate([ll1,ll2])
mask['longitude'] = ll
mask = mask.sortby('longitude')
mask = mask.sel(latitude=slice(70,15),longitude=slice(-30,40)).isel(time=0)
data2d['mask'] = mask.lsm
data2d = data2d.where(data2d.mask>0.9)
data2d = data2d.rename({'t':'t850'})
data2d = data2d.sortby('latitude')
hw = data2d['t850'] 
 
MJJA = hw.isel(time=hw.time.dt.month.isin([5, 6, 7, 8])) # ['t850']
MJJA['doy'] = xr.DataArray(data = np.repeat(np.arange(0,123).reshape(1,123), 33, axis=0).reshape(123*33),
             dims=['time'],
             coords=dict(time=MJJA.time))
MJJA_df = MJJA.to_dataframe().reset_index().set_index(['latitude','longitude']).dropna()
iid = MJJA_df.index.unique()
num_start = 1990
num_end = 2023
years = num_end - num_start
len_year = 61 # June and July, length of days in a year
percentile = 95.
percentile_window = 15 
half_window = 7
start_day = 31
manager = mp.Manager()
glb = manager.Namespace()
# glb.df = metrics_df
glb.hyperparams = [start_day, len_year, half_window, percentile]

def thres_calc(params):
    df, i = params
    start_day, len_year, half_window, percentile = glb.hyperparams
    # print(i,'\n')
    t850_window = np.zeros(len_year)
    # t850m_window = np.zeros(len_year)
    for t in np.arange(start_day,start_day+len_year):
        t850_window[t-start_day] = df.set_index('doy').loc[list(range(t-half_window,t+half_window))].t850.quantile(percentile/100.)
        # t850m_window[t-start_day] = df.set_index('doy').loc[list(range(t-half_window,t+half_window))].t850m.quantile(percentile)
    return pd.Series(t850_window, name = i) #, pd.Series(t850m_window, name = i) 


print('-------------calculating 95th%---------------')
pool = mp.Pool(processes=32)
tic = time.time()
print('start')
results = pool.map(thres_calc, [(MJJA_df.loc[i],i) for i in iid]) #[(params[i],i) for i in list(range(len(params)))])
print('end')
toc = time.time()
print('Use time:',(toc-tic), 's')

print('----------------output 95th%-----------------')
N = len(results)
tmp1 = results[0]
# tmp1 = results[0][0]
# tmp2 = results[0][1]
for i in list(range(N-1)):
    tmp1 = pd.concat([tmp1, results[i+1]], axis=1)
    # tmp1 = pd.concat([tmp1, results[i+1][0]], axis=1)
    # tmp2 = pd.concat([tmp2, results[i+1][1]], axis=1)
tmp1.index = tmp1.index
# tmp1.index = tmp1.index+152
# tmp2.index = tmp2.index+152
tmp1 = tmp1.unstack().reset_index()
# tmp2 = tmp2.unstack().reset_index()
tmp1.columns = ['latitude','longitude','doy','t850_95th']
# tmp2.columns = ['latitude','longitude','doy','t850m_95th']
# tmp1['t850m_95th'] = tmp2['t850m_95th'].copy()
print('-------------storing data to csv-------------')
tmp1.to_csv('/burg/glab/users/yh3019/csv/t850_95th_15d.csv', index=True)
# tmp2.to_csv('/burg/glab/users/yh3019/csv/t850m_95th.csv', index=True)
