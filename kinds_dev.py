from typing import List, Dict, Any, Set, Union, Tuple, Optional

MONTH_TO_SEASON = {
    1: "冬", 2: "冬",
    3: "春", 4: "春", 5: "春",
    6: "夏", 7: "夏", 8: "夏",
    9: "秋", 10: "秋", 11: "秋",
    12: "冬"
}


def ym_to_int(dk: str) -> int:
    """'YYYYMM' -> 202512"""
    return int(dk)


def int_to_ym(ym: int) -> Tuple[int, int]:
    """202512 -> (2025, 12)"""
    y = ym // 100
    m = ym % 100
    return y, m


def ym_add_months(ym: int, delta: int) -> int:
    """对 YYYYMM 做月份加减，delta 可为负"""
    y, m = int_to_ym(ym)
    total = y * 12 + (m - 1) + delta
    ny = total // 12
    nm = total % 12 + 1
    return ny * 100 + nm


def parse_seasons(seasons: Union[str, List[str], Set[str], None]) -> Set[str]:
    """
    seasons 可传：
    - "春、秋"
    - ["春","秋"]
    - {"春","秋"}
    - None
    """
    if seasons is None:
        return set()
    if isinstance(seasons, str):
        s = seasons.replace(",", "、").replace(" ", "")
        parts = [p for p in s.split("、") if p]
        return set(parts)
    return set(seasons)


def sum_sales_by_season_last_year(
        sales_hist: List[Dict[str, Any]],
        seasons: Union[str, List[str], Set[str], None],
        traffic_months: List[List[int]],  # ✅ 必选 + 二维
) -> Dict[str, int]:
    """
    sales_hist: [{'dk':'202410','sales':50}, ...]  dk=YYYYMM
    seasons:
      - "全年季" 或 "春、秋" 等（用于过滤季节：非全年季时只保留指定季节）
    traffic_months:
      - 二维列表，每个子列表是一个“流量周期月份”，例如：
        [[3,4,5,6,7,8,9], [11,12]]

    返回：
      仅返回 season_sums 中不为 0 的项，例如：
      {'秋': 50, '冬': 50}
    """
    if not sales_hist:
        return {'春': 0, '夏': 0, '秋': 0, '冬': 0}

    # ✅ 1) 扁平化 traffic_months（二维 -> 去重月份集合）
    allowed_months = set()
    for group in traffic_months:
        if not group:
            continue
        for m in group:
            try:
                m = int(m)
            except Exception:
                continue
            if 1 <= m <= 12:
                allowed_months.add(m)

    # 如果没有任何有效月份，直接返回空（避免误算）
    if not allowed_months:
        return {'春': 0, '夏': 0, '秋': 0, '冬': 0}

    # ✅ 2) 近一年窗口（含最新月共12个月）
    latest_ym = max(ym_to_int(x["dk"]) for x in sales_hist if x.get("dk"))
    start_ym = ym_add_months(latest_ym, -11)

    # ✅ 3) 解析 seasons（用于非全年季时过滤）
    season_set = parse_seasons(seasons)
    is_all_year = ("全年季" in season_set) or (seasons == "全年季")

    # ✅ 4) 汇总近一年每个月销量（月 -> sales）
    month_sales: Dict[int, int] = {}
    for x in sales_hist:
        dk = x.get("dk")
        if not dk:
            continue
        ym = ym_to_int(dk)
        if ym < start_ym or ym > latest_ym:
            continue

        sales = x.get("sales", 0) or 0
        _, m = int_to_ym(ym)
        month_sales[m] = month_sales.get(m, 0) + int(sales)

    # ✅ 5) 只统计 traffic_months 覆盖到的月份
    season_sums = {"春": 0, "夏": 0, "秋": 0, "冬": 0}
    used_months = sorted(m for m in month_sales.keys() if m in allowed_months)

    for m in used_months:
        season = MONTH_TO_SEASON[m]
        season_sums[season] += month_sales[m]

    # ✅ 6) 非全年季：只保留你传入的季节（如 春、秋）
    if not is_all_year and season_set:
        for s in list(season_sums.keys()):
            if s not in season_set:
                season_sums[s] = 0

    # ✅ 7) 只返回不为 0 的季节
    if '全年季' in season_set:
        return {season: sales for season, sales in season_sums.items()}

    return {season: sales for season, sales in season_sums.items() if season in season_set}
    # return {season: sales for season, sales in season_sums.items() if sales != 0}


