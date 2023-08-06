import pandas as pd


def mean_Jan_Feb(ts):
    """Jan&Feb data Adjustment
    1,2月的数据都取1,2月数据的均值
    """
    # 输入的时间序列中1月和2月数据必须成对出现！
    ts_ave12 = ts.copy()
    Jan = pd.date_range(ts.index[0], ts.index[-1], freq='A-JAN')
    Feb = pd.date_range(ts.index[0], ts.index[-1], freq='A-FEB')
    ave12 = (ts.loc[Jan].values + ts.loc[Feb].values) / 2  # 将1,2月的数据进行修正
    ts_ave12.loc[Jan] = ave12
    ts_ave12.loc[Feb] = ave12
    ts_ave12.name = 'mean_Jan_Feb'

    return ts_ave12


def get_idx(yoyr, yoycr, base, base_year=2011):
    """
    获取定基指数
    输入为当月同比，累计同比，基值，基年（默认2015年）,因为CPI和IP的wind提供的定基指数的时长都不长，
    因此综合考虑，我们觉得放在2015年是比较合适的。
    :param yoyr: 当月同比数据
    :param yoycr: 累计同比数据
    :param base: 原始定基指数
    :param base_year: 定基年，默认2015
    :return:
    """
    # 初始化
    date_index = pd.date_range(pd.to_datetime('1990-01-31'), yoycr.index[-1], freq='M')
    idx = pd.DataFrame(index=date_index)
    Sec_Names = yoycr.columns

    for sec_name in Sec_Names:  # 将基年总工业增加值序列（12个月）设为各行业工业增加值的基准
        idx.loc[str(base_year), sec_name] = base[str(base_year)] / base[str(base_year)].iloc[0] * 100

    # 推算基年之后数据
    year = base_year + 1
    while pd.to_datetime(str(year) + '-01-31') <= yoycr.index[-1]:
        year_idx = yoycr[str(year)].index
        last_year_idx = year_idx - pd.tseries.offsets.MonthEnd() * 12
        idx.loc[year_idx] = idx.loc[last_year_idx].values * yoyr.loc[year_idx].values
        idx.loc[year_idx[1]] = idx.loc[last_year_idx[1]].values * yoycr.loc[year_idx[1]].values
        idx.loc[year_idx[0]] = idx.loc[year_idx[1]]  # 1月等于2月
        year = year + 1

    # 推算基年之前数据
    year = base_year
    while pd.to_datetime(str(year) + '-12-31') >= yoycr.index[0]:
        next_year_idx = yoycr[str(year)].index
        year_idx = next_year_idx - pd.tseries.offsets.MonthEnd() * 12
        idx.loc[year_idx] = idx.loc[next_year_idx].values / yoyr.loc[next_year_idx].values
        if pd.to_datetime(str(year - 1) + '-01-31') == year_idx[0]:  # 去年的一月份
            # 2月份的数据用累计同比倒推，并使得1月等于2月
            idx.loc[year_idx[1]] = idx.loc[next_year_idx[1]].values / yoycr.loc[next_year_idx[1]].values
            idx.loc[year_idx[0]] = idx.loc[year_idx[1]]  # 1月等于2月
        year = year - 1

    return idx


def cum2single(series, missingJan=False, pctChange=False):
    """
    将累计值转为单月值 input: pd.series/dataframe
    # 若1月数据缺失 missingJan = True
    # 函数默认返回当月值 要返回环比 pctChange = True
    :param series:
    :param missingJan:
    :param pctChange:
    :return:
    """
    monthindex = pd.date_range(start=series.index[0], end=series.index[-1], freq='A-JAN')
    if missingJan:
        monthindex = pd.date_range(start=series.index[0], end=series.index[-1], freq='A-FEB')
    new_series = series.diff()
    new_series.loc[monthindex] = series.loc[monthindex]
    if pctChange:
        lenzero = len(new_series.loc[new_series.iloc[:, 0] == 0])
        print('caution: number of zeros in series: {0!s}, which may lead NaN or Inf'.format(lenzero))
        new_series = new_series.pct_change()
    return new_series
