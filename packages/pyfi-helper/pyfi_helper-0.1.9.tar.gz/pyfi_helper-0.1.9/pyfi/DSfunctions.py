"""
#-#-#-#-#-#-#-#-#-#-#-#-#-#-季节性调整-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

所有输入应当是月频时间序列，即以月频datetime为index的pandas.Series
需要下载的模组：numpy，pandas，scipy
关于季节性调整的资料参考以下网址：
http://cn.mathworks.com/help/econ/seasonal-adjustment-using-snxd7m-seasonal-filters.html

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#--#-#-#-#-#-
"""

import numpy as np
import pandas as pd
import scipy.signal as sg


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-滤波函数#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def mean_Jan_Feb(ts):
    """
    平均1、2月数据
    输入的时间序列中1月和2月数据必须成对出现！
    :param ts:
    :return:
    """
    ts_ave12 = ts.copy()
    Jan = pd.date_range(ts.index[0], ts.index[-1], freq='A-JAN')
    Feb = pd.date_range(ts.index[0], ts.index[-1], freq='A-FEB')
    ave12 = (ts.loc[Jan].values + ts.loc[Feb].values) / 2
    ts_ave12.loc[Jan] = ave12
    ts_ave12.loc[Feb] = ave12
    ts_ave12.name = 'mean_Jan_Feb'

    return ts_ave12


def MA13(ts):  # 13-Term Moving Average

    # Symmetric weights for 13-Term MA
    sw13 = np.zeros(13) + 1 / 12
    sw13[0] = 1 / 24
    sw13[-1] = 1 / 24

    arr_ts_MA13 = sg.convolve(ts, sw13, 'same')  # 卷积
    # the following two lines deals with data at end of Series
    arr_ts_MA13[0:6] = arr_ts_MA13[6]
    arr_ts_MA13[-6:] = arr_ts_MA13[-7]
    ts_MA13 = pd.Series(arr_ts_MA13, index=ts.index)
    ts_MA13.name = '13-Term Moving Average'

    return ts_MA13


def MA13C(ts):
    """
    13-Term Moving Average for centering data
    :param ts:
    :return:
    """
    # Symmetric weights for 13-Term MA
    sw13 = np.zeros(13) + 1 / 12
    sw13[0] = 1 / 24
    sw13[-1] = 1 / 24

    arr_ts_MA13C = sg.convolve(ts, sw13, 'same')
    # the following two lines deals with data at end of Series
    # different from original MA13
    arr_ts_MA13C[0:6] = arr_ts_MA13C[12:18]
    arr_ts_MA13C[-6:] = arr_ts_MA13C[-18:-12]
    ts_MA13C = pd.Series(arr_ts_MA13C, index=ts.index)
    ts_MA13C.name = '13-Term Moving Average C'

    return ts_MA13C


def H13(ts):  # 13-Term Henderson filter

    # Henderson filter weights
    swh = np.array([-0.019, -0.028, 0, .066, .147, .214,
                    .24, .214, .147, .066, 0, -0.028, -0.019])
    # Asymmetric weights for end of series
    awh = np.array([[-.034, -.017, .045, .148, .279, .421],
                    [-.005, .051, .130, .215, .292, .353],
                    [.061, .135, .201, .241, .254, .244],
                    [.144, .205, .230, .216, .174, .120],
                    [.211, .233, .208, .149, .080, .012],
                    [.238, .210, .144, .068, .002, -.058],
                    [.213, .146, .066, .003, -.039, -.092],
                    [.147, .066, .004, -.025, -.042, 0],
                    [.066, .003, -.020, -.016, 0, 0],
                    [.001, -.022, -.008, 0, 0, 0],
                    [-.026, -.011, 0, 0, 0, 0],
                    [-.016, 0, 0, 0, 0, 0]])

    # Apply 13-term Henderson filter
    arr_h13 = sg.convolve(ts, swh, 'same')
    arr_h13[-6:] = sg.convolve(ts[-12:].values[:, None], awh, 'valid')
    arr_h13[0:6] = sg.convolve(ts[0:12].values[:, None], np.rot90(awh, 2), 'valid')
    h13 = pd.Series(arr_h13, index=ts.index)
    h13.name = '13-Term Henderson Filter'

    return h13


