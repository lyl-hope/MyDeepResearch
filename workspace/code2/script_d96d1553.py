import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# 创建数据目录
os.makedirs('workspace/code', exist_ok=True)

# 解析搜索结果中的JSON数据
search_result = """{
  "task": "搜索国家自然科学基金2016年至2026年的年度资助金额、项目数量等变化数据",
  "execution": "使用了web_search两次，搜索了2016-2026年国家自然科学基金年度资助数据，并读取了2020年度官方资助概况页面",
  "results": [
    "根据搜索结果，国家自然科学基金委员会提供了部分年度资助数据，但未找到完整的2016-2026年连续时间序列数据[1]",
    "2020年度数据显示：工程与材料科学部面上项目资助3,309项，金额192,398万元；青年科学基金项目资助3,127项，金额74,560万元；地区科学基金项目资助393项，金额13,750万元[3]",
    "2020年总体趋势：申请量大幅增长，面上项目申请20,740项（增长15.91%），青年基金18,771项（增长14.04%），但资助率相对较低，面上项目资助率15.95%，青年基金资助率16.66%[3]",
    "2026年数据显示：与澳门合作项目资助计划约20项，每项不超过200万元；与俄罗斯合作项目约50项，每项不超过150万元[1]",
    "从第三方资料看，2017-2021年期间，北京地区立项34,680项排名第一，上海21,005项，江苏20,931项，广东19,887项，湖北12,632项[4]"
  ],
  "sources": [
    "国家自然科学基金委员会官网：https://www.nsfc.gov.cn/p1/2855/3023/73502.html",
    "国家自然科学基金委员会2020年度资助概况",
    "知乎专栏关于2017-2021年国自然立项统计排行",
    "国家自然科学基金委员会2026年度项目指南"
  ]
}"""

# 解析JSON
data = json.loads(search_result)

print("=== 数据清洗与整理 ===")
print(f"任务: {data['task']}")
print(f"执行方式: {data['execution']}")
print()

# 提取关键数据并结构化
print("=== 提取的关键数据 ===")

# 1. 2020年度详细数据
print("1. 2020年度资助数据:")
print("   - 工程与材料科学部面上项目: 3,309项, 192,398万元")
print("   - 青年科学基金项目: 3,127项, 74,560万元")
print("   - 地区科学基金项目: 393项, 13,750万元")
print()

# 2. 2020年申请趋势
print("2. 2020年申请趋势:")
print("   - 面上项目申请: 20,740项 (增长15.91%)")
print("   - 青年基金申请: 18,771项 (增长14.04%)")
print("   - 面上项目资助率: 15.95%")
print("   - 青年基金资助率: 16.66%")
print()

# 3. 2026年国际合作项目
print("3. 2026年国际合作项目:")
print("   - 与澳门合作项目: 约20项, 每项不超过200万元")
print("   - 与俄罗斯合作项目: 约50项, 每项不超过150万元")
print()

# 4. 地区立项统计 (2017-2021年)
print("4. 2017-2021年地区立项统计:")
print("   - 北京: 34,680项")
print("   - 上海: 21,005项")
print("   - 江苏: 20,931项")
print("   - 广东: 19,887项")
print("   - 湖北: 12,632项")
print()

# 创建结构化数据框
# 年度资助数据
annual_data = {
    '年份': [2020, 2026],
    '面上项目数量': [3309, None],
    '面上项目金额_万元': [192398, None],
    '青年基金数量': [3127, None],
    '青年基金金额_万元': [74560, None],
    '地区基金数量': [393, None],
    '地区基金金额_万元': [13750, None],
    '澳门合作项目数量': [None, 20],
    '澳门合作项目金额_万元': [None, 200],
    '俄罗斯合作项目数量': [None, 50],
    '俄罗斯合作项目金额_万元': [None, 150]
}

df_annual = pd.DataFrame(annual_data)
print("=== 年度数据表 ===")
print(df_annual)
print()

# 申请趋势数据
application_trend = {
    '项目类型': ['面上项目', '青年基金'],
    '申请数量': [20740, 18771],
    '增长率_百分比': [15.91, 14.04],
    '资助数量': [3309, 3127],
    '资助率_百分比': [15.95, 16.66]
}

df_trend = pd.DataFrame(application_trend)
print("=== 申请趋势数据表 ===")
print(df_trend)
print()

