# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os

# 创建输出目录
output_dir = "workspace"
os.makedirs(output_dir, exist_ok=True)

# 小米SU7和小米YU7数据
models = ['小米SU7', '小米YU7']

# 价格数据（万元）
prices = {
    '最低价': [21.59, 25.35],
    '最高价': [29.99, 32.99],
    '平均价': [(21.59+29.99)/2, (25.35+32.99)/2]
}

# 性能数据
performance = {
    '零百加速(s)': [2.78, 3.23],  # 最快版本
    'CLTC续航(km)': [830, 835],  # 最长续航
    '车身长度(mm)': [4997, 4999],
    '轴距(mm)': [3000, 3000],
    '车身高度(mm)': [1445, 1600]  # 添加高度数据
}

# 创建图表
fig = plt.figure(figsize=(16, 12))
fig.suptitle('小米SU7 vs 小米YU7 车型对比分析', fontsize=18, fontweight='bold')

# 1. 价格对比图
ax1 = plt.subplot(2, 2, 1)
x = np.arange(len(models))
width = 0.25

bars1 = ax1.bar(x - width, prices['最低价'], width, label='最低价', color='#FF6B6B')
bars2 = ax1.bar(x, prices['平均价'], width, label='平均价', color='#4ECDC4')
bars3 = ax1.bar(x + width, prices['最高价'], width, label='最高价', color='#45B7D1')

ax1.set_xlabel('车型', fontsize=12)
ax1.set_ylabel('价格 (万元)', fontsize=12)
ax1.set_title('价格对比', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 在柱子上添加数值
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10)

# 2. 性能雷达图（修复除零错误）
ax2 = plt.subplot(2, 2, 2, projection='polar')

# 性能指标
categories = ['加速性能', '续航能力', '车身长度', '车身高度']
N = len(categories)

# 数据归一化（0-1范围），处理相同值的情况
def safe_normalize(values):
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [0.5] * len(values)  # 如果所有值相同，返回中间值
    return [(v - min_val) / (max_val - min_val) for v in values]

# 注意：加速时间越小越好，所以需要特殊处理
accel_values = performance['零百加速(s)']
accel_norm = [1 - (p - min(accel_values)) / (max(accel_values) - min(accel_values)) 
              if max(accel_values) != min(accel_values) else 0.5 
              for p in accel_values]

range_norm = safe_normalize(performance['CLTC续航(km)'])
length_norm = safe_normalize(performance['车身长度(mm)'])
height_norm = safe_normalize(performance['车身高度(mm)'])

# 创建雷达图数据
values_su7 = [accel_norm[0], range_norm[0], length_norm[0], height_norm[0]]
values_yu7 = [accel_norm[1], range_norm[1], length_norm[1], height_norm[1]]

# 闭合数据
values_su7 = values_su7 + values_su7[:1]
values_yu7 = values_yu7 + values_yu7[:1]

# 角度设置
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

# 绘制雷达图
ax2.plot(angles, values_su7, 'o-', linewidth=2, label='小米SU7', color='#FF6B6B')
ax2.fill(angles, values_su7, alpha=0.25, color='#FF6B6B')
ax2.plot(angles, values_yu7, 'o-', linewidth=2, label='小米YU7', color='#4ECDC4')
ax2.fill(angles, values_yu7, alpha=0.25, color='#4ECDC4')

# 设置雷达图标签
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontsize=11)
ax2.set_ylim(0, 1)
ax2.set_title('性能雷达图对比', fontsize=14, fontweight='bold', pad=20)
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax2.grid(True)

# 3. 续航和加速散点图
ax3 = plt.subplot(2, 2, 3)

# 实际数据点
ax3.scatter(performance['零百加速(s)'][0], performance['CLTC续航(km)'][0], 
           s=200, color='#FF6B6B', alpha=0.7, label='小米SU7', edgecolors='black')
ax3.scatter(performance['零百加速(s)'][1], performance['CLTC续航(km)'][1], 
           s=200, color='#4ECDC4', alpha=0.7, label='小米YU7', edgecolors='black')