def S33(ts):  # S3x3 seasonal components

    T = len(ts)
    sidx = []
    for i in range(12):
        sidx.append(np.arange(i, T, 12))

    # Symmetric weights
    sw3 = np.array([1 / 9, 2 / 9, 1 / 3, 2 / 9, 1 / 9])
    # Asymmetric weights for end of series
    aw3 = np.array([[.259, .407], [.37, .407], [.259, .185], [.111, 0]])
    aw3R = [[0, .111], [.185, .259], [.407, .37], [.407, .259]]
    # Apply filter to each month
    shat3 = ts.copy()
    for i in range(12):
        ns = len(sidx[i])
        dat = ts[sidx[i]].copy()
        sd = sg.convolve(dat.values, sw3, 'same')
        sd[0:2] = sg.convolve(dat[0:4].values[:, None], np.rot90(aw3, 2), 'valid')
        sd[-2:] = sg.convolve(dat[-4:].values[:, None], aw3, 'valid')
        shat3.iloc[sidx[i]] = sd

    # 13-term moving average of filtered series
    sb = MA13C(shat3)
    # Center to get final estimate
    s33 = shat3 / sb
    s33.name = 'Seasonal component estimates'

    return s33


def S35(ts):  # S3x5 seasonal Components

    T = len(ts)
    sidx = []
    for i in range(12):
        sidx.append(np.arange(i, T, 12))

    # Symmetric weights
    sw5 = np.zeros(7) + 1 / 5
    sw5[0:2] = [1 / 15, 2 / 15]
    sw5[-2:] = [2 / 15, 1 / 15]
    # Asymmetric weights for end of series
    aw5 = np.array([[.150, .250, .293],
                    [.217, .250, .283],
                    [.217, .250, .283],
                    [.217, .183, .150],
                    [.133, .067, 0],
                    [.067, 0, 0]])
    # Apply filter to each month
    shat5 = ts.copy()
    for i in range(12):
        ns = len(sidx[i])
        dat = ts[sidx[i]].copy()
        sd = sg.convolve(dat.values, sw5, 'same')
        sd[0:3] = sg.convolve(dat[0:6].values[:, None], np.rot90(aw5, 2), 'valid')
        sd[-3:] = sg.convolve(dat[-6:].values[:, None], aw5, 'valid')
        shat5.iloc[sidx[i]] = sd

    # 13-term moving average of filtered series
    sb = MA13C(shat5)
    # Center to get final estimate
    s35 = shat5 / sb
    s35.name = 'Seasonal component estimates'

    return s35


# -#-#-#-#-#-#-#-derive deseasonalized series-#-#-#-#-#-#-#-

def Deseason(ts, Jan_Feb=False):
    """
    # -----是否平均1、2月数据-----
    :param ts:
    :param Jan_Feb:
    :return:
    """
    if Jan_Feb:  # 如果选择平均，则对1,2月数据进行取平均，否则就不做处理
        IVA_av12 = mean_Jan_Feb(ts)
    else:
        IVA_av12 = ts

    # -----Detrend the data using a 13-term moving average-----
    IVA_MA13 = MA13(IVA_av12)
    IVA_xt = IVA_av12 / IVA_MA13

    # -----Apply an S(3,3) seasonal filter to deseasonalize-----
    IVA_S33 = S33(IVA_xt)
    IVA_DeSeason = IVA_av12 / IVA_S33  # Deseasonalize series

    # -----Apply a 13-term Henderson filter to improve detrending-----
    IVA_H13 = H13(IVA_DeSeason)
    IVA_xt2 = IVA_av12 / IVA_H13  # New detrended series

    # -----Apply an S(3,5) seasonal filter to improve deseasonalizing-----
    IVA_S35 = S35(IVA_xt2)
    IVA_DeSeason2 = IVA_av12 / IVA_S35
    IVA_DeSeason2.name = 'Deseasonalized IVA'

    return IVA_DeSeason2

################### X13 ########################