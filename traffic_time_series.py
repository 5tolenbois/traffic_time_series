import os
import pandas as pd
import matplotlib.pyplot as plt

# ========== 路径配置 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "data", "州际交通量数据集.csv")

# 设置全局中文字体，解决中文乱码
plt.rcParams['font.sans-serif'] = 'SimHei'
plt.rcParams["axes.unicode_minus"] = False

# ===================== 3.1 州际公路交通量数据集介绍 =====================
"""
数据集：州际公路交通量
字段：
date_time：时间戳
traffic_volume：公路交通流量
任务：时间序列处理、resample重采样、时间切片、时间维度分组、时序绘图
"""

# ===================== 3.2 数据读取 =====================
data = pd.read_csv(csv_path)
print("="*70)
print("【数据集前5行】")
print(data.head(5))

# 捕获info输出打印
from io import StringIO
buffer = StringIO()
data.info(buf=buffer)
data_info = buffer.getvalue()
print("="*70)
print("【data info信息】")
print(data_info)

# 查看统计描述
data_de = data.describe()
print("="*70)
print("【数据集统计描述】")
print(data_de)

# ===================== 3.3 创建时间类型数据 =====================
# 将date_time转为datetime时间类型，设置为索引并排序
data["date_time"] = pd.to_datetime(data['date_time'])
data = data.set_index('date_time')
data = data.sort_index()
print("="*70)
print("【时间索引设置完成，前5行】")
print(data.head(5))

# ===================== 3.4 查看时间跨度 =====================
# resample按月统计月份数量（新版pandas用ME代替M）
p_month = len(data.resample('ME'))
# 最大最小时间求时间差
max_min = data.index.max() - data.index.min()
p_day = max_min.days
print("="*70)
print(f"数据集时间跨度(月份数): {p_month}")
print(f"数据集时间跨度(总天数): {p_day}")

# ===================== 3.5 groupby降采样到年份、月份 =====================
# ----按年份分组，交通流量总和
data1 = data.groupby(data.index.year)['traffic_volume'].sum()
print("="*70)
print("【每年交通流量总数】")
print(data1)

# 绘制每年流量条形图
plt.figure(figsize=(10, 6))
data1.plot(kind='bar')
plt.title('每年交通流量总数条形图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "year_traffic_bar.png"))
plt.show()

# ----按月份分组，交通流量均值
data['month'] = data.index.month
month_t = data.groupby('month')['traffic_volume'].mean()
print("="*70)
print("【每月平均交通流量】")
print(month_t)

plt.figure(figsize=(8, 8))
month_t.plot(kind='pie', autopct='%.2f%%')
plt.title('按月查看平均交通流量饼图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "month_traffic_pie.png"))
plt.show()

# ===================== 3.6 groupby降采样到每天、每小时 =====================
# 按天分组：每日流量最大值
data['day'] = data.index.day
day_t = data.groupby('day')['traffic_volume'].max()
print("="*70)
print("【每日交通流量最大值】")
print(day_t)

plt.figure(figsize=(12, 6), dpi=100)
day_t.plot(kind='line')
# 在折线上标注数值
for x, y in zip(day_t.index, day_t):
    plt.text(x, y - 0.55, '%.0f' % y, ha="right", va="bottom", fontsize=10)
plt.title('每日交通流量最大值折线图')
plt.xlabel('日期（日）')
plt.ylabel('交通流量最大值')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "day_max_traffic_line.png"))
plt.show()

# 按小时分组：每小时流量均值
data['hour'] = data.index.hour
hour_t = data.groupby('hour')['traffic_volume'].mean()
print("="*70)
print("【每小时平均交通流量】")
print(hour_t)

plt.figure(figsize=(15, 6), dpi=100)
hour_t.plot(kind='bar', color='g', rot=0)
plt.title('每小时平均交通流量柱状图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "hour_avg_traffic_bar.png"))
plt.show()

# ===================== 3.7 划分出2016年至2017年数据 =====================
df = data.truncate(before="2016-1-1 00:00:00", after="2017-12-31 23:00:00")
print("="*70)
print("【2016‑2017截取数据前5行】")
print(df.head(5))

# ===================== 3.8 2016至2017年每月平均交通流量对比分析 =====================
# resample重采样到月份，取均值
df1 = df[["traffic_volume"]].resample(rule='ME').mean()
df1 = df1.to_period(freq='M')
print("="*70)
print("【按月重采样均值】")
print(df1.head(5))
# 拆分2016、2017数据
y_data = df1[df1.index < '2017-01-01']["traffic_volume"]
y_data2 = df1[df1.index >= '2017-01-01']["traffic_volume"]
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
y_data.index = month_names
y_data2.index = month_names
df2 = pd.concat([y_data, y_data2], axis=1)
df2.columns = [2016, 2017]
print("="*70)
print("【2016‑2017按月对比表】")
print(df2.head(5))
plt.figure(figsize=(10, 8))
df2.plot.line(subplots=True, title='2016‑2017年按月进行交通流量折线图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "2016_2017_month_compare.png"))
plt.show()


# ===================== 3.9 每周交通总量分析 =====================
week_t = df.resample('W-SUN', closed='right', label='right').sum()
print("="*70)
print("【每周交通流量总和】")
print(week_t.head(5))

plt.figure(figsize=(10, 6))
week_t['traffic_volume'].plot(title='每周交通流量总量折线图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "week_sum_traffic_line.png"))
plt.show()

# ===================== 3.10 升采样到每小时查看平均交通流量分布 =====================
# 升采样h每小时，均值，ffill向前填充空值
hour_resample = df[['traffic_volume']].resample('h').mean()
print("="*70)
print(f"升采样后缺失数目：\n{hour_resample.isnull().sum()}")
hour_t_fill = hour_resample.ffill()
print("="*70)
print("【填充后前5行】")
print(hour_t_fill.head(5))
print(f"填充后缺失数目：\n{hour_t_fill.isnull().sum()}")
hour_t_fill['hour'] = hour_t_fill.index.hour
y = hour_t_fill.groupby('hour')['traffic_volume'].sum()
plt.figure(figsize=(10, 6))
y.plot.bar()
plt.title('每小时总交通流量柱状图')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "result", "resample_hour_sum_bar.png"))
plt.show()


print("\n✅州际公路交通量时间序列全部分析执行完成！图片输出到result文件夹")
