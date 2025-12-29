import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import pymannkendall as mk


# =========================================================
# 时间解析
# =========================================================
def parse_time(t):
    if isinstance(t, datetime):
        return t
    return datetime.strptime(t, "%Y-%m-%d %H:%M")


# =========================================================
# price 规范化（支持 list / tuple / 标量）
# =========================================================
def normalize_price(p):
    if p is None:
        return None

    # 如果是列表，取最后一个有效值
    if isinstance(p, (list, tuple)):
        for v in reversed(p):
            if v is None:
                continue
            try:
                return float(v)
            except Exception:
                continue
        return None

    try:
        return float(p)
    except Exception:
        return None


# =========================================================
# 清洗数据
# =========================================================
def filter_valid_data(prices, times):
    clean_prices = []
    clean_times = []

    for p, t in zip(prices, times):
        if t is None:
            continue

        try:
            t = parse_time(t)
        except Exception:
            continue

        p_val = normalize_price(p)
        if p_val is None:
            continue

        clean_prices.append(p_val)
        clean_times.append(t)

    return clean_prices, clean_times


# =========================================================
# 选择最近 N 天
# =========================================================
def select_last_n_days(prices, times, days=7):
    if not prices:
        return [], []

    max_time = max(times)
    start_time = max_time - timedelta(days=days)

    new_prices = []
    new_times = []

    for p, t in zip(prices, times):
        if t >= start_time:
            new_prices.append(p)
            new_times.append(t)

    return new_prices, new_times


# =========================================================
# 根据销量数据筛选有销量的月份对应的价格
# =========================================================
def filter_prices_by_sales_months(prices, times, sales_data):
    """
    根据销量数据，只选择有销量的月份对应的价格数据
    
    参数:
    prices: 价格列表
    times: 时间列表（datetime对象或字符串）
    sales_data: 销量数据列表，格式为 [{'dk': 'YYYYMM', 'sales': int}, ...]
    
    返回:
    filtered_prices: 筛选后的价格列表
    filtered_times: 筛选后的时间列表
    """
    if not sales_data or not isinstance(sales_data, list):
        return prices, times
    
    # 提取有销量的月份（销量大于0的月份）
    sales_months = set()
    for item in sales_data:
        if isinstance(item, dict):
            dk = item.get('dk')
            sales = item.get('sales', 0)
            if dk and sales and sales > 0:
                # dk格式为 'YYYYMM'，转换为年月用于匹配
                try:
                    sales_months.add(dk)  # 保留原始格式 'YYYYMM'
                except:
                    pass
    
    if not sales_months:
        return prices, times
    
    # 筛选价格和时间数据
    filtered_prices = []
    filtered_times = []
    
    for p, t in zip(prices, times):
        # 将时间转换为 'YYYYMM' 格式进行匹配
        try:
            if isinstance(t, datetime):
                time_str = t.strftime('%Y%m')
            elif isinstance(t, str):
                # 尝试解析时间字符串
                if len(t) >= 6:
                    # 如果是 'YYYYMM' 格式
                    if len(t) == 6 and t.isdigit():
                        time_str = t
                    # 如果是 'YYYY-MM' 格式
                    elif '-' in t and len(t) >= 7:
                        time_str = t.replace('-', '')[:6]
                    # 如果是 'YYYY-MM-DD' 格式
                    elif len(t) >= 10 and '-' in t:
                        time_str = t.replace('-', '')[:6]
                    else:
                        # 尝试解析为datetime
                        try:
                            dt = datetime.strptime(t[:10], '%Y-%m-%d')
                            time_str = dt.strftime('%Y%m')
                        except:
                            continue
                else:
                    continue
            else:
                continue
            
            # 如果该月份有销量，则保留该价格数据
            if time_str in sales_months:
                filtered_prices.append(p)
                filtered_times.append(t)
        except Exception as e:
            continue
    
    return filtered_prices, filtered_times