def classify_season_from_traffic_cycle(sales_hist: List[Dict[str, Any]], traffic_cycle: List[List[int]]
                                       ) -> Union[Dict[str, Union[str, Dict[str, int]]], str]:
    """
    traffic_cycle: 二维列表，例如：
      - [[3,4,5,6,7,8,9], [11,12]]
      - [[1,2,3,4,5,6,7,8,9]]
      - [[10,11,12]]
    规则：
      - 涉及月份去重后数量 > 8 => 全年季
      - 否则 => 输出涉及季节 + 每季对应月份
    """
    # 1) 扁平化 + 去重月份
    months: Set[int] = set()
    for group in traffic_cycle or []:
        if not group:
            continue
        for m in group:
            if isinstance(m, int) and 1 <= m <= 12:
                months.add(m)

    sorted_months = sorted(months)
    if len(sorted_months) == 0:
        return f"流量数据不足|春:0，夏:0，秋:0，冬:0"
    # 2) 全年季判断
    if len(months) > 8:
        # 返回的数据是{'春': xx, '夏': xx...}
        season_data = sum_sales_by_season_last_year(sales_hist=sales_hist, seasons="全年季",
                                                    traffic_months=traffic_cycle)
        data_str = "，".join(
            f"{season}:{sales}"
            for season, sales in season_data.items()
        )
        if data_str == '':
            data_str = '对应月份没有销量数据'
        return f"全年季|{data_str}"

    # 3) 非全年季：统计涉及哪些季节，并记录每季月份
    season_months: Dict[str, List[int]] = {"春": [], "夏": [], "秋": [], "冬": []}
    for m in sorted_months:
        season_months[MONTH_TO_SEASON[m]].append(m)

    seasons_involved = "、".join([s for s, ms in season_months.items() if ms])
    season_data = sum_sales_by_season_last_year(sales_hist=sales_hist, seasons=seasons_involved,
                                                traffic_months=traffic_cycle)
    data_str = "，".join(
        f"{season}:{sales}"
        for season, sales in season_data.items()
    )
    if data_str == '':
        data_str = '对应月份没有销量数据'
    return f"{seasons_involved}|{data_str}"
    # return {
    #     '所属季度': seasons_involved,
    #     '季度数据': season_data
    # }


if __name__ == '__main__':
    # print(classify_season_from_traffic_cycle(
    #     traffic_cycle=[[1, 2, 3, 11, 12], [5, 6]]))
    sales_hist = [
        {'dk': '202410', 'sales': 50},
        {'dk': '202507', 'sales': 0},
        {'dk': '202508', 'sales': 0},
        {'dk': '202509', 'sales': 0},
        {'dk': '202510', 'sales': 0},
        {'dk': '202511', 'sales': 50},
        {'dk': '202512', 'sales': 50}
    ]

    # 例1：季节 = "春、秋"（只统计春+秋，近一年）
    print(sum_sales_by_season_last_year(sales_hist, seasons="春、秋", traffic_months=[[1, 3, 4]]))

    # 例2：全年季 + 流量月份=[3,4,5,6,7,8,9,10,11,12]（只累加这些月份）
    print(
        sum_sales_by_season_last_year(sales_hist, seasons="全年季",
                                      traffic_months=[[11, 12, 3, 4], [5, 6, 7, 8, 9, 10], ]))
