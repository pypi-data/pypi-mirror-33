import pandas as pd


def ds_ip_idx(begin_date, end_date):
    import pyfi.DSfunctions as dsf
    # -----还原工业增加值绝对值-----
    IVA_idx = ip_idx(begin_date, end_date)
    IVA_Deseason = dsf.Deseason(IVA_idx.iloc[:, 0].dropna(how='all'), Jan_Feb=False)
    yoy_Deseason = (IVA_Deseason / IVA_Deseason.shift(12) - 1).dropna(how='all')
    return yoy_Deseason


def ip_idx(begin_date, end_date):
    from pyfi import WindHelper
    import pyfi.IVA_idx as ii
    df = WindHelper.edb(codes=['ip_yoy', 'ip_cyoy'], begin_date=begin_date, end_date=end_date)
    base = WindHelper.edb(codes=["M5567963"], begin_date=begin_date, end_date=end_date).iloc[:, 0]
    IVAyoy = df.loc[:, 'ip_yoy']/100.0
    IVAyoyc = df.loc[:, 'ip_cyoy']/100.0
    IVAyoyr = pd.DataFrame(1 + IVAyoy)
    IVAyoycr = pd.DataFrame(1 + IVAyoyc)
    Base = ii.mean_Jan_Feb(base)  # 平均基值的1、2月数据
    # -----还原工业增加值绝对值-----
    IVA_idx = ii.get_idx(IVAyoyr, IVAyoycr, Base).dropna()
    return IVA_idx


def ds_cpi():
    pass


def shuini(begin_date, end_date):
    """
    水泥指数
    :param begin_date:
    :param end_date:
    :return:
    """
    from pyfi import WindHelper
    df = WindHelper.edb(codes=["S5104572",
                               "S5104580",
                               "S5104577",
                               "S5104584",
                               "S5104588",
                               "S5104592"],
                        begin_date=begin_date,
                        end_date=end_date)
    return pd.DataFrame({"水泥指数": df.mean(axis=1)}, index=df.index)


def hbhdlm(begin_date, end_date):
    """
    环渤海动力煤(周度数据）
    :param begin_date:
    :param end_date:
    :return:
    """
    from pyfi import WindHelper
    df = WindHelper.edb(codes=["S5104572",
                               "S5104580",
                               "S5104577",
                               "S5104584",
                               "S5104588",
                               "S5104592"],
                        begin_date=begin_date,
                        end_date=end_date).ffill()
    return pd.DataFrame({"环渤海动力煤指数": df.mean(axis=1)}, index=df.index)