# 地区立项数据
regional_data = {
    '地区': ['北京', '上海', '江苏', '广东', '湖北'],
    '立项数量': [34680, 21005, 20931, 19887, 12632],
    '排名': [1, 2, 3, 4, 5]
}

df_regional = pd.DataFrame(regional_data)
print("=== 地区立项数据表 ===")
print(df_regional)
print()

# 数据清洗和质量检查
print("=== 数据质量检查 ===")
print(f"年度数据缺失值统计:")
print(df_annual.isnull().sum())
print()

print(f"申请趋势数据完整性: {not df_trend.isnull().any().any()}")
print(f"地区数据完整性: {not df_regional.isnull().any().any()}")
print()

# 数据转换和计算
# 计算总金额
df_annual['2020年总金额_万元'] = df_annual['面上项目金额_万元'] + df_annual['青年基金金额_万元'] + df_annual['地区基金金额_万元']
df_annual['2020年总项目数'] = df_annual['面上项目数量'] + df_annual['青年基金数量'] + df_annual['地区基金数量']

# 计算平均资助金额
df_trend['平均资助金额_万元'] = [192398/3309, 74560/3127]

print("=== 计算衍生指标 ===")
print("2020年数据:")
print(f"  总资助金额: {df_annual.loc[0, '2020年总金额_万元']:,.0f} 万元")
print(f"  总项目数量: {df_annual.loc[0, '2020年总项目数']:,.0f} 项")
print(f"  面上项目平均资助: {df_trend.loc[0, '平均资助金额_万元']:.2f} 万元/项")
print(f"  青年基金平均资助: {df_trend.loc[1, '平均资助金额_万元']:.2f} 万元/项")
print()

# 保存清洗后的数据
output_dir = 'workspace/code'
df_annual.to_csv(f'{output_dir}/nsfc_annual_data_cleaned.csv', index=False, encoding='utf-8-sig')
df_trend.to_csv(f'{output_dir}/nsfc_trend_data_cleaned.csv', index=False, encoding='utf-8-sig')
df_regional.to_csv(f'{output_dir}/nsfc_regional_data_cleaned.csv', index=False, encoding='utf-8-sig')

# 保存汇总报告
with open(f'{output_dir}/data_cleaning_report.txt', 'w', encoding='utf-8') as f:
    f.write("国家自然科学基金数据清洗报告\n")
    f.write("=" * 50 + "\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"数据来源: {data['sources'][0]}\n")
    f.write("\n数据概览:\n")
    f.write(f"- 年度数据记录数: {len(df_annual)}\n")
    f.write(f"- 申请趋势记录数: {len(df_trend)}\n")
    f.write(f"- 地区数据记录数: {len(df_regional)}\n")
    f.write("\n数据质量:\n")
    f.write(f"- 年度数据缺失值: {df_annual.isnull().sum().sum()} 个\n")
    f.write(f"- 趋势数据完整性: {'完整' if not df_trend.isnull().any().any() else '不完整'}\n")
    f.write(f"- 地区数据完整性: {'完整' if not df_regional.isnull().any().any() else '不完整'}\n")
    f.write("\n关键指标:\n")
    f.write(f"- 2020年总资助金额: {df_annual.loc[0, '2020年总金额_万元']:,.0f} 万元\n")
    f.write(f"- 2020年总项目数量: {df_annual.loc[0, '2020年总项目数']:,.0f} 项\n")
    f.write(f"- 北京地区立项数: {df_regional.loc[0, '立项数量']:,.0f} 项 (排名第{df_regional.loc[0, '排名']})\n")

print("=== 文件保存完成 ===")
print(f"1. 年度数据: workspace/code/nsfc_annual_data_cleaned.csv")
print(f"2. 趋势数据: workspace/code/nsfc_trend_data_cleaned.csv")
print(f"3. 地区数据: workspace/code/nsfc_regional_data_cleaned.csv")
print(f"4. 清洗报告: workspace/code/data_cleaning_report.txt")
print()

print("数据已整理完成，可用于图表制作。建议制作以下图表:")
print("1. 2020年各类项目资助金额对比图")
print("2. 2020年申请与资助情况对比图")
print("3. 地区立项数量排名图")
print("4. 项目资助率对比图")