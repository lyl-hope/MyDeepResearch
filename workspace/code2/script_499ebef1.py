import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import rcParams

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建数据
models = ['小米SU7', '小米YU7']

# 价格数据 (万元)
prices = {
    '标准版': [21.59, 25.35],
    'Pro版': [24.59, 27.99],
    'Max版': [29.99, 32.99]
}

# 性能数据
performance = {
    '0-100km/h加速(s)': [5.28, 5.88],  # 标准版对比
    '续航里程(km)': [700, 835],  # 标准版对比
    '电池容量(kWh)': [73.6, 96.3],  # 标准版对比
    '电机功率(kW)': [220, 235]  # 标准版对比
}

# 尺寸数据
dimensions = {
    '长度(mm)': [4997, 4999],
    '宽度(mm)': [1963, 1996],
    '高度(mm)': [1455, 1600],
    '轴距(mm)': [3000, 3000]
}

# 智能配置
smart_features = {
    '激光雷达': ['标配', '标配'],
    '辅助驾驶芯片': ['Orin-X', 'Thor'],
    '算力(TOPS)': [508, 700],
    '中控屏尺寸(英寸)': [16.1, 16.1]
}

# 创建图表
fig = plt.figure(figsize=(18, 12))
fig.suptitle('小米SU7 vs 小米YU7 详细对比分析', fontsize=16, fontweight='bold')

# 1. 价格对比图
ax1 = plt.subplot(2, 3, 1)
x = np.arange(len(prices.keys()))
width = 0.35

for i, (version, price_data) in enumerate(prices.items()):
    ax1.bar(x[i] - width/2, price_data[0], width, label='SU7' if i==0 else '', color='#FF6B00', alpha=0.8)
    ax1.bar(x[i] + width/2, price_data[1], width, label='YU7' if i==0 else '', color='#007AFF', alpha=0.8)

ax1.set_xlabel('版本')
ax1.set_ylabel('价格 (万元)')
ax1.set_title('各版本价格对比')
ax1.set_xticks(x)
ax1.set_xticklabels(prices.keys())
ax1.legend()
ax1.grid(True, alpha=0.3)

# 在柱状图上添加数值
for i, (version, price_data) in enumerate(prices.items()):
    ax1.text(i - width/2, price_data[0] + 0.5, f'{price_data[0]}', ha='center', va='bottom', fontsize=9)
    ax1.text(i + width/2, price_data[1] + 0.5, f'{price_data[1]}', ha='center', va='bottom', fontsize=9)

# 2. 性能雷达图
ax2 = plt.subplot(2, 3, 2, projection='polar')
categories = list(performance.keys())
N = len(categories)

# 标准化数据
values_su7 = [performance[cat][0] for cat in categories]
values_yu7 = [performance[cat][1] for cat in categories]

# 归一化处理
max_values = [max(v1, v2) for v1, v2 in zip(values_su7, values_yu7)]
norm_su7 = [v/max_v for v, max_v in zip(values_su7, max_values)]
norm_yu7 = [v/max_v for v, max_v in zip(values_yu7, max_values)]

# 闭合数据
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
norm_su7 += norm_su7[:1]
norm_yu7 += norm_yu7[:1]
angles += angles[:1]

ax2.plot(angles, norm_su7, 'o-', linewidth=2, label='SU7', color='#FF6B00')
ax2.fill(angles, norm_su7, alpha=0.25, color='#FF6B00')
ax2.plot(angles, norm_yu7, 'o-', linewidth=2, label='YU7', color='#007AFF')
ax2.fill(angles, norm_yu7, alpha=0.25, color='#007AFF')

ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontsize=9)
ax2.set_title('性能参数对比（归一化）')
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax2.grid(True)

# 3. 尺寸对比条形图
ax3 = plt.subplot(2, 3, 3)
x_dim = np.arange(len(dimensions.keys()))
width = 0.35

for i, (dim, data) in enumerate(dimensions.items()):
    ax3.bar(x_dim[i] - width/2, data[0], width, label='SU7' if i==0 else '', color='#FF6B00', alpha=0.8)
    ax3.bar(x_dim[i] + width/2, data[1], width, label='YU7' if i==0 else '', color='#007AFF', alpha=0.8)

ax3.set_xlabel('尺寸参数')
ax3.set_ylabel('数值 (mm)')
ax3.set_title('车身尺寸对比')
ax3.set_xticks(x_dim)
ax3.set_xticklabels(dimensions.keys(), rotation=45, ha='right')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. 智能配置对比表格
ax4 = plt.subplot(2, 3, 4)
ax4.axis('tight')
ax4.axis('off')

table_data = []
for feature, values in smart_features.items():
    table_data.append([feature, values[0], values[1]])

table = ax4.table(cellText=table_data,
                  colLabels=['配置项', 'SU7', 'YU7'],
                  cellLoc='center',
                  loc='center',
                  colWidths=[0.3, 0.3, 0.3])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)

