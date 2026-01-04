
import pandas as pd
from collections import Counter
from typing import List, Tuple, Sequence, Union, Any


def detect_low_flow_months(
    traffic_values: List[Sequence[float]],
    start_time: str,
    end_time: str,
    traffic_cycle: List[List[int]],   # 二维旺季周期
    max_ratio: float = 0.2
) -> Union[Tuple[List[Any], str], List[int]]:
    """
    方案一（支持多个旺季周期）：
    - 贡献比例基于【全年】
    - 低谷月份只从【非所有旺季月份】中选择
    - 使用关键词投票机制决策最终低谷月份
    """

    if not traffic_values:
        return [], "无流量数据"

    # ✅ 将二维旺季周期拍平成一维月份集合
    traffic_cycle_months = {
        m for cycle in traffic_cycle for m in cycle
    }

    month_vote_counter = Counter()
    all_month_avg_list = []

    # ---------- 1️⃣ 单关键词：全年比例 + 非旺季筛选 ----------
    for values in traffic_values:
        if not values:
            continue

        months = pd.date_range(start=start_time, periods=len(values), freq="MS")
        series = pd.Series(values, index=months)

        df = series.to_frame("value")
        df["month"] = df.index.month

        # 全年：按月份多年均值
        month_avg_all = df.groupby("month")["value"].mean()
        all_month_avg_list.append(month_avg_all)

        total_all = month_avg_all.sum()
        if total_all == 0:
            continue

        # 全年贡献比例（不删除旺季）
        month_ratio_all = (month_avg_all / total_all).sort_values()

        cumulative = 0.0
        low_months_single = []

        for m, ratio in month_ratio_all.items():
            # ⚠ 排除所有旺季月份
            if m in traffic_cycle_months:
                continue

            if cumulative + ratio <= max_ratio:
                low_months_single.append(int(m))
                cumulative += ratio
            else:
                break

        # 投票
        for m in low_months_single:
            month_vote_counter[m] += 1

    if not month_vote_counter:
        return []

    # ---------- 2️⃣ 全局：全年比例 + 非旺季筛选 ----------
    all_month_avg = pd.concat(all_month_avg_list, axis=1).mean(axis=1)

    total_all = all_month_avg.sum()
    if total_all == 0:
        return [], "全年流量为 0"

    month_ratio_all = (all_month_avg / total_all).sort_values()

    global_low_candidates = []
    cumulative = 0.0

    for m, ratio in month_ratio_all.items():
        if m in traffic_cycle_months:
            continue

        if cumulative + ratio <= max_ratio:
            global_low_candidates.append(int(m))
            cumulative += ratio
        else:
            break

    if not global_low_candidates:
        return [], "非旺季月份中未识别到全局低谷候选"

    # ---------- 3️⃣ 投票 + 全局候选双重约束 ----------
    filtered_votes = {
        m: cnt for m, cnt in month_vote_counter.items()
        if m in global_low_candidates
    }

    if not filtered_votes:
        return [], "低谷候选月份中无关键词共识"

    max_vote = max(filtered_votes.values())

    final_low_months = sorted(
        [m for m, cnt in filtered_votes.items() if cnt == max_vote]
    )

    # detail = (
    #     f"低谷月份基于【全年贡献比例】判断，"
    #     f"排除旺季周期 {traffic_cycle}（展开为 {sorted(traffic_cycle_months)}），"
    #     f"由 {len(traffic_values)} 个核心词投票决定，"
    #     f"最终低谷月份 {final_low_months}，"
    #     f"最高票数 {max_vote}"
    # )

    return final_low_months



if __name__ == '__main__':
    traffic_cycle = [[1,2],[5,6]]

    traffic_samples: List[List[float]] = [
        # [3208, 1379, 0, 0, 0, 369, 714, 2309, 4120, 14810, 61220, 64123, 2932, 1337, 637,
        #  616, 754, 722, 1556, 2522, 4809, 16264, 54534, 67706, 2151, 700, 621, 482, 0, 140,
        #  1570, 2280, 4182, 11829, 51028],
        # [8221, 1675, 1342, 917, 1963, 2614, 5220, 16444, 25416, 49888, 160115, 80169, 3785, 1243,
        #  935, 1362, 1351, 1901, 3477, 6904, 13913, 38366, 121840, 69718, 3105, 641, 140, 762, 698,
        #  1401, 3164, 5430, 20078, 50232, 158884],
        # [37909, 7997, 4778, 5482, 5378, 12439, 24655, 86859, 177866, 370334, 1332640, 417609, 43744, 9261, 9295, 8655,
        #  9980, 23188, 50701, 94861, 171563, 351848, 920260, 371111, 26902, 5090, 3680, 4475, 7596, 14852, 34076, 58731,
        #  112284, 239809, 1059041],
        # [1907, 640, 0, 0, 0, 0, 620, 1169, 2461, 4171, 15988, 10055, 0, 0, 0, 0, 0, 0, 0, 421, 3152, 12976, 52063,
        #  47172, 1644, 0, 0, 0, 0, 0, 140, 947, 2765, 9094, 52785],
        # [2538, 0, 0, 0, 0, 0, 246, 1231, 2958, 7492, 30545, 38959, 2103, 0, 0, 0, 545, 0, 438, 656, 2293, 7785, 29335,
        #  40743, 1251, 0, 0, 0, 0, 0, 140, 518, 1744, 4184, 24393]
        # [222,222,90,95,220,240,90,90,100,95,90,85,
        #  222,222,88,92,210,235,90,90,98,93,88,83]
        # [
        #     0, 130, 125, 128, 135, 140,
        #     150, 155, 160, 130, 140, 150,
        #     0, 135, 130, 132, 138, 142,
        #     148, 152, 158, 130, 140, 150
        # ]
    ]
    low_months, low_reason = detect_low_flow_months(
        traffic_values=traffic_samples,
        start_time="2023-01",
        end_time="2024-12",
        traffic_cycle=traffic_cycle,
        max_ratio=0.2
    )

    print(low_months)
    print(low_reason)
