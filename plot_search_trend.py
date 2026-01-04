import io
import json
import re
from datetime import datetime
from io import BytesIO
from typing import Optional
import platform

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import ScalarFormatter, FuncFormatter, FixedLocator
import xlsxwriter

# 设置中文字体支持
def setup_chinese_font():
    """设置 matplotlib 支持中文字体"""
    system = platform.system()
    if system == 'Windows':
        # Windows 系统常用中文字体
        fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi']
    elif system == 'Darwin':  # macOS
        fonts = ['Arial Unicode MS', 'PingFang SC', 'STHeiti']
    else:  # Linux
        fonts = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC']
    
    # 尝试设置字体
    from matplotlib.font_manager import FontManager
    fm = FontManager()
    available_fonts = [f.name for f in fm.ttflist]
    
    for font in fonts:
        if font in available_fonts:
            try:
                plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                return font
            except:
                continue
    
    # 如果所有字体都不可用，至少设置基本配置
    plt.rcParams['axes.unicode_minus'] = False
    # 尝试使用系统默认的sans-serif字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif'] + plt.rcParams['font.sans-serif']
    return None

# 初始化中文字体
_chinese_font = setup_chinese_font()
if _chinese_font:
    print(f"已设置中文字体: {_chinese_font}")
else:
    print("警告: 未找到可用的中文字体，中文可能显示为方框")


