from pyfi import WindHelper
import datetime as dt
import pandas as pd
import numpy as np


def yoy2fixedbaseindex(orgfbi, yoylist, option1='index', option2='yoy', fbiloc='start'):
    """
    author: HuPeiran
    # input: orgfib, yoylist = pandas.data dataframe
    # option1 = 'index' OR 'mom', option2 = 'yoy' OR 'cumyoy', fbiloc = 'start' OR ?

    # option1 代表初始定基指数的形式，指数形式 - 'index'，环比形式 - 'mom'
    # option2 代表计算定基指数的数据形式，同比数据 - 'yoy'，累计同比数据 - 'cumyoy'
    # option3 用于指定初始定基指数和后面环比数据位置

    # 初始定基指数不能与同比数据叠加
    # 举例：初始定基指数'2011-01:2011-12'，同比数据'2012-01:2018-05'
    # 函数最后将初始定基指数和同比数据一并返回
    :param orgfbi:
    :param yoylist:
    :param option1:
    :param option2:
    :param fbiloc:
    :return:
    """
    startmonth = orgfbi.index[0].month
    endmonth = orgfbi.index[-1].month
    cyc = endmonth - startmonth + 1

    if option1 == 'mom':
        temp = [1 + i for i in orgfbi.iloc[:, 0].values]
        temp[0] = 1
        orgfbi_list = np.cumprod(temp)
        orgfbi_list = [i * 100 for i in orgfbi_list]
    elif option1 == 'index':
        start = orgfbi.iloc[:, 0].values[0]
        temp = [i / start * 100 for i in orgfbi.iloc[:, 0].values]
        orgfbi_list = temp

    startyear = yoylist.iloc[:, 0].index[0].year
    alldatelist = yoylist.index
    allyearlist = [i.year for i in alldatelist]
    temp = list()
    [temp.append(i) for i in allyearlist if not i in temp]  # 取yoy数据的所有年份
    allyearlist = temp

    len_ = len(yoylist[str(allyearlist[-1])])
    if len_ != cyc:
        newdate = pd.date_range(start=dt.date(allyearlist[0], startmonth, 1),
                                end=dt.date(allyearlist[-1], endmonth, 31), freq='M')
        adddata = [0] * (cyc * (len(allyearlist) - 1) + len_) + [np.nan] * (cyc - len_)
        adddata_dataf = pd.DataFrame(data=adddata, index=newdate, columns=['temp'])
        yoylist.columns = ['temp']
        yoylist_new = yoylist + adddata_dataf

    yoy_1year = list()
    yoy_1year.append(orgfbi_list)

    for year_count in allyearlist:
        yoy_1year.append(
            [float(i) / 100 + 1 for i in yoylist_new.loc[str(year_count), :].values])  # dataframe.values = array

    yoy_1year_array = np.array([i for i in yoy_1year])
    re = list(np.cumprod(yoy_1year_array.T, axis=1).T.reshape((1, cyc * (len(allyearlist) + 1)))[0])
    re[-(cyc - len_):] = []
    re = pd.DataFrame(data=re, index=list(orgfbi.index) + list(yoylist.index), columns=['FixedBaseIndex'])
    return re



def macro_adjust(yoy, cyoy):
    yoy = yoy[yoy.index.month != 1]
    for i in range(len(yoy)):
        if yoy.index[i].month == 2:
            yoy[i] = cyoy[i]
    return yoy
