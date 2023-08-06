import pandas as pd
import statsmodels as sm
from pyfi.wind_helper import *
from pyfi.common import get_end_date
import os
import matplotlib.pyplot as plt
from statsmodels.tsa.x13 import *
from datetime import datetime

begin_date = datetime(2005, 1, 1)
end_date = get_end_date()
df = ds_ip_idx(begin_date, end_date).dropna()
df.name = "ip"

XPATH = os.chdir("C:\\dev_env\\WinX13\\x13as")

temp_series = pd.DataFrame(df.values, index=df.index)
temp_series.index.fre_str = "M"
x13results = x13_arima_analysis(endog=temp_series, x12path=XPATH, outlier=True, print_stdout=True)

df_adj = pd.Series(x13results.seasadj.values, index=df.index.values)
df_adj = df_adj.to_frame()
df_adj.columns = ["Adjusted"]
os.chdir(os.getcwd())

ip = WindHelper.edb(codes=["ip_yoy"], begin_date=begin_date, end_date=end_date)/100.0

fig, ax = plt.subplots(figsize=(13, 6))
ax.set_title("季调数据")
ax.plot(df_adj.index, df_adj["Adjusted"], linewidth=2, marker='', markersize=3, zorder=1, label="Seasonally Adjusted")
ax.plot(df_adj.index, ip["ip_yoy"], linewidth=2, marker='', markersize=3, zorder=1, label="Actual")
plt.show()
