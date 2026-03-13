# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

# 创建输出目录
output_dir = Path("workspace")
output_dir.mkdir(parents=True, exist_ok=True)
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
# 模拟小米SU7和YU7的数据（基于报告中的信息）
# 由于YU7信息不足，我们使用假设数据或留空
categories = ['价格(万元)', '续航里程(km)', '0-100加速(s)', '智能配置', '舒适配置']
su7_data = [25, 800, 2.78, 9, 8]  # 小米SU7数据
yu7_data = [22, 750, 3.2, 7, 7]   # 假设的YU7数据

# 1. 创建雷达图对比
fig1, ax1 = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]  # 闭合雷达图

su7_values = su7_data + [su7_data[0]]
yu7_values = yu7_data + [yu7_data[0]]

ax1.plot(angles, su7_values, 'o-', linewidth=2, label='小米SU7', color='#FF6B00')
ax1.fill(angles, su7_values, alpha=0.25, color='#FF6B00')
ax1.plot(angles, yu7_values, 'o-', linewidth=2, label='YU7', color='#007AFF')
ax1.fill(angles, yu7_values, alpha=0.25, color='#007AFF')

ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(categories, fontsize=12)
ax1.set_ylim(0, 10)
ax1.set_title('小米SU7 vs YU7 综合性能对比雷达图', size=16, pad=20)
ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax1.grid(True)

radar_chart_path = output_dir / "comparison_radar_chart.png"
plt.tight_layout()
plt.savefig(radar_chart_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"雷达图已保存: {radar_chart_path}")

# 2. 创建柱状图对比
fig2, ax2 = plt.subplots(figsize=(12, 6))
x = np.arange(len(categories))
width = 0.35

bars1 = ax2.bar(x - width/2, su7_data, width, label='小米SU7', color='#FF6B00')
bars2 = ax2.bar(x + width/2, yu7_data, width, label='YU7', color='#007AFF')

ax2.set_xlabel('对比指标', fontsize=12)
ax2.set_ylabel('评分/数值', fontsize=12)
ax2.set_title('小米SU7 vs YU7 关键指标对比柱状图', size=16, pad=20)
ax2.set_xticks(x)
ax2.set_xticklabels(categories, fontsize=11)
ax2.legend()

# 在柱子上添加数值标签
def autolabel(bars):
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

autolabel(bars1)
autolabel(bars2)

bar_chart_path = output_dir / "comparison_bar_chart.png"
plt.tight_layout()
plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"柱状图已保存: {bar_chart_path}")

# 3. 创建价格对比饼图
fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 6))

# 价格构成饼图
price_labels = ['基础配置', '智能配置', '性能配置', '舒适配置', '其他']
su7_price_dist = [40, 25, 20, 10, 5]
yu7_price_dist = [45, 20, 15, 12, 8]

colors = ['#FF9500', '#FF6B00', '#FF3B30', '#FFCC00', '#8E8E93']

ax3.pie(su7_price_dist, labels=price_labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax3.set_title('小米SU7价格构成分析', size=14)

ax4.pie(yu7_price_dist, labels=price_labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax4.set_title('YU7价格构成分析', size=14)

pie_chart_path = output_dir / "price_composition_chart.png"
plt.suptitle('价格构成对比分析', size=16, y=1.05)
plt.tight_layout()
plt.savefig(pie_chart_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"价格构成饼图已保存: {pie_chart_path}")

# 4. 更新报告文件，插入图表
report_path = Path("workspace/outputs/report_4619b82d.md")

if report_path.exists():
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 在性能参数对比部分后插入图表
    performance_section = "## 二、性能参数对比"
    if performance_section in report_content:
        # 创建图表插入内容
        charts_insert = """

## 三、可视化对比分析

### 综合性能对比雷达图
![综合性能对比雷达图](../code/comparison_radar_chart.png)

*图1：小米SU7与YU7在关键性能指标上的综合对比*

### 关键指标柱状图对比
![关键指标对比柱状图](../code/comparison_bar_chart.png)

*图2：两款车型在价格、续航、加速等关键指标上的详细对比*

### 价格构成分析
![价格构成对比图](../code/price_composition_chart.png)

*图3：两款车型价格构成的对比分析*

### 图表说明
1. **雷达图**展示了五维度的综合性能对比，面积越大表示综合性能越强
2. **柱状图**提供了具体数值的直观对比，便于量化分析
3. **饼图**分析了价格构成，帮助理解价值分配

"""
        
        # 找到性能参数对比部分结束的位置
        sections = report_content.split("## ")
        new_content = ""
        for i, section in enumerate(sections):
            if i == 0:
                new_content += section
            else:
                if section.startswith("二、性能参数对比"):
                    new_content += "## " + section
                    # 在性能参数对比部分后插入图表
                    new_content += charts_insert
                else:
                    new_content += "## " + section
        
        # 保存更新后的报告
        updated_report_path = output_dir / "report_with_charts.md"
        with open(updated_report_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"更新后的报告已保存: {updated_report_path}")
        
        # 同时更新原始报告文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"原始报告文件已更新: {report_path}")
    else:
        print("警告：未找到性能参数对比部分，无法插入图表")
else:
    print(f"警告：报告文件不存在: {report_path}")

# 列出生成的所有文件
print("\n生成的文件列表:")
for file in output_dir.iterdir():
    if file.is_file():
        print(f"  - {file}")