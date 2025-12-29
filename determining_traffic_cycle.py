from typing import List, Sequence, Dict, Any, Optional, Union, Tuple
from collections import Counter

import pandas as pd


def _monthly_effective_contribution(series: pd.Series) -> pd.Series:
    """计算每个月份的有效季节性贡献度（0-1 之间，按月度归一化）。"""
    # 年内标准化
    normalized = series / series.groupby(series.index.year).transform("mean")

    # 只保留高于整体均值的“超额”部分
    mean_val = normalized.mean()
    excess = (normalized - mean_val).clip(lower=0)

    # 按月份聚合超额贡献
    monthly_contrib = excess.groupby(series.index.month).sum()

    if monthly_contrib.sum() == 0:
        return monthly_contrib * 0

    # 归一化到 0-1
    return monthly_contrib / monthly_contrib.sum()


def _find_peak_windows(
        monthly_ratio: pd.Series,
        window_sizes: Optional[List[int]] = None,
        min_score: float = 0.05,
        min_ratio: float = 0.0,
) -> List[Dict[str, Any]]:
    """在 12 个月度贡献度上寻找所有候选峰值窗口。"""
    if window_sizes is None:
        window_sizes = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    candidates: List[Dict[str, Any]] = []

    for w in window_sizes:
        for start in range(1, 13):
            window_months = [(start + i - 1) % 12 + 1 for i in range(w)]
            values = monthly_ratio.loc[window_months]

            # 硬约束：连续 + 正贡献
            if (values <= min_ratio).any():
                continue

            score = values.sum()
            if score >= min_score:
                candidates.append(
                    {"months": window_months, "score": float(score), "length": w}
                )

    return candidates


