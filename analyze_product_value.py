import pandas as pd
import os
from typing import Union, Tuple, Optional

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
        masterKind: str = None,
        slaverKind: str = None,
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

        if i == 27:
            print(i)
        i+=1
        # 检查"是否开发"列的值
        should_develop = str(row.get("经验判断是否开发", "")).strip()
        cycle = str(row.get("核心词周期", "")).strip()
        price_trend = str(row.get("价格趋势类型", "")).strip()
        price = str(row.get('价格', '')).strip()
        reason_develop = str(row.get('规则层建议', '')).strip()
        sales = str(row.get('上月销量','')).strip()
        title = str(row.get('标题', '')).strip()

        # 只有在"是否开发"列为"是"时才进行判断，因为这时当前商品已经通过价格规则判断了
        # 判断是否开发的时候有四个步骤：数据完整性、人工规则、流量周期、价格
        if masterKind == 'toys&games' and slaverKind == 'plates':
            if judgment_data_complete(masterKind=masterKind,slaverKind=slaverKind,price=price, has_traffic_reason=cycle, pcs_reason=reason_develop):
                # 数据完整
                if judgment_person_rule(reason=reason_develop):
                    # 存在对应人工规则
                    if judgement_pass_person_rule(reason=reason_develop):
                        # 通过人工规则
                        if judgement_identify_traffic_cycle(reason=reason_develop):
                            # 可以识别到流量周期
                            if judgement_catch_up_traffic_cycle(reason=reason_develop):
                                # 可以赶上流量周期
                                if price_trend == '上升':
                                    reason = '数据完整，通过人工规则，能赶上流量周期，价格趋势上升'
                                    is_develop = '开发'
                                elif price_trend == '波动' or price_trend == '下降':
                                    reason = '数据完整，通过人工规则，能赶上流量周期，价格趋势波动/下降'
                                    is_develop = '追踪'
                                elif price_trend == '平稳':
                                    reason = '数据完整，通过人工规则，能赶上流量周期，价格趋势平稳'
                                    is_develop = '待定'
                                else:
                                    reason = ''
                                    is_develop = ''
                            else:
                                # 不能赶上流量周期
                                if price_trend == '上升':
                                    reason = '数据完整，通过人工规则，赶不上流量周期，价格趋势上升'
                                    is_develop = '追踪'
                                elif price_trend == '波动' or price_trend == '下降':
                                    reason = '数据完整，通过人工规则，赶不上流量周期，价格趋势波动/下降'
                                    is_develop = '不开发'
                                elif price_trend == '平稳':
                                    reason = '数据完整，通过人工规则，赶不上流量周期，价格趋势平稳'
                                    is_develop = '待定'
                                else:
                                    reason = ''
                                    is_develop = ''
                        else:
                            # 未识别到流量周期
                            if price_trend == '上升':
                                reason = '数据完整，通过人工规则，没有识别到流量周期，价格趋势上升'
                                is_develop = '追踪'
                            elif price_trend == '波动' or price_trend == '下降' or price_trend == '平稳':
                                reason = '数据完整，没通过人工规则，识别不到流量周期，价格波动/下降/平稳'
                                is_develop = '不开发'
                            else:
                                reason = ''
                                is_develop = ''
                    else:
                        # 没通过规则
                        reason = '数据完整，没通过人工规则'
                        is_develop = '不开发'
                else:
                    # 不存在人工规则
                    if price_trend == '上升':
                        reason = '数据完整，没有对应人工规则，价格趋势上升'
                        is_develop = '追踪'
                    elif price_trend == '波动' or price_trend == '下降' or price_trend == '平稳':
                        reason = '数据完整，没有对应人工规则，价格趋势波动/下降/平稳'
                        is_develop = '不开发'
                    else:
                        reason = ''
                        is_develop = ''
            else:
                # 数据不完整
                if price is None:
                    # 没有价格
                    reason = '数据不完整，缺少价格'
                    is_develop = '待定'
                elif cycle is None:
                    # 没有流量周期
                    reason = '数据不完整，缺少流量周期'
                    is_develop = '待定'
                else:
                    # 没有pcs情况
                    if price_trend == '上升':
                        reason = '数据不完整，缺少pcs，价格趋势上升'
                        is_develop = '追踪'
                    elif price_trend == '波动' or price_trend == '下降':
                        reason = '数据不完整，缺少pcs，价格趋势波动/下降'
                        is_develop = '不开发'
                    elif price_trend == '平稳':
                        reason = '数据不完整，有价格，有流量周期，价格趋势平稳'
                        is_develop = '待定'
                    else:
                        reason = ''
                        is_develop = ''
        elif masterKind == 'toys&games' and slaverKind == 'banners':
            if judgment_data_complete(masterKind=masterKind, slaverKind=slaverKind,price_trend=price_trend, sales=sales):
                # 数据完整
                if float(sales) >= 50:
                    if price_trend == '上升':
                        if judgement_identify_traffic_cycle(reason=reason_develop):
                            # 可以识别到流量周期
                            if judgement_catch_up_traffic_cycle(reason=reason_develop):
                                # 可以赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势上升，能赶上流量周期'
                                is_develop = '开发'
                            else:
                                # 无法赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势上升，赶不上流量周期'
                                is_develop = '追踪'
                        else:
                            # 无法识别到流量周期
                            reason = '数据完整，销量≥50，价格趋势上升，识别不到流量周期'
                            is_develop = '追踪'
                    elif price_trend == '波动' or price_trend == '下降':
                        # 波动/下降
                        if judgement_identify_traffic_cycle(reason=reason_develop):
                            # 可以识别到流量周期
                            if judgement_catch_up_traffic_cycle(reason=reason_develop):
                                # 可以赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势波动/下降，能赶上流量周期'
                                is_develop = '追踪'
                            else:
                                # 无法赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势波动/下降，赶不上流量周期'
                                is_develop = '不开发'
                        else:
                            # 无法识别到流量周期
                            reason = '数据完整，销量≥50，价格趋势波动/下降，识别不到流量周期'
                            is_develop = '追踪'
                    else:
                        # 价格趋势平稳
                        if judgement_identify_traffic_cycle(reason=reason_develop):
                            # 可以识别到流量周期
                            if judgement_catch_up_traffic_cycle(reason=reason_develop):
                                # 可以赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势平稳，能赶上流量周期'
                                is_develop = '待定'
                            else:
                                # 无法赶上流量周期
                                reason = '数据完整，销量≥50，价格趋势平稳，赶不上流量周期'
                                is_develop = '不开发'
                        else:
                            # 无法识别到流量周期
                            reason = '数据完整，销量≥50，价格趋势平稳，识别不到流量周期'
                            is_develop = '待定'
                else:
                    if price_trend == '上升':
                        if judgement_identify_traffic_cycle(reason=reason_develop):
                            # 可以识别到流量周期
                            if judgement_catch_up_traffic_cycle(reason=reason_develop):
                                # 可以赶上流量周期
                                reason = '数据完整，销量<50，价格趋势上升，能赶上流量周期'
                                is_develop = '待定'
                            else:
                                # 赶不上流量周期
                                reason = '数据完整，销量<50，价格趋势上升，赶不上流量周期'
                                is_develop = '不开发'
                        else:
                            reason = '数据完整，销量<50，价格趋势上升，识别不到流量周期'
                            is_develop = '待定'
                    else:
                        reason = '数据完整，销量<50，价格趋势波动/下降/平稳'
                        is_develop = '不开发'


            else:
                # 数据不完整
                if sales is None:
                    reason = '待定'
                    is_develop = '数据不完整，没有销量'
                elif price_trend is None:
                    reason = '待定'
                    is_develop = '数据不完整，有销量没有价格趋势'
                else:
                    reason = '追踪'
                    is_develop = '数据不完整，有销量，有价格趋势，没有流量周期'
        else:
            pass

        explanations.append(reason)
        isDevelop.append(is_develop)
    df["开发结论"] = isDevelop
    df["开发结论说明"] = explanations


    # 如果提供了输出路径，则保存到Excel
    if output_path:
        # 确保输出目录存在
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df.to_excel(output_path, index=False)
        return df, output_path

    return df


