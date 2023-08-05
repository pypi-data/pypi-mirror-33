#  Python Module for import                           Date : 2018-06-08
#  vim: set fileencoding=utf-8 ff=unix tw=78 ai syn=python : per PEP 0263
'''
_______________|  bootstrap.py :: Bootstrap module for fecon236

- Design bootstrap to study alternate histories and small-sample statistics.
- Normalize, include fat tails, specify population mean and volatility.
- Pre-compute pool of asset returns:
    - SPX 1957-2014, requires fecon235/nb/SIMU-mn0-sd1pc-d4spx_1957-2014.csv.gz
- Visualize price paths.


CHANGE LOG  For LATEST version, see https://git.io/fecon236
2018-06-08  Spin-off 2014 material from sim.py, but needs generalization. <=
                Let N generally be the count:= sample size.
'''

from __future__ import absolute_import, print_function, division

import numpy as np
from fecon236.util import system
from fecon236.tool import todf, georet
from fecon236.host.fred import readfile
from fecon236.visual.plots import plotn


#  ACTUAL SPX mean and volatility from 1957-01-03 to 2014-12-11 in percent,
#  where N = 15116
MEAN_PC_SPX = 7.6306
STD_PC_SPX = 15.5742
N_PC_SPX = 15116


def GET_simu_spx_pcent():
    '''Retrieve normalized SPX daily percent change 1957-2014.'''
    #           NORMALIZED s.t. sample mean=0 and std=1%.
    datafile = 'SIMU-mn0-sd1pc-d4spx_1957-2014.csv.gz'
    try:
        df = readfile(datafile, compress='gzip')
        #  print(' ::  Import success: ' + datafile)
    except Exception:
        df = 0
        print(' !!  Failed to find: ' + datafile)
    return df


def SHAPE_simu_spx_pcent(mean=MEAN_PC_SPX, std=STD_PC_SPX):
    '''Generate SPX percent change (defaults are ACTUAL annualized numbers).'''
    #  Thus the default arguments can replicate actual time series
    #  given initial value:  1957-01-02  46.20
    #  Volatility is std:= standard deviation.
    spxpc = GET_simu_spx_pcent()
    mean_offset = mean / 256.0
    #                    Assumed days in a year.
    std_multiple = std / 16.0
    #                    sqrt(256)
    return (spxpc * std_multiple) + mean_offset


def SHAPE_simu_spx_returns(mean=MEAN_PC_SPX, std=STD_PC_SPX):
    '''Convert percent form to return form.'''
    #  So e.g. 2% gain is converted to 1.02.
    spxpc = SHAPE_simu_spx_pcent(mean, std)
    return 1 + (spxpc / 100.0)


def array_spx_returns(mean=MEAN_PC_SPX, std=STD_PC_SPX):
    '''Array of SPX in return form.'''
    #  Array far better than list because of numpy efficiency.
    #        But if needed, use .tolist()
    spxret = SHAPE_simu_spx_returns(mean, std)
    #  Use array to conveniently bootstrap sample later.
    #  The date index will no longer matter.
    return spxret['Y'].values


def bootstrap(N, yarray):
    '''Randomly pick out N without replacment from yarray.'''
    #  In repeated simulations, yarray should be pre-computed,
    #                           using array_spx_returns(...).
    #  http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html
    return np.random.choice(yarray, size=N, replace=False)


def simu_prices(N, yarray):
    '''Convert bootstrap returns to price time-series into pandas DataFrame.'''
    #  Initial price implicitly starts at 1.
    #  Realize that its history is just the products of the returns.
    ret = bootstrap(N, yarray)
    #               Cumulative product of array elements:
    #               cumprod is very fast, and keeps interim results!
    #  http://docs.scipy.org/doc/numpy/reference/generated/numpy.cumprod.html
    return todf(np.cumprod(ret))


def simu_plots_spx(charts=1, N=N_PC_SPX, mean=MEAN_PC_SPX, std=STD_PC_SPX):
    '''Display simulated SPX price charts of N days, given mean and std.'''
    yarray = array_spx_returns(mean, std)
    #        Read in the data only once BEFORE the loop...
    for i in range(charts):
        px = simu_prices(N, yarray)
        plotn(px)
        #  Plot, then for the given prices, compute annualized:
        #           geometric mean, arithmetic mean, volatility.
        print('     georet: ' + str(georet(px)))
        print('   ____________________________________')
        print('')
    return


if __name__ == "__main__":
    system.endmodule()