# 添加数据标签
for i, model in enumerate(models):
    ax3.annotate(f'{model}\n加速: {performance["零百加速(s)"][i]}s\n续航: {performance["CLTC续航(km)"][i]}km',
                xy=(performance['零百加速(s)'][i], performance['CLTC续航(km)'][i]),
                xytext=(10, 10), textcoords='offset points',
                fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

ax3.set_xlabel('零百加速时间 (秒)', fontsize=12)
ax3.set_ylabel('CLTC续航里程 (km)', fontsize=12)
ax3.set_title('加速与续航性能对比', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()

# 反转x轴（加速时间越小越好）
ax3.invert_xaxis()

# 4. 配置对比表格
ax4 = plt.subplot(2, 2, 4)
ax4.axis('tight')
ax4.axis('off')

# 配置数据
config_data = [
    ['车型定位', '中大型纯电轿跑', '中大型豪华智能SUV'],
    ['车身尺寸', '4997×1963×1445mm', '4999×1996×1600mm'],
    ['轴距', '3000mm', '3000mm'],
    ['价格区间', '21.59-29.99万元', '25.35-32.99万元'],
    ['版本配置', '标准版/Pro版/Max版', '后驱标准版/四驱Pro版/四驱Max版'],
    ['驱动形式', '单电机后驱/双电机四驱', '单电机后驱/双电机四驱'],
    ['智能配置', '激光雷达+700TOPS+Xiaomi HAD', '激光雷达+700TOPS+澎湃OS'],
    ['技术平台', '常规平台', '800V碳化硅高压平台']
]

# 创建表格
table = ax4.table(cellText=config_data,
                  colLabels=['配置项', '小米SU7', '小米YU7'],
                  cellLoc='left',
                  loc='center',
                  colWidths=[0.25, 0.35, 0.35])

# 设置表格样式
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.8)

# 设置标题行样式
for i in range(3):
    table[(0, i)].set_facecolor('#4ECDC4')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置交替行颜色
for i in range(1, len(config_data)+1):
    for j in range(3):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#F5F5F5')

ax4.set_title('详细配置对比', fontsize=14, fontweight='bold', pad=20)

# 调整布局
plt.tight_layout(rect=[0, 0, 1, 0.96])

# 保存图表
chart_path = os.path.join(output_dir, 'xiaomi_cars_comparison.png')
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"对比图表已生成并保存到: {chart_path}")
print(f"文件大小: {os.path.getsize(chart_path) / 1024:.1f} KB")

# 生成数据文件
data_path = os.path.join(output_dir, 'xiaomi_cars_data.csv')
with open(data_path, 'w', encoding='utf-8') as f:
    f.write('车型,最低价(万元),最高价(万元),平均价(万元),零百加速(s),CLTC续航(km),车身长度(mm),车身高度(mm),轴距(mm)\n')
    f.write(f'小米SU7,{prices["最低价"][0]},{prices["最高价"][0]},{prices["平均价"][0]:.2f},')
    f.write(f'{performance["零百加速(s)"][0]},{performance["CLTC续航(km)"][0]},')
    f.write(f'{performance["车身长度(mm)"][0]},{performance["车身高度(mm)"][0]},{performance["轴距(mm)"][0]}\n')
    f.write(f'小米YU7,{prices["最低价"][1]},{prices["最高价"][1]},{prices["平均价"][1]:.2f},')
    f.write(f'{performance["零百加速(s)"][1]},{performance["CLTC续航(km)"][1]},')
    f.write(f'{performance["车身长度(mm)"][1]},{performance["车身高度(mm)"][1]},{performance["轴距(mm)"][1]}\n')

print(f"数据文件已保存到: {data_path}")

