import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib import rcParams

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = 'workspace/code'
os.makedirs(output_dir, exist_ok=True)

# 加载清洗后的数据
df_annual = pd.read_csv(f'{output_dir}/nsfc_annual_data_cleaned.csv')
df_trend = pd.read_csv(f'{output_dir}/nsfc_trend_data_cleaned.csv')
df_regional = pd.read_csv(f'{output_dir}/nsfc_regional_data_cleaned.csv')

print("=== 数据加载完成 ===")
print(f"年度数据形状: {df_annual.shape}")
print(f"趋势数据形状: {df_trend.shape}")
print(f"地区数据形状: {df_regional.shape}")
print()

# 图表1: 2020年各类项目资助金额对比图
print("正在生成图表1: 2020年各类项目资助金额对比图...")

# 提取2020年数据
annual_2020 = df_annual[df_annual['年份'] == 2020].iloc[0]

# 准备数据
project_types = ['面上项目', '青年基金', '地区基金']
funding_amounts = [
    annual_2020['面上项目金额_万元'],
    annual_2020['青年基金金额_万元'],
    annual_2020['地区基金金额_万元']
]
project_counts = [
    annual_2020['面上项目数量'],
    annual_2020['青年基金数量'],
    annual_2020['地区基金数量']
]

# 创建子图
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左侧：资助金额柱状图
bars1 = ax1.bar(project_types, funding_amounts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax1.set_title('2020年国家自然科学基金各类项目资助金额对比', fontsize=14, fontweight='bold')
ax1.set_ylabel('资助金额（万元）', fontsize=12)
ax1.set_xlabel('项目类型', fontsize=12)
ax1.grid(axis='y', alpha=0.3)

# 在柱子上添加数值标签
for i, (bar, amount) in enumerate(zip(bars1, funding_amounts)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 5000,
             f'{amount:,.0f}',
             ha='center', va='bottom', fontsize=10)

# 右侧：项目数量柱状图
bars2 = ax2.bar(project_types, project_counts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax2.set_title('2020年国家自然科学基金各类项目资助数量对比', fontsize=14, fontweight='bold')
ax2.set_ylabel('项目数量（项）', fontsize=12)
ax2.set_xlabel('项目类型', fontsize=12)
ax2.grid(axis='y', alpha=0.3)

# 在柱子上添加数值标签
for i, (bar, count) in enumerate(zip(bars2, project_counts)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 100,
             f'{count:,.0f}',
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
chart1_path = f'{output_dir}/chart1_2020_funding_comparison.png'
plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"图表1已保存: {chart1_path}")

# 图表2: 2020年申请与资助情况对比图
print("正在生成图表2: 2020年申请与资助情况对比图...")

fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左侧：申请与资助数量对比
x = np.arange(len(df_trend['项目类型']))
width = 0.35

bars1 = ax1.bar(x - width/2, df_trend['申请数量'], width, label='申请数量', color='#1f77b4')
bars2 = ax1.bar(x + width/2, df_trend['资助数量'], width, label='资助数量', color='#ff7f0e')

ax1.set_xlabel('项目类型', fontsize=12)
ax1.set_ylabel('项目数量（项）', fontsize=12)
ax1.set_title('2020年申请与资助数量对比', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(df_trend['项目类型'])
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 添加数值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 500,
                f'{height:,.0f}',
                ha='center', va='bottom', fontsize=9)

# 右侧：资助率柱状图
colors = ['#1f77b4', '#ff7f0e']
bars3 = ax2.bar(df_trend['项目类型'], df_trend['资助率_百分比'], color=colors)
ax2.set_xlabel('项目类型', fontsize=12)
ax2.set_ylabel('资助率（%）', fontsize=12)
ax2.set_title('2020年各类项目资助率对比', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar, rate in zip(bars3, df_trend['资助率_百分比']):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
            f'{rate:.2f}%',
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
chart2_path = f'{output_dir}/chart2_2020_application_funding_comparison.png'
plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"图表2已保存: {chart2_path}")

# 图表3: 地区立项数量排名图
print("正在生成图表3: 地区立项数量排名图...")

# 按立项数量排序
df_regional_sorted = df_regional.sort_values('立项数量', ascending=True)

fig3, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(df_regional_sorted['地区'], df_regional_sorted['立项数量'], 
               color=plt.cm.viridis(np.linspace(0.2, 0.8, len(df_regional_sorted))))

ax.set_xlabel('立项数量（项）', fontsize=12)
ax.set_title('2017-2021年国家自然科学基金地区立项数量排名', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# 在条形右侧添加数值和排名
for i, (bar, count, rank) in enumerate(zip(bars, df_regional_sorted['立项数量'], df_regional_sorted['排名'])):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
            f'{count:,.0f}项 (第{int(rank)}名)',
            va='center', fontsize=10)

plt.tight_layout()
chart3_path = f'{output_dir}/chart3_regional_funding_ranking.png'
plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"图表3已保存: {chart3_path}")

# 图表4: 综合对比图 - 资助金额、数量、资助率
print("正在生成图表4: 综合对比图...")

fig4, axes = plt.subplots(2, 2, figsize=(14, 10))

# 子图1: 资助金额饼图
ax1 = axes[0, 0]
ax1.pie(funding_amounts, labels=project_types, autopct='%1.1f%%', 
        colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax1.set_title('2020年各类项目资助金额占比', fontsize=12, fontweight='bold')

# 子图2: 项目数量饼图
ax2 = axes[0, 1]
ax2.pie(project_counts, labels=project_types, autopct='%1.1f%%',
        colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax2.set_title('2020年各类项目资助数量占比', fontsize=12, fontweight='bold')

# 子图3: 平均资助金额对比
ax3 = axes[1, 0]
avg_funding = [amount/count for amount, count in zip(funding_amounts, project_counts)]
bars3 = ax3.bar(project_types, avg_funding, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax3.set_title('2020年各类项目平均资助金额', fontsize=12, fontweight='bold')
ax3.set_ylabel('平均资助金额（万元/项）', fontsize=11)
ax3.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar, avg in zip(bars3, avg_funding):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{avg:.2f}',
            ha='center', va='bottom', fontsize=10)

# 子图4: 资助率对比
ax4 = axes[1, 1]
funding_rates = df_trend['资助率_百分比'].values
bars4 = ax4.bar(df_trend['项目类型'], funding_rates, color=['#1f77b4', '#ff7f0e'])
ax4.set_title('2020年各类项目资助率对比', fontsize=12, fontweight='bold')
ax4.set_ylabel('资助率（%）', fontsize=11)
ax4.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar, rate in zip(bars4, funding_rates):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{rate:.2f}%',
            ha='center', va='bottom', fontsize=10)

plt.suptitle('国家自然科学基金2020年资助情况综合分析', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
chart4_path = f'{output_dir}/chart4_comprehensive_analysis.png'
plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"图表4已保存: {chart4_path}")

# 图表5: 地区立项分布图（进阶版）
print("正在生成图表5: 地区立项分布图...")

fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左侧：地区立项数量柱状图（带排名）
x_pos = np.arange(len(df_regional))
bars5 = ax1.bar(x_pos, df_regional['立项数量'], 
                color=plt.cm.plasma(np.linspace(0.2, 0.8, len(df_regional))))
ax1.set_xlabel('地区', fontsize=12)
ax1.set_ylabel('立项数量（项）', fontsize=12)
ax1.set_title('2017-2021年各地区立项数量分布', fontsize=14, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(df_regional['地区'], rotation=45, ha='right')
ax1.grid(axis='y', alpha=0.3)

# 添加数值和排名标签
for i, (bar, count, rank) in enumerate(zip(bars5, df_regional['立项数量'], df_regional['排名'])):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 500,
            f'{count:,.0f}\n(第{int(rank)}名)',
            ha='center', va='bottom', fontsize=9)

# 右侧：地区占比饼图
ax2.pie(df_regional['立项数量'], labels=df_regional['地区'], autopct='%1.1f%%',
        colors=plt.cm.plasma(np.linspace(0.2, 0.8, len(df_regional))))
ax2.set_title('各地区立项数量占比', fontsize=14, fontweight='bold')

plt.tight_layout()
chart5_path = f'{output_dir}/chart5_regional_distribution.png'
plt.savefig(chart5_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"图表5已保存: {chart5_path}")

# 生成数据汇总报告
print("\n=== 数据可视化完成 ===")
print(f"共生成5个图表文件:")
print(f"1. {chart1_path}")
print(f"2. {chart2_path}")
print(f"3. {chart3_path}")
print(f"4. {chart4_path}")
print(f"5. {chart5_path}")

# 计算关键指标
total_funding_2020 = sum(funding_amounts)
total_projects_2020 = sum(project_counts)
avg_funding_per_project = total_funding_2020 / total_projects_2020

print(f"\n=== 关键指标汇总 ===")
print(f"2020年总资助金额: {total_funding_2020:,.0f} 万元")
print(f"2020年总项目数量: {total_projects_2020:,.0f} 项")
print(f"平均每项资助金额: {avg_funding_per_project:.2f} 万元/项")
print(f"面上项目资助率: {df_trend.loc[0, '资助率_百分比']:.2f}%")
print(f"青年基金资助率: {df_trend.loc[1, '资助率_百分比']:.2f}%")
print(f"北京地区立项数最高: {df_regional.loc[0, '立项数量']:,.0f} 项")

# 保存汇总报告
summary_path = f'{output_dir}/chart_generation_summary.txt'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("国家自然科学基金数据可视化报告\n")
    f.write("=" * 50 + "\n")
    f.write(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("生成的图表文件:\n")
    f.write(f"1. {chart1_path}\n")
    f.write("   描述: 2020年各类项目资助金额和数量对比图\n\n")
    
    f.write(f"2. {chart2_path}\n")
    f.write("   描述: 2020年申请与资助情况对比图\n\n")
    
    f.write(f"3. {chart3_path}\n")
    f.write("   描述: 2017-2021年地区立项数量排名图\n\n")
    
    f.write(f"4. {chart4_path}\n")
    f.write("   描述: 2020年资助情况综合分析图\n\n")
    
    f.write(f"5. {chart5_path}\n")
    f.write("   描述: 地区立项分布图\n\n")
    
    f.write("关键数据指标:\n")
    f.write(f"- 2020年总资助金额: {total_funding_2020:,.0f} 万元\n")
    f.write(f"- 2020年总项目数量: {total_projects_2020:,.0f} 项\n")
    f.write(f"- 平均每项资助金额: {avg_funding_per_project:.2f} 万元/项\n")
    f.write(f"- 面上项目资助率: {df_trend.loc[0, '资助率_百分比']:.2f}%\n")
    f.write(f"- 青年基金资助率: {df_trend.loc[1, '资助率_百分比']:.2f}%\n")
    f.write(f"- 北京地区立项数最高: {df_regional.loc[0, '立项数量']:,.0f} 项\n")

print(f"\n汇总报告已保存: {summary_path}")
print("\n所有图表已生成完成！")