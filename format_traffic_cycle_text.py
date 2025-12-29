from typing import List


def format_traffic_cycle_text(
    flow_type: str,
    traffic_cycle: List[List[int]],
    low_months: List[int]
) -> str:
    """
    将流量周期结果格式化为用户可读文本
    """

    lines = []
    if flow_type == '近几年上新':
        lines.append(f'流量类型：无')
        lines.append(f'说明：近几年核心词才有搜索量，无法判断流量周期')
        return "\n".join(lines)

    # ---------- 1️⃣ 流量类型 ----------
    lines.append(f"流量类型：{flow_type}")

    # ---------- 2️⃣ 流量高峰期 ----------
    if traffic_cycle:
        lines.append("流量周期：")
        for idx, cycle in enumerate(traffic_cycle, start=1):
            if not cycle:
                continue

            if len(cycle) == 1:
                cycle_text = f"{cycle[0]} 月"
            else:
                cycle_text = f"{cycle}"

            lines.append(f"• 第 {idx} 个周期：{cycle_text}")
    else:
        lines.append("流量周期：未识别到明显周期")

    # ---------- 3️⃣ 流量低谷期 ----------
    if low_months:
        low_months_text = "、".join(str(m) for m in sorted(low_months))
        lines.append(f"低流量月份：{low_months_text} 月")
    else:
        lines.append("流量低谷期：未识别到明显低谷")

    return "\n".join(lines)

if __name__ == '__main__':
    flow_type = '季节型'
    traffic_cycle = [[1,2],[5,6]]
    low_months = [3,11,12]
    core_word_cell_text = format_traffic_cycle_text(
        flow_type=flow_type,
        traffic_cycle=traffic_cycle,
        low_months=low_months
    )
    print(core_word_cell_text)