# 生成简单的文本对比
text_path = os.path.join(output_dir, 'comparison_summary.txt')
with open(text_path, 'w', encoding='utf-8') as f:
    f.write("小米SU7与小米YU7对比分析总结\n")
    f.write("=" * 50 + "\n\n")
    
    f.write("1. 价格对比:\n")
    f.write(f"   小米SU7: {prices['最低价'][0]} - {prices['最高价'][0]} 万元\n")
    f.write(f"   小米YU7: {prices['最低价'][1]} - {prices['最高价'][1]} 万元\n")
    f.write(f"   YU7比SU7贵约 {prices['最低价'][1]-prices['最低价'][0]:.1f} 万元起\n\n")
    
    f.write("2. 性能对比:\n")
    f.write(f"   加速性能: SU7 ({performance['零百加速(s)'][0]}s) 优于 YU7 ({performance['零百加速(s)'][1]}s)\n")
    f.write(f"   续航里程: YU7 ({performance['CLTC续航(km)'][1]}km) 略优于 SU7 ({performance['CLTC续航(km)'][0]}km)\n")
    f.write(f"   车身尺寸: SU7: {performance['车身长度(mm)'][0]}×{performance['车身高度(mm)'][0]}mm\n")
    f.write(f"             YU7: {performance['车身长度(mm)'][1]}×{performance['车身高度(mm)'][1]}mm (更高更宽)\n\n")
    
    f.write("3. 配置特点:\n")
    f.write("   小米SU7: 运动轿跑定位，加速性能突出，适合追求驾驶乐趣的用户\n")
    f.write("   小米YU7: 豪华SUV定位，800V平台技术先进，空间更大，适合家庭用户\n\n")
    
    f.write("4. 智能配置:\n")
    f.write("   两者均标配激光雷达和700TOPS算力芯片\n")
    f.write("   SU7使用Xiaomi HAD辅助驾驶系统\n")
    f.write("   YU7使用澎湃OS智能座舱系统\n\n")
    
    f.write("5. 市场定位:\n")
    f.write("   小米SU7: 对标特斯拉Model 3、蔚来ET5等运动型纯电轿车\n")
    f.write("   小米YU7: 对标理想L7、问界M7等中大型智能SUV\n")

print(f"文本总结已保存到: {text_path}")

# 生成额外的柱状图对比
fig2, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左侧：关键参数对比
ax1 = axes[0]
categories = ['最低价(万元)', '最高价(万元)', '加速(s)', '续航(km)']
su7_values = [prices['最低价'][0], prices['最高价'][0], 
              performance['零百加速(s)'][0], performance['CLTC续航(km)'][0]]
yu7_values = [prices['最低价'][1], prices['最高价'][1], 
              performance['零百加速(s)'][1], performance['CLTC续航(km)'][1]]

x = np.arange(len(categories))
width = 0.35

bars1 = ax1.bar(x - width/2, su7_values, width, label='小米SU7', color='#FF6B6B')
bars2 = ax1.bar(x + width/2, yu7_values, width, label='小米YU7', color='#4ECDC4')

ax1.set_xlabel('参数类别', fontsize=12)
ax1.set_ylabel('数值', fontsize=12)
ax1.set_title('关键参数对比', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 添加数值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)

# 右侧：尺寸对比
ax2 = axes[1]
size_categories = ['车身长度(mm)', '车身高度(mm)', '轴距(mm)']
su7_sizes = [performance['车身长度(mm)'][0], performance['车身高度(mm)'][0], performance['轴距(mm)'][0]]
yu7_sizes = [performance['车身长度(mm)'][1], performance['车身高度(mm)'][1], performance['轴距(mm)'][1]]

x2 = np.arange(len(size_categories))
bars3 = ax2.bar(x2 - width/2, su7_sizes, width, label='小米SU7', color='#FF6B6B')
bars4 = ax2.bar(x2 + width/2, yu7_sizes, width, label='小米YU7', color='#4ECDC4')

ax2.set_xlabel('尺寸参数', fontsize=12)
ax2.set_ylabel('毫米(mm)', fontsize=12)
ax2.set_title('车身尺寸对比', fontsize=14, fontweight='bold')
ax2.set_xticks(x2)
ax2.set_xticklabels(size_categories)
ax2.legend()
ax2.grid(True, alpha=0.3)

# 添加数值标签
for bars in [bars3, bars4]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
simple_chart_path = os.path.join(output_dir, 'xiaomi_cars_simple_comparison.png')
plt.savefig(simple_chart_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"简化对比图表已保存到: {simple_chart_path}")

# 列出所有生成的文件
print("\n生成的文件列表:")
print(f"1. 综合对比图表: {chart_path}")
print(f"2. 简化对比图表: {simple_chart_path}")
print(f"3. 数据文件: {data_path}")
print(f"4. 文本总结: {text_path}")