# ---------- 安全 sheet 名 ----------
def safe_sheet_name(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name[:31]  # Excel 限制


# ---------- 单关键词画图（返回 BytesIO） ----------
def plot_keyword_search_trend_to_bytes(
    months,
    searches,
    title,
    figsize=(14, 5)
):
    df = pd.DataFrame({
        "month": pd.to_datetime(months),
        "search": searches
    }).sort_values("month")

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(df["month"], df["search"], linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Search Volume")

    ax.grid(True, linestyle="--", alpha=0.4)
    fig.autofmt_xdate()

    # ---------- 保存到内存 ----------
    image_data = io.BytesIO()
    fig.savefig(image_data, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    image_data.seek(0)
    return image_data


# ---------- 从 traffic_cycle_json 绘制所有关键词的趋势图（返回 BytesIO） ----------
def plot_traffic_cycle_json_to_bytes(traffic_cycle_json: dict, figsize=(14, 4)) -> Optional[BytesIO]:
    """
    根据 traffic_cycle_json 绘制所有关键词的搜索趋势图（仅使用近三年数据）
    
    参数
    ------
    traffic_cycle_json : dict
        包含关键词搜索数据的字典，格式：
        {
            "code": "OK",
            "message": None,
            "data": [
                {
                    "keyword": "keyword1",
                    "months": ["2024-01", "2024-02", ...],
                    "searches": [100, 200, ...]
                },
                ...
            ]
        }
    figsize : tuple
        图片大小，默认 (14, 5)
    
    返回
    ------
    io.BytesIO
        图片的二进制数据流
    """
    if not traffic_cycle_json or not isinstance(traffic_cycle_json, dict):
        return None
    
    data_list = traffic_cycle_json.get("data", [])
    if not data_list:
        return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 为每个关键词绘制一条线
    colors = plt.cm.tab10(range(len(data_list)))
    plotted_count = 0  # 记录成功绘制的数据条数
    all_months_dt = []  # 收集所有月份，用于设置横坐标
    
    for idx, item in enumerate(data_list):
        keyword = item.get("keyword", f"Keyword {idx+1}")
        months = item.get("months", [])
        searches = item.get("searches", [])
        
        # 检查数据有效性
        if not months or not searches:
            print(f"  警告: 关键词 {keyword} 的 months 或 searches 为空，跳过")
            continue
        
        if len(months) != len(searches):
            print(f"  警告: 关键词 {keyword} 的 months 和 searches 长度不一致 ({len(months)} vs {len(searches)})，跳过")
            continue
        
        try:
            # 直接取最后36个月的数据（近三年 = 36个月）
            if len(months) > 36:
                filtered_months = months[-36:]
                filtered_searches = searches[-36:]
            else:
                filtered_months = months
                filtered_searches = searches
            
            if not filtered_months:
                print(f"  警告: 关键词 {keyword} 在近三年范围内没有数据，跳过")
                continue
            
            # 转换月份格式
            months_dt = pd.to_datetime(filtered_months)
            df = pd.DataFrame({
                "month": months_dt,
                "search": filtered_searches
            }).sort_values("month")
            
            # 检查搜索量数据是否有效（不能全为0或全为空）
            if df["search"].sum() == 0 and df["search"].max() == 0:
                print(f"  警告: 关键词 {keyword} 的搜索量全为0，跳过")
                continue
            
            # 收集所有月份用于横坐标
            all_months_dt.extend(df["month"].tolist())
            
            # 绘制趋势线
            ax.plot(df["month"], df["search"], 
                   linewidth=2, 
                   label=keyword,
                   color=colors[idx % len(colors)])
            plotted_count += 1
        except Exception as e:
            print(f"  绘制关键词 {keyword} 时出错: {e}")
            continue
    
    # 如果没有任何数据被绘制，返回 None
    if plotted_count == 0:
        plt.close(fig)
        print(f"  警告: 没有有效数据可绘制，data_list 有 {len(data_list)} 项但都无法绘制")
        return None
    
    ax.set_title("核心词搜索趋势图（近三年）", fontsize=14, fontweight='bold')
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("搜索量", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.4)
    
    # 设置纵坐标格式：使用完整数字，不使用科学计数法
    y_formatter = ScalarFormatter(useOffset=False, useMathText=False)
    y_formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(y_formatter)
    
    # 设置横坐标：每个月份都显示标签
    if all_months_dt:
        # 获取所有唯一的月份（已排序）
        unique_months = sorted(set(all_months_dt))
        # 生成完整的月份序列（从最小月份到最大月份，每月一个）
        if unique_months:
            min_month = unique_months[0]
            max_month = unique_months[-1]
            # 生成完整的月份序列
            month_range = pd.date_range(start=min_month, end=max_month, freq='MS')  # MS = Month Start
            # 设置x轴刻度为每个月份
            ax.set_xticks(month_range)
            # 设置x轴标签格式为 "YYYY-MM"
            ax.set_xticklabels([dt.strftime("%Y-%m") for dt in month_range], rotation=45, ha='right', fontsize=8)
    
    # 只有当有图例时才显示
    if plotted_count > 0:
        ax.legend(loc='best', fontsize=8)
    
    # 保存到内存
    image_data = io.BytesIO()
    fig.savefig(image_data, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    image_data.seek(0)
    return image_data


# ---------- 从 sell_trend 数据绘制销量趋势柱状图（返回 BytesIO） ----------
def plot_sales_trend_to_bytes(sell_trend: list, figsize=(10, 5)) -> Optional[BytesIO]:
    """
    根据 sell_trend 数据绘制销量趋势柱状图
    
    参数
    ------
    sell_trend : list
        销量数据列表，格式：
        [{'dk': '202509', 'sales': 0}, {'dk': '202510', 'sales': 0}, ...]
    figsize : tuple
        图片大小，默认 (10, 5)
    
    返回
    ------
    io.BytesIO
        图片的二进制数据流
    """
    if not sell_trend or not isinstance(sell_trend, list):
        return None
    
    # 提取dk和sales，并转换日期格式
    dk_list = []
    dk_formatted_list = []  # 格式化后的日期列表
    sales_list = []
    for item in sell_trend:
        if isinstance(item, dict):
            dk = item.get('dk', '')
            sales = item.get('sales', 0)
            if dk:
                dk_list.append(dk)
                sales_list.append(sales)
                # 将日期格式从 "202509" 转换为 "2025-09"
                try:
                    if len(dk) == 6 and dk.isdigit():
                        # 格式：YYYYMM -> YYYY-MM
                        formatted_dk = f"{dk[:4]}-{dk[4:6]}"
                    elif len(dk) == 7 and '-' in dk:
                        # 已经是 "2025-09" 格式，保持不变
                        formatted_dk = dk
                    else:
                        # 其他格式，保持原样
                        formatted_dk = dk
                except:
                    formatted_dk = dk
                dk_formatted_list.append(formatted_dk)
    
    if not dk_list:
        return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制柱状图
    bars = ax.bar(range(len(dk_list)), sales_list, width=0.6, color='steelblue', edgecolor='navy', linewidth=0.5)
    
    # 在每个柱体上方标注sales值
    for i, (bar, sales) in enumerate(zip(bars, sales_list)):
        height = bar.get_height()
        # 在柱体上方标注数值
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{int(sales)}',
                ha='center', va='bottom', fontsize=8)
    
    # 设置标题和标签
    ax.set_title("销量趋势图", fontsize=12, fontweight='bold')
    ax.set_xlabel("月份", fontsize=10)
    ax.set_ylabel("销量", fontsize=10)
    
    # 设置x轴刻度，使用格式化后的日期
    ax.set_xticks(range(len(dk_list)))
    ax.set_xticklabels(dk_formatted_list, rotation=45, ha='right', fontsize=8)
    
    # 设置纵坐标格式：使用完整数字，不使用科学计数法
    y_formatter = ScalarFormatter(useOffset=False, useMathText=False)
    y_formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(y_formatter)
    
    # 添加网格
    ax.grid(True, linestyle="--", alpha=0.3, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存到内存
    image_data = io.BytesIO()
    fig.savefig(image_data, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    image_data.seek(0)
    return image_data


# ---------- 从价格趋势数据绘制价格趋势图（返回 BytesIO） ----------
def plot_price_trend_to_bytes(price_trend: list, times: list, figsize=(10, 5)) -> Optional[BytesIO]:
    """
    根据价格趋势数据绘制价格趋势折线图（仅使用近三年数据）
    
    参数
    ------
    price_trend : list
        价格数据列表
    times : list
        时间数据列表，格式：["202509", "202510", ...] 或 ["2025-09", "2025-10", ...]
    figsize : tuple
        图片大小，默认 (10, 5)
    
    返回
    ------
    io.BytesIO
        图片的二进制数据流，如果数据无效则返回 None
    """
    if not price_trend or not times or len(price_trend) != len(times):
        return None
    
    # 计算近三年的起始时间
    current_date = datetime.now()
    three_years_ago = current_date.replace(year=current_date.year - 3)
    
    # 在进行绘制之前，将list中的null替换为-1
    processed_price_trend = []
    for price in price_trend:
        if price is None or price == "null" or (isinstance(price, str) and price.lower() == "null"):
            processed_price_trend.append(-1)
        else:
            processed_price_trend.append(price)
    
    # 过滤出近三年的数据，保留所有时间点（包括-1对应的），-1值将形成断点
    filtered_times = []
    filtered_prices = []
    
    for time_str, price in zip(times, processed_price_trend):
        try:
            # 解析时间字符串
            if len(time_str) == 6 and time_str.isdigit():
                # 格式：YYYYMM，转换为该月第一天
                time_dt = datetime.strptime(time_str, "%Y%m")
            elif len(time_str) == 7 and '-' in time_str:
                # 格式：YYYY-MM，转换为该月第一天
                time_dt = datetime.strptime(time_str, "%Y-%m")
            elif len(time_str) == 8 and time_str.isdigit():
                # 格式：YYYYMMDD
                time_dt = datetime.strptime(time_str, "%Y%m%d")
            elif len(time_str) == 10 and '-' in time_str:
                # 格式：YYYY-MM-DD
                time_dt = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                # 其他格式，尝试解析
                time_dt = pd.to_datetime(time_str)
            
            # 只保留近三年的数据
            if time_dt >= three_years_ago:
                filtered_times.append(time_dt)
                # 如果价格为-1，转换为NaN，这样matplotlib会自动跳过，形成断点
                if price == -1:
                    filtered_prices.append(float('nan'))
                else:
                    filtered_prices.append(price)
        except Exception as e:
            print(f"  解析时间字符串 '{time_str}' 时出错: {e}")
            continue
    
    if not filtered_times:
        return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 将数据分成连续的有效数据段，每个段单独绘制
    # 这样可以避免-1值（NaN）被连接，形成断点
    filtered_prices_array = np.array(filtered_prices)
    
    # 找到所有有效数据点的索引（非NaN）
    valid_mask = ~np.isnan(filtered_prices_array)
    
    if not np.any(valid_mask):
        # 如果没有有效数据点，返回None
        return None
    
    # 找到连续的有效数据段
    segments = []
    start_idx = None
    
    for i, is_valid in enumerate(valid_mask):
        if is_valid:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                # 找到一个连续段
                segments.append((start_idx, i - 1))
                start_idx = None
    
    # 处理最后一个段（如果最后一个点是有效的）
    if start_idx is not None:
        segments.append((start_idx, len(valid_mask) - 1))
    
    # 找到第一个和最后一个有效数据点（用于标注）
    first_valid_idx = None
    last_valid_idx = None
    for i, is_valid in enumerate(valid_mask):
        if is_valid:
            if first_valid_idx is None:
                first_valid_idx = i
            last_valid_idx = i
    
    # 绘制每个连续的有效数据段
    for start_idx, end_idx in segments:
        segment_times = filtered_times[start_idx:end_idx + 1]
        segment_prices = filtered_prices[start_idx:end_idx + 1]
        
        # 绘制阶梯图（竖线和横线，不使用直接连接）
        # drawstyle='steps-post' 表示先画横线，然后在点之后画竖线改变值
        ax.plot(segment_times, segment_prices, drawstyle='steps-post', linewidth=1, color='red')
    
    # 在第一个和最后一个数据点处添加文本标注
    if first_valid_idx is not None and last_valid_idx is not None:
        first_time = filtered_times[first_valid_idx]
        first_price = filtered_prices[first_valid_idx]
        last_time = filtered_times[last_valid_idx]
        last_price = filtered_prices[last_valid_idx]
        
        # 标注第一个数据点
        ax.text(first_time, first_price, f'${first_price:.2f}', 
                fontsize=8, ha='left', va='bottom')
        
        # 标注最后一个数据点
        ax.text(last_time, last_price, f'${last_price:.2f}', 
                fontsize=8, ha='left', va='bottom')
    
    # 设置标题和标签
    ax.set_title("价格趋势图", fontsize=12, fontweight='bold')
    ax.set_xlabel("日期", fontsize=10)
    ax.set_ylabel("价格", fontsize=10)
    
    # 手动设置y轴刻度，避免重复的标签
    if filtered_prices:
        # 过滤掉 None 和 NaN 值，确保只处理有效的价格数据
        valid_prices = [p for p in filtered_prices if p is not None and not (isinstance(p, float) and np.isnan(p))]
        if not valid_prices:
            return None
        
        min_price = min(valid_prices)
        max_price = max(valid_prices)
        
        # 固定使用1美元为间隔
        # 从最小价格的整数部分开始，到最大价格的整数部分+1结束，间隔为1
        y_ticks = list(range(int(min_price), int(max_price) + 2))
        
        # 确保刻度点不重复
        y_ticks = sorted(set(y_ticks))
        # 使用FixedLocator固定刻度位置，避免matplotlib自动添加额外刻度
        ax.yaxis.set_major_locator(FixedLocator(y_ticks))
    
    # 设置x轴刻度
    if filtered_times:
        # 获取所有时间点
        unique_times = sorted(set(filtered_times))
        if unique_times:
            min_time = unique_times[0]
            max_time = unique_times[-1]
            
            # 计算时间跨度（月份数）
            # 计算两个日期之间的月份差
            months_diff = (max_time.year - min_time.year) * 12 + (max_time.month - min_time.month)
            
            # 如果时间跨度小于等于2个月，使用日期标注（年-月-日）
            if months_diff <= 2:
                # 按日期去重，每天只保留一个刻度点（使用每天的第一个时间点）
                # 这样可以避免同一天有多个数据点时，x轴显示重复的日期标签
                daily_times = {}
                for dt in unique_times:
                    date_key = dt.date()  # 只使用日期部分（不包含时间）
                    if date_key not in daily_times:
                        daily_times[date_key] = dt
                tick_dates = sorted(daily_times.values())
                ax.set_xticks(tick_dates)
                # 设置x轴标签格式为 "YYYY-MM-DD"（年-月-日）
                ax.set_xticklabels([dt.strftime("%Y-%m-%d") for dt in tick_dates], rotation=45, ha='right', fontsize=8)
            else:
                # 如果时间跨度大于2个月，使用月份标注（年-月）
                # 生成所有需要标注的月份点（每月1日）
                tick_dates = []
                # 从最小日期的月初开始
                current_date = min_time.replace(day=1)
                
                while current_date <= max_time:
                    # 只添加在数据范围内的日期
                    if min_time <= current_date <= max_time:
                        tick_dates.append(current_date)
                    
                    # 移动到下一个月
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1, day=1)
                
                # 去重并排序
                tick_dates = sorted(set(tick_dates))
                
                # 设置x轴刻度
                if tick_dates:
                    ax.set_xticks(tick_dates)
                    # 设置x轴标签格式为 "YYYY-MM"（只显示年-月）
                    ax.set_xticklabels([dt.strftime("%Y-%m") for dt in tick_dates], rotation=45, ha='right', fontsize=8)
                else:
                    # 如果没有生成标注点，使用默认的自动标注
                    ax.tick_params(axis='x', rotation=45)
        else:
            # 如果没有时间点，使用默认的自动标注
            ax.tick_params(axis='x', rotation=45)
    
    # 设置纵坐标格式：显示美元符号，不保留小数
    def dollar_formatter(x, pos):
        """格式化函数：将数字转换为美元格式，不保留小数"""
        return f'${int(x)}'
    
    y_formatter = FuncFormatter(dollar_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    
    # 添加网格
    ax.grid(True, linestyle="--", alpha=0.3)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存到内存
    image_data = io.BytesIO()
    fig.savefig(image_data, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    image_data.seek(0)
    return image_data


# ---------- 核心：json → Excel ----------
def traffic_cycle_json_to_excel(traffic_cycle_json: dict, excel_path: str):
    workbook = xlsxwriter.Workbook(excel_path)

    data_list = traffic_cycle_json.get("data", [])

    for item in data_list:
        keyword = item.get("keyword")
        months = item.get("months")
        searches = item.get("searches")

        if not keyword or not months or not searches:
            print(f"[SKIP] 数据不完整: {keyword}")
            continue
        if len(months) != len(searches):
            print(f"[SKIP] months/searches 不一致: {keyword}")
            continue

        sheet_name = safe_sheet_name(keyword)
        worksheet = workbook.add_worksheet(sheet_name)

        # 标题
        worksheet.write("A1", keyword)

        # 画图（内存）
        image_bytes = plot_keyword_search_trend_to_bytes(
            months=months,
            searches=searches,
            title=f"Search Trend - {keyword}"
        )

        # 插入 Excel（不落地）
        worksheet.insert_image(
            "A3",
            "trend.png",  # 占位名
            {"image_data": image_bytes}
        )

        print(f"[OK] 已写入 Excel: {keyword}")

    workbook.close()


# ---------- main ----------
def main():
    # ===== 示例数据（你真实环境中替换）=====
    traffic_cycle_json = {
        "code": "OK",
        "message": None,
        "data": [
            {
                "keywordCn": "篮球生日装饰品",
                "keyword": "basketball birthday decorations",
                "months": [
                    "2024-01", "2024-02", "2024-03",
                    "2024-04", "2024-05", "2024-06"
                ],
                "searches": [1200, 1500, 900, 3000, 5200, 4800]
            },
            {
                "keywordCn": "篮球派对装饰品",
                "keyword": "basketball party decorations",
                "months": [
                    "2024-01", "2024-02", "2024-03",
                    "2024-04", "2024-05", "2024-06"
                ],
                "searches": [800, 1100, 700, 2400, 4100, 3900]
            }
        ]
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = f"流量周期趋势_{ts}.xlsx"

    traffic_cycle_json_to_excel(
        traffic_cycle_json=traffic_cycle_json,
        excel_path=excel_path
    )

    print(f"\n[DONE] Excel 已生成: {excel_path}")


if __name__ == "__main__":
    main()