# =========================================================
# 清洗价格和时间数据（兼容旧接口）
# =========================================================
def clean_price_and_time(times: List[str], prices: List):
    """
    清洗价格和时间数据（排除None值，转换为float）
    兼容旧接口，内部调用 filter_valid_data
    """
    clean_prices,clean_times,  = filter_valid_data(prices, times)
    return clean_times, clean_prices


# =========================================================
# 主函数：趋势分类
# =========================================================
def classify_price_trend(
    prices,
    times,
    sales_data=None,
    days=60,
    alpha=0.05,
    vol_threshold=0.05,
    quantile_level=0.9,
):
    """
    返回:
        label: 上升 / 下降 / 平稳 / 波动 / unknown
        detail: dict (调试信息)
    
    参数:
        prices: 价格列表
        times: 时间列表
        sales_data: 销量数据列表，格式为 [{'dk': 'YYYYMM', 'sales': int}, ...]
                   如果提供，则只使用有销量的月份对应的价格数据
    """

    # ---------- 1. 清洗 ----------
    prices, times = filter_valid_data(prices, times)

    if len(prices) < 3:
        return "unknown", {"reason": "数据太少"}

    # ---------- 2. 排序 ----------
    pairs = sorted(zip(times, prices), key=lambda x: x[0])
    times = [p[0] for p in pairs]
    prices = [p[1] for p in pairs]

    # ---------- 2.5. 根据销量数据筛选有销量的月份对应的价格 ----------
    if sales_data:
        prices, times = filter_prices_by_sales_months(prices, times, sales_data)
        if len(prices) < 3:
            return "unknown", {"reason": "有销量的月份对应的价格数据太少"}

    # ---------- 3. 最近 N 天（如果提供了销量数据，则使用所有筛选后的数据） ----------
    if sales_data:
        # 如果使用了销量筛选，则使用所有筛选后的数据，不再限制天数
        recent_prices = np.array(prices)
        recent_times = times
    else:
        # 如果没有销量数据，则使用原来的逻辑：选择最近N天
        recent_prices, recent_times = select_last_n_days(prices, times, days)
        if len(recent_prices) < 4:
            return "unknown", {"reason": f"近{days}天数据不足"}
        recent_prices = np.array(recent_prices)

    if len(recent_prices) < 4:
        return "unknown", {"reason": "分析数据不足"}

    # ---------- 4. 分位数 ----------
    high_q = np.percentile(prices, quantile_level * 100)
    low_q = np.percentile(prices, (1 - quantile_level) * 100)

    latest = recent_prices[-1]

    high_position = latest >= 0.8 * high_q
    low_position = latest <= 1.2 * low_q

    # ---------- 5. MK 趋势 ----------
    mk_result = mk.original_test(recent_prices)

    has_trend = mk_result.p < alpha
    trend_dir = mk_result.trend  # increasing / decreasing / no trend

    # ---------- 6. 波动 ----------
    volatility = np.std(recent_prices) / (np.mean(recent_prices) + 1e-9)
    vol_ok = volatility < vol_threshold
    vol_ok = True
    # ---------- 7. 末尾确认 ----------
    mean_recent = np.mean(recent_prices)
    end_up = latest > mean_recent
    end_down = latest < mean_recent

    # ---------- 8. 分类 ----------
    if has_trend and trend_dir == "increasing" and vol_ok and end_up and high_position:
        label = "上升"

    elif has_trend and trend_dir == "decreasing" and vol_ok and end_down and low_position:
        label = "下降"

    elif volatility >= vol_threshold:
        label = "波动"

    else:
        label = "平稳"

    detail = {
        "latest_price": latest,
        "high_quantile": high_q,
        "low_quantile": low_q,
        "volatility": volatility,
        "vol_ok": vol_ok,
        "mk_trend": mk_result.trend,
        "mk_p": mk_result.p,
        "end_up": end_up,
        "end_down": end_down,
        "window_size": len(recent_prices),
    }

    return label, detail