# 设置表格颜色
for i in range(len(table_data) + 1):
    for j in range(3):
        cell = table[i, j]
        if i == 0:  # 标题行
            cell.set_facecolor('#f0f0f0')
            cell.set_text_props(weight='bold')
        elif j == 1:  # SU7列
            cell.set_facecolor('#FFE5D9')
        elif j == 2:  # YU7列
            cell.set_facecolor('#E5F1FF')

ax4.set_title('智能配置对比', fontsize=12, fontweight='bold', pad=20)

# 5. 关键差异总结
ax5 = plt.subplot(2, 3, 5)
ax5.axis('off')

summary_text = """关键差异总结：

🚗 车型定位：
• SU7：豪华运动轿车
• YU7：中大型豪华SUV

💰 价格区间：
• SU7：21.59-52.99万元
• YU7：25.35-32.99万元

🔋 平台技术：
• SU7：400V/800V混合平台
• YU7：全系800V碳化硅平台

🚀 性能特点：
• SU7：极致加速性能（Ultra版1.98s）
• YU7：均衡性能与续航（最长835km）

📱 智能配置：
• SU7：Xiaomi Pilot Max系统
• YU7：英伟达Thor芯片（700TOPS）

📊 市场表现：
• SU7：累计交付超36万台
• YU7：3分钟大定突破20万台"""

ax5.text(0.1, 0.95, summary_text, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#f8f9fa', alpha=0.8))
ax5.set_title('核心差异分析', fontsize=12, fontweight='bold')

# 6. 续航与充电对比
ax6 = plt.subplot(2, 3, 6)

# 续航数据
range_data = {
    '标准版续航(km)': [700, 835],
    '快充功率(kW)': [110, 300],  # 标准版对比
    '充电时间(10-80%)': [0.5, 0.35]  # 小时
}

x_range = np.arange(len(range_data.keys()))
width = 0.35

for i, (item, data) in enumerate(range_data.items()):
    ax6.bar(x_range[i] - width/2, data[0], width, label='SU7' if i==0 else '', color='#FF6B00', alpha=0.8)
    ax6.bar(x_range[i] + width/2, data[1], width, label='YU7' if i==0 else '', color='#007AFF', alpha=0.8)

ax6.set_xlabel('项目')
ax6.set_ylabel('数值')
ax6.set_title('续航与充电能力对比')
ax6.set_xticks(x_range)
ax6.set_xticklabels(range_data.keys(), rotation=45, ha='right')
ax6.legend()
ax6.grid(True, alpha=0.3)

# 添加数值标签
for i, (item, data) in enumerate(range_data.items()):
    ax6.text(x_range[i] - width/2, data[0] + max(data)*0.05, f'{data[0]}', 
             ha='center', va='bottom', fontsize=9)
    ax6.text(x_range[i] + width/2, data[1] + max(data)*0.05, f'{data[1]}', 
             ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('workspace/code/xiaomi_su7_yu7_comparison.png', dpi=300, bbox_inches='tight')
plt.savefig('workspace/code/xiaomi_su7_yu7_comparison.pdf', bbox_inches='tight')

print("图表已保存到 workspace/code/ 目录:")
print("1. xiaomi_su7_yu7_comparison.png")
print("2. xiaomi_su7_yu7_comparison.pdf")

# 同时创建数据表格CSV文件
# 创建综合数据表
comparison_data = {
    '参数类别': ['价格(万元)', '价格(万元)', '价格(万元)', 
               '性能-加速(s)', '性能-续航(km)', '性能-电池(kWh)', '性能-功率(kW)',
               '尺寸-长度(mm)', '尺寸-宽度(mm)', '尺寸-高度(mm)', '尺寸-轴距(mm)',
               '智能-激光雷达', '智能-芯片', '智能-算力(TOPS)', '智能-屏幕(英寸)',
               '续航-标准版(km)', '充电-快充(kW)', '充电-时间(小时)'],
    '版本': ['标准版', 'Pro版', 'Max版',
            '标准版', '标准版', '标准版', '标准版',
            '全系', '全系', '全系', '全系',
            '全系', '全系', '全系', '全系',
            '标准版', '标准版', '标准版'],
    '小米SU7': [21.59, 24.59, 29.99,
               5.28, 700, 73.6, 220,
               4997, 1963, 1455, 3000,
               '标配', 'Orin-X', 508, 16.1,
               700, 110, 0.5],
    '小米YU7': [25.35, 27.99, 32.99,
               5.88, 835, 96.3, 235,
               4999, 1996, 1600, 3000,
               '标配', 'Thor', 700, 16.1,
               835, 300, 0.35]
}

df = pd.DataFrame(comparison_data)
csv_path = 'workspace/code/xiaomi_comparison_data.csv'
df.to_csv(csv_path, index=False, encoding='utf-8-sig')

print(f"3. {csv_path}")
print("\n数据表格内容预览:")
print(df.head(10))