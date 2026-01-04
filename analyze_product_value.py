import pandas as pd
import os
from typing import Union, Tuple

from pandas import DataFrame


def analyze_product_value_nr(
        data: Union[str, pd.DataFrame],
        output_path: str = None,
        sales_threshold: int = 5
) -> pd.DataFrame:
    """
    分析产品潜在价值
    
    参数:
        data: Excel文件路径或DataFrame
        output_path: 输出文件路径（可选，如果提供则保存到Excel）
        sales_threshold: 销量阈值，默认5
    
    返回:
        添加了"说明"和"是否具有潜力"列的DataFrame
    """
    # 如果输入是字符串，则读取Excel文件；否则直接使用DataFrame
    if isinstance(data, str):
        df = pd.read_excel(data)
    else:
        df = data.copy()

    explanations = []
    potential_flags = []

    for _, row in df.iterrows():

        cycle = str(row.get("核心词周期", "")).strip()
        price_trend = str(row.get("价格趋势类型", "")).strip()
        last_sales = row.get("上月销量", 0)

        # 处理上月销量可能为None的情况
        if pd.isna(last_sales) or last_sales is None:
            last_sales = 0
        else:
            try:
                last_sales = int(float(last_sales))
            except (ValueError, TypeError):
                last_sales = 0

        reasons = []
        has_potential = False

        # ① 全年流量型 + 价格上升
        if "全年" in cycle and "上升" in price_trend:
            reasons.append("全年流量型需求且价格呈上升趋势，说明具备长期可持续开发价值")
            has_potential = True

        # ② 全年流量型 + 先升后降
        elif "全年" in cycle and "先" in price_trend and "降" in price_trend:
            reasons.append("全年流量型需求，在阶段性高位出现价格回落，说明存在可复制的溢价窗口")
            has_potential = True

        # ③ 周期型 + 先升后降
        elif "周期" in cycle and "先" in price_trend and "降" in price_trend:
            reasons.append("典型周期型产品，高峰期具备提价能力，适合提前卡位开发")
            has_potential = True

        # ④ 价格上升 + 有销量
        elif "上升" in price_trend and last_sales >= sales_threshold:
            reasons.append("在已有销量基础上价格仍能上涨，需求强度提升，具备潜力")
            has_potential = True

        # ⑤ 价格下降 + 有销量
        elif "下降" in price_trend and last_sales > 0:
            reasons.append("价格下降但仍有销量，说明市场进入竞争阶段，需谨慎评估利润空间")

        # ⑥ 价格下降 + 无销量
        elif "下降" in price_trend and last_sales == 0:
            reasons.append("价格下降且销量不足，需求疲软，不建议开发")

        else:
            reasons.append("目前无法判断潜在价值，建议持续观察")

        explanations.append("；".join(reasons))
        potential_flags.append("是" if has_potential else "否")

    df["商品潜力说明"] = explanations
    # df["是否具有潜力"] = potential_flags

    # 如果提供了输出路径，则保存到Excel
    if output_path:
        # 确保输出目录存在
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df.to_excel(output_path, index=False)
        return df, output_path

    return df


