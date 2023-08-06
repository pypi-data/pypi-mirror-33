from datetime import timedelta, datetime
import pandas as pd
import time


def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__))
        print("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back

    return newFunc


def nearest(items, pivot):
    return min(items, key=lambda x: abs((x + timedelta(1) - pivot)))


def get_end_date():
    """确定开始时间，计算最新的已经结算的交易日"""
    from pyfi import WindHelper
    # 确定结束时间
    # 结束时间为该合约的最后交易日和当前日期的最小值
    last_trade_date = WindHelper.t_days_offset(offset=0, cur_date=datetime.now())
    # 确定结束时间
    if datetime.now().hour >= 19:  # 以晚上19点为界限
        end_date = last_trade_date
    elif datetime.now().date() > last_trade_date.date():  # 当天不是交易日
        end_date = last_trade_date
    else:  # 既非节假日，且当然的数据也没有生成
        end_date = WindHelper.t_days_offset(offset=-1, cur_date=datetime.now())  # datetime类型
    return end_date


def get_date_list(begin_date, end_date):
    # begin_date, end_date是形如‘20160601’的字符串或datetime格式
    date_l = [x for x in list(pd.date_range(start=begin_date, end=end_date))]
    return date_l
