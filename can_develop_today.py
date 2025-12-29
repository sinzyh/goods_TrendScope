from __future__ import annotations
from datetime import datetime
from typing import List, Tuple


def can_develop(
    traffic_cycles: List[List[int]],
    prepare_months: int = 3,
    now: datetime | None = None
) -> Tuple[bool, str]:
    """
    综合判断是否值得开发（支持多峰周期）

    返回:
        (overall_can_develop, reason)
    """

    if not traffic_cycles:
        return False, "未识别到流量周期"

    if now is None:
        now = datetime.now()

    current_month = now.month
    T_ready = current_month + prepare_months

    can_hit = []     # 能赶上的周期说明
    cannot_hit = []  # 赶不上的周期说明

    for cycle in traffic_cycles:
        cycle = sorted(cycle)
        start, end = cycle[0], cycle[-1]

        # 上一年 & 下一年周期开始
        prev_start = start
        next_start = start + 12

        # 计算距离
        dist_prev = abs(T_ready - prev_start)
        dist_next = abs(next_start - T_ready)

        # 判断倾向
        if dist_prev <= dist_next:
            # 倾向上一年
            if T_ready <= prev_start:
                gap = prev_start - T_ready
                can_hit.append(
                    f"可赶上今年 {start}-{end} 月流量周期（提前 {gap} 个月完成开发）"
                )
            else:
                cannot_hit.append(
                    f"无法赶上今年 {start}-{end} 月流量周期（开发完成时间已晚于周期开始）"
                )
        else:
            # 倾向下一年
            if T_ready <= next_start:
                gap = next_start - T_ready
                can_hit.append(
                    f"可赶上明年 {start}-{end} 月流量周期（提前 {gap} 个月完成开发）"
                )
            else:
                cannot_hit.append(
                    f"无法赶上明年 {start}-{end} 月流量周期（开发完成时间过晚）"
                )

    # ---------- 综合结论 ----------
    if can_hit:
        reason = (
            "可以开发。\n"
            + "；".join(can_hit)
        )
        if cannot_hit:
            reason += "\n同时注意：\n" + "；".join(cannot_hit)

        return True, reason

    return False, "不建议开发。\n" + "；".join(cannot_hit)




if __name__ == '__main__':
    print(can_develop([[5,6],[10,11],],))