def _deduplicate_windows(windows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """去掉被更大窗口完全包含的子窗口。"""
    windows = sorted(windows, key=lambda x: (-x["score"], x["length"]))
    final: List[Dict[str, Any]] = []

    for w in windows:
        w_set = set(w["months"])
        if any(w_set.issubset(set(f["months"])) for f in final):
            continue
        final.append(w)

    return final


def _window_stability(series: pd.Series, window_months: Sequence[int]) -> float:
    """计算某一窗口在不同年份之间的稳定性（窗口均值 / 全年均值 的最小值）。"""
    df = series.to_frame("v")
    df["year"] = df.index.year
    df["month"] = df.index.month

    ratios: List[float] = []
    for _, g in df.groupby("year"):
        window_mean = g[g["month"].isin(window_months)]["v"].mean()
        year_mean = g["v"].mean()
        if year_mean == 0:
            ratios.append(0)
            continue
        ratios.append(float(window_mean / year_mean))

    return min(ratios) if ratios else 1.0


def _detect_product_flow_with_peaks(series: pd.Series) -> Dict[str, Any]:
    """复制自 `分析流量周期算法2.py` 的核心判断逻辑（简化为内部使用）。"""
    monthly_ratio = _monthly_effective_contribution(series)

    # 找所有峰
    raw_peaks = _find_peak_windows(monthly_ratio)
    peaks = _deduplicate_windows(raw_peaks)

    if not peaks:
        return {
            "flow_type": "未知",
            "main_peak": None,
            "secondary_peaks": [],
            "seasonality_strength": 0.0,
            "stability": 1.0,
        }

    # 主峰 = score 最大
    main_peak = max(peaks, key=lambda x: x["score"])
    # 次峰
    secondary_peaks = [p for p in peaks if p is not main_peak]

    stability = _window_stability(series, main_peak["months"])
    ss = float(main_peak["score"])

    # 主分类判断（仍然只看主峰）
    if stability == 0:
        flow_type = '未知'
        main_peak = {
            'length': 0,
            'months': [],
            'scores': 0,
        }
    elif 0< stability < 1.15:
        flow_type = "全年流量型"
    elif ss >= 0.65 and stability >= 1.3:
        flow_type = "强周期型"
    else:
        flow_type = "混合季节型"

    return {
        "flow_type": flow_type,
        "main_peak": main_peak["months"],
        "secondary_peaks": [p["months"] for p in secondary_peaks],
        "seasonality_strength": round(ss, 3),
        "stability": round(stability, 2),
    }


def _normalize_cycle_months(months: Optional[Sequence[int]]) -> Optional[tuple]:
    """将月份窗口标准化为可比较的 key（排序后的元组）。"""
    if not months:
        return None
    return tuple(sorted(int(m) for m in months))


def determine_traffic_cycle(traffic_values: List[Sequence[float]], start_time: str, end_time: str) -> Union[
    List[Any], Tuple[List[List[Any]], Any]]:
    """
    根据多条流量序列，计算每条的主周期窗口，并返回“出现次数最多”的周期作为最终结果。

    参数
    ------
    traffic_values : List[Sequence[float]]
        若干条流量数据，每一条为一个时间序列（长度建议为 24 的倍数，按月度顺序排列）。

    返回
    ------
    List[int]
        最终判定的周期对应的月份列表（按月份从小到大排序）。
        如果所有序列都无法识别周期，则返回空列表。
    """
    
    # 检查 traffic_values 里面的内容是否全是0
    all_zero = True
    for values in traffic_values:
        if values:
            # 检查序列中是否有非零值
            if any(v != 0 for v in values):
                all_zero = False
                break
    
    if all_zero:
        return [],''
    
    cycle_counter: Counter = Counter()
    flow_type_counter: Counter = Counter()

    for values in traffic_values:
        if not values:
            continue

        # 构造时间序列（按月度均匀间隔）
        months = pd.date_range(start_time, periods=len(values), freq="MS")
        series = pd.Series(list(values), index=months, name="product_search_volume")

        result = _detect_product_flow_with_peaks(series)
        main_peak_months = result.get("main_peak")
        secondary_peak_months = result.get("secondary_peaks")
        flow_type = result.get("flow_type")

        cycle_key = _normalize_cycle_months(main_peak_months)

        if cycle_key is not None:
            cycle_counter[cycle_key] += 1
        if len(secondary_peak_months) != 0:
            for secondary_month in secondary_peak_months:
                cycle_counter[_normalize_cycle_months(secondary_month)] += 1
        if flow_type:
            flow_type_counter[flow_type] += 1

    if not cycle_counter and flow_type_counter:
        return [],'近几年上新'


    # 选择出现次数最多的周期（如有并列，取其中一个即可）
    if flow_type_counter:
        final_flow_type, _ = flow_type_counter.most_common(1)[0]
    else:
        final_flow_type = '未知'

    max_count = max(cycle_counter.values())
    
    # 如果所有周期的出现次数都为1，则统计每个月份的出现次数，找最长的连续月份周期
    all_counts = set(cycle_counter.values())
    if len(all_counts) == 1 and max_count == 1:
        # 所有周期都只出现一次，统计每个月份的出现次数
        all_cycles = list(cycle_counter.keys())
        if len(all_cycles) > 0:
            # 统计每个月份在所有周期中出现的次数
            month_count = {}
            for cycle in all_cycles:
                for month in cycle:
                    month_count[month] = month_count.get(month, 0) + 1
            
            # 找出出现次数>=2的月份
            frequent_months = sorted([month for month, count in month_count.items() if count >= 2])
            
            if frequent_months:
                # 找出最长的连续月份周期（包括跨年）
                def is_consecutive(month1, month2):
                    """判断两个月份是否连续（包括跨年：12和1是连续的）"""
                    if month1 == 12 and month2 == 1:
                        return True
                    if month1 == 1 and month2 == 12:
                        return True
                    return month2 == month1 + 1
                
                # 找出所有连续的子序列（考虑跨年）
                if len(frequent_months) == 1:
                    final_cycles = [frequent_months]
                else:
                    # 构建连续序列
                    sequences = []
                    current_seq = [frequent_months[0]]
                    
                    for i in range(1, len(frequent_months)):
                        if is_consecutive(frequent_months[i-1], frequent_months[i]):
                            current_seq.append(frequent_months[i])
                        else:
                            sequences.append(current_seq)
                            current_seq = [frequent_months[i]]
                    sequences.append(current_seq)
                    
                    # 检查跨年情况：如果序列以12结尾且另一个序列以1开头，可以合并
                    # 或者如果序列以1开头且另一个序列以12结尾，可以合并
                    merged_sequences = []
                    for seq in sequences:
                        if len(merged_sequences) > 0:
                            last_seq = merged_sequences[-1]
                            # 如果上一个序列以12结尾，当前序列以1开头，可以合并
                            if last_seq[-1] == 12 and seq[0] == 1:
                                merged_sequences[-1] = last_seq + seq
                            # 如果上一个序列以1开头，当前序列以12结尾，可以合并（但需要重新排序）
                            elif last_seq[0] == 1 and seq[-1] == 12:
                                merged_sequences[-1] = seq + last_seq
                            else:
                                merged_sequences.append(seq)
                        else:
                            merged_sequences.append(seq)
                    
                    # 再次检查：如果第一个序列以12结尾，最后一个序列以1开头，也可以合并
                    if len(merged_sequences) > 1:
                        first_seq = merged_sequences[0]
                        last_seq = merged_sequences[-1]
                        if first_seq[-1] == 12 and last_seq[0] == 1:
                            merged_sequences[0] = first_seq + last_seq
                            merged_sequences.pop()
                    
                    # 选择最长的序列
                    if merged_sequences:
                        max_length = max(len(seq) for seq in merged_sequences)
                        final_cycles = [sorted(seq) for seq in merged_sequences if len(seq) == max_length]
                    else:
                        final_cycles = []
            else:
                # 没有出现次数>=2的月份，返回空列表
                final_cycles = []
        else:
            final_cycles = []
    else:
        # 原有逻辑：选择出现次数最多的周期
        final_cycles = [
            list(cycle)
            for cycle, count in cycle_counter.items()
            if count == max_count
        ]
    
    # 检查：如果最终周期是空列表，则尝试取下一个最多的周期
    # 判断 final_cycles 是否为空或只包含空列表
    is_empty_cycles = (not final_cycles or 
                      all(len(cycle) == 0 for cycle in final_cycles))
    
    if is_empty_cycles:
        # 尝试找下一个最多的周期（排除空列表）
        non_empty_cycles = [(cycle, count) for cycle, count in cycle_counter.items() 
                           if cycle and len(cycle) > 0]
        if non_empty_cycles:
            # 按出现次数排序，取最多的
            non_empty_cycles.sort(key=lambda x: x[1], reverse=True)
            max_non_empty_count = non_empty_cycles[0][1]
            # 获取所有出现次数最多的非空周期
            final_cycles = [list(cycle) for cycle, count in non_empty_cycles 
                          if count == max_non_empty_count]
    
    # 检查：如果流量类型是"未知"，则尝试取下一个最多的流量类型
    if final_flow_type == '未知':
        # 尝试找下一个最多的流量类型（排除"未知"）
        non_unknown_types = [(ftype, count) for ftype, count in flow_type_counter.items() 
                           if ftype != '未知']
        if non_unknown_types:
            # 按出现次数排序，取最多的
            non_unknown_types.sort(key=lambda x: x[1], reverse=True)
            final_flow_type = non_unknown_types[0][0]
    
    # 如果还是没有找到有效的周期，确保返回空列表
    is_still_empty = (not final_cycles or 
                     all(len(cycle) == 0 for cycle in final_cycles))
    if is_still_empty:
        final_cycles = []
        # 如果流量类型还是"未知"，保持"未知"
        if not flow_type_counter or final_flow_type == '未知':
            final_flow_type = '未知'
    
    # 过滤：如果final_cycles的长度>=2，处理两两相交的情况
    if len(final_cycles) >= 2:
        # 转换为集合以便计算交集
        cycle_sets = [set(cycle) for cycle in final_cycles]
        to_remove = set()  # 需要移除的索引
        intersections = []  # 需要添加的交集
        
        # 检查所有两两组合
        for i in range(len(cycle_sets)):
            if i in to_remove:
                continue
            for j in range(i + 1, len(cycle_sets)):
                if j in to_remove:
                    continue
                
                # 计算交集
                intersection = cycle_sets[i] & cycle_sets[j]
                
                # 如果交集不为空
                if intersection:
                    # 标记需要移除
                    to_remove.add(i)
                    to_remove.add(j)
                    # 添加交集（转换为排序后的列表）
                    intersections.append(sorted(list(intersection)))
        
        # 移除相交的集合，保留不相交的集合
        filtered_cycles = [final_cycles[i] for i in range(len(final_cycles)) 
                          if i not in to_remove]
        
        # 添加交集结果
        filtered_cycles.extend(intersections)
        
        # 去重（保持顺序）
        seen = set()
        unique_cycles = []
        for cycle in filtered_cycles:
            cycle_tuple = tuple(cycle)
            if cycle_tuple not in seen:
                seen.add(cycle_tuple)
                unique_cycles.append(cycle)
        
        final_cycles = unique_cycles
    
    return final_cycles, final_flow_type


if __name__ == "__main__":
    # 构造几组模拟流量数据（2 年 * 12 个月），大部分样本在 4-7 月有明显旺季
    # def build_series(peak_months: Sequence[int], base: float = 100.0, peak: float = 200.0):
    #     values: List[float] = []
    #     for _ in range(2):  # 两年
    #         for m in range(1, 13):
    #             values.append(peak if m in peak_months else base)
    #     return values


    # 三条样本的主周期都是 4-7 月，一条样本的主周期偏向 1-4 月
    traffic_samples: List[Sequence[float]] = [
        [3208, 1379, 0, 0, 0, 369, 714, 2309, 4120, 14810, 61220, 64123, 2932, 1337, 637,
         616, 754, 722, 1556, 2522, 4809, 16264, 54534, 67706, 2151, 700, 621, 482, 0, 140,
         1570, 2280, 4182, 11829, 51028],
        [8221, 1675, 1342, 917, 1963, 2614, 5220, 16444, 25416, 49888, 160115, 80169, 3785, 1243,
         935, 1362, 1351, 1901, 3477, 6904, 13913, 38366, 121840, 69718, 3105, 641, 140, 762, 698,
         1401, 3164, 5430, 20078, 50232, 158884],
        [37909, 7997, 4778, 5482, 5378, 12439, 24655, 86859, 177866, 370334, 1332640, 417609, 43744, 9261, 9295, 8655,
         9980, 23188, 50701, 94861, 171563, 351848, 920260, 371111, 26902, 5090, 3680, 4475, 7596, 14852, 34076, 58731,
         112284, 239809, 1059041],
        # [1907, 640, 0, 0, 0, 0, 620, 1169, 2461, 4171, 15988, 10055, 0, 0, 0, 0, 0, 0, 0, 421, 3152, 12976, 52063,
        #  47172, 1644, 0, 0, 0, 0, 0, 140, 947, 2765, 9094, 52785],
        # [2538, 0, 0, 0, 0, 0, 246, 1231, 2958, 7492, 30545, 38959, 2103, 0, 0, 0, 545, 0, 438, 656, 2293, 7785, 29335,
        #  40743, 1251, 0, 0, 0, 0, 0, 140, 518, 1744, 4184, 24393]
        # [222,222,90,95,220,240,90,90,100,95,90,85,
        #  222,222,88,92,210,235,90,90,98,93,88,83]
    ]

    print("=== 单条样本的周期判定 ===")
    for idx, vals in enumerate(traffic_samples, start=1):
        months = pd.date_range(start="2023-01", end='2025-11', freq="MS")
        series = pd.Series(vals, index=months, name=f"sample_{idx}")
        detail = _detect_product_flow_with_peaks(series)
        print(
            f"样本 {idx}: flow_type={detail['flow_type']}, "
            f"main_peak={detail['main_peak']}, "
            f"secondary_peaks={detail['secondary_peaks']}, "
            f"seasonality_strength={detail['seasonality_strength']}, "
            f"stability={detail['stability']}"
        )

    final_cycle = determine_traffic_cycle(traffic_samples, '2017-01', '2025-11')
    print("\n=== 最终多数票周期 ===")
    print(f"最终判定周期月份: {final_cycle}")