def analyze_product_value_bs(
        data: Union[str, pd.DataFrame],
        output_path: str = None,
) -> Union[Tuple[DataFrame, str], DataFrame]:
    """
    分析产品潜在价值

    参数:
        data: Excel文件路径或DataFrame
        output_path: 输出文件路径（可选，如果提供则保存到Excel）
        sales_threshold: 销量阈值，默认5

    返回:
        添加了"说明"和"是否具有潜力"列的DataFrame
    """
    # 如果输入是字符串，则读取Excel文件；否则直接使用DataFrame
    if isinstance(data, str):
        df = pd.read_excel(data)
    else:
        df = data.copy()

    explanations = []
    isDevelop = []
    i = 0
    for _, row in df.iterrows():

        if i == 15:
            print(i)
        i+=1
        # 检查"是否开发"列的值
        should_develop = str(row.get("经验判断是否开发", "")).strip()
        cycle = str(row.get("核心词周期", "")).strip()
        price_trend = str(row.get("价格趋势类型", "")).strip()
        reason_develop = str(row.get('原因', '')).strip()
        title = str(row.get('标题', '')).strip()

        # 只有在"是否开发"列为"是"时才进行判断，因为这时当前商品已经通过价格规则判断了
        # 前提：已是 BS 榜商品 → 默认销量合格
        if should_develop == "是":
            # 按照新的逻辑判断
            if "全年流量型" in cycle and price_trend == "上升":
                reason = "全年具备流量且价格上升，可以优先开发"
                is_develop = "开发"
            elif "全年流量型" in cycle and price_trend == "下降":
                reason = "全年具备流量但是价格下降，需要持续观察"
                is_develop = '追踪'
            elif price_trend == "上升":
                reason = "价格呈上升趋势，可以开发"
                is_develop = '开发'
            elif price_trend == "下降" or price_trend == '波动':
                reason = "价格属于非上升趋势但有微博利润，需要继续观察"
                is_develop = '追踪'
            else:
                reason = "当前信息不足"
                is_develop = '待定'
        elif should_develop == '否':
            if '无法赶上' in reason_develop and price_trend == '上升' :
                reason = '虽然价格上升但是不处于流量周期中，需要持续观察'
                is_develop = '追踪'
            elif '无法赶上' in reason_develop and price_trend == '下降':
                reason = '价格下降只有超薄利润但是无法赶上流量周期，不进行开发'
                is_develop = '不开发'
            elif '无法赶上' in reason_develop:
                reason = '价格处于波动中可能低于利润阈值，不进行开发'
                is_develop = '不开发'
            elif '价格过低' in reason_develop:
                reason = '价格过低，不进行开发'
                is_develop = '不开发'
            elif '未识别到流量周期' in reason_develop and price_trend == '上升':
                reason = '没有识别到流量周期，无法判断近期是否可以开发，需要持续观察'
                is_develop = '追踪'
            elif '未识别到流量周期' in reason_develop and price_trend == '下降':
                reason = '价格下降只有超薄利润且无法判断近期是否可以开发，不进行开发'
                is_develop = '不开发'
            elif "没有" in reason_develop and '规则' in reason_develop:
                if "全年流量型" in cycle and price_trend == "上升":
                    reason = "没有固定规则，全年具备流量且价格上升，需要持续观察"
                    is_develop = "追踪"
                elif "全年流量型" in cycle and price_trend == "下降":
                    reason = "没有固定规则，全年具备流量但是价格下降，不进行开发"
                    is_develop = '不开发'
                elif price_trend == "上升":
                    reason = "没有固定规则，价格呈上升趋势，需要持续观察"
                    is_develop = '追踪'
                elif price_trend == "下降" or price_trend == '波动':
                    reason = "没有固定规则，价格属于非上升趋势，需要继续观察"
                    is_develop = '不开发'
                else:
                    reason = "当前信息不足"
                    is_develop = '待定'
            else:
                reason = "当前信息不足"
                is_develop = '待定'
        elif should_develop == '待定' and 'pcs解析失败' in reason_develop:
            # 按照新的逻辑判断
            if "全年流量型" in cycle and price_trend == "上升":
                reason = "没有固定规则，全年具备流量且价格上升，需要持续观察"
                is_develop = "追踪"
            elif "全年流量型" in cycle and price_trend == "下降":
                reason = "没有固定规则，全年具备流量但是价格下降，不进行开发"
                is_develop = '不开发'
            elif price_trend == "上升":
                reason = "没有固定规则，价格呈上升趋势，需要持续观察"
                is_develop = '追踪'
            elif price_trend == "下降" or price_trend == '波动':
                reason = "没有固定规则，价格属于非上升趋势，不进行开发"
                is_develop = '不开发'
            else:
                reason = "当前信息不足"
                is_develop = '待定'
        else:
            reason = ''
            is_develop = ''

        explanations.append(reason)
        isDevelop.append(is_develop)
    df["商品潜力说明"] = explanations
    df["是否开发"] = isDevelop

    # 如果提供了输出路径，则保存到Excel
    if output_path:
        # 确保输出目录存在
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df.to_excel(output_path, index=False)
        return df, output_path

    return df


if __name__ == '__main__':
    # analyze_product_value_nr(data='./result/流量周期分析结果_20251230.xlsx', output_path='result/nr/潜在价值结果/分析后_潜在价值_20251230.xlsx')
    analyze_product_value_bs(data='./result/bs/流量周期分析结果_20251231.xlsx',
                             output_path='result/bs/潜在价值结果/分析后_潜在价值_20251231-2.xlsx')