def judgment_data_complete(masterKind:str,slaverKind:str,price:str=None, has_traffic_reason:str=None, pcs_reason:str=None, price_trend:str=None, sales:str=None)->bool:
    if masterKind == 'toys&games' and slaverKind == 'plates':
        if price is None or '未识别到明显周期' in has_traffic_reason or 'pcs解析失败' in pcs_reason:
            return False
    elif masterKind == 'toys&games' and slaverKind == 'banners':
        if price_trend is None or sales is None:
            return False
    return True

def judgment_person_rule(reason:str)->bool:
    return '该类目下没有' not in reason

def judgement_pass_person_rule(reason:str)->bool:
    return '通过规则校验' in reason

def judgement_identify_traffic_cycle(reason:str)->bool:
    return '未识别到流量周期' not in reason

def judgement_catch_up_traffic_cycle(reason:str)-> bool:
    if '可赶上' in reason:
        return True
    else:
        return False
if __name__ == '__main__':
    # analyze_product_value_nr(data='./result/流量周期分析结果_20251230.xlsx', output_path='result/nr/潜在价值结果/分析后_潜在价值_20251230.xlsx')
    analyze_product_value_bs(data='./result/bs/流量周期分析结果_20260104.xlsx',
                             output_path='result/bs/潜在价值结果/分析后_潜在价值_20260104.xlsx')
