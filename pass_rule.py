from typing import Tuple, Union, Optional

import re

from price_rules import get_price_rules


def normalize_title(title: str) -> str:
    """
    统一 title：小写 + 去符号 + 合并空格
    （拷贝自「根据条件过滤BS文件.py」，便于独立使用）
    """
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_pcs(title: str):
    """
    从 title 中提取数量，如：
    96pcs / 96 pcs / 96 PCS / 96 Pieces / 96-piece
    """
    m = re.search(r"(\d+)\s*(pcs|pc|pieces|piece)", title)
    if m:
        return int(m.group(1))
    return None


def parse_price(value):
    """
    把 '$19.75', 'USD 19.75', '19.75$', '$19.75 - $29.99'
    等各种格式转成 float。
    若已是数字则直接返回 float(value)。
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value)
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1))
    return None


def pass_rule(main_menu: str = None, sub_menu: str = None, sales: int = None, price = None, title: str = None, price_trend: str = None) -> \
        Union[None, Tuple[bool, str, None], Tuple[bool, str, int], bool, Tuple[bool, str, Optional[int]], Tuple[
            bool, None, None]]:
    """
    根据「大类(main_menu) + 小类(sub_menu) + 标题 + 价格」判断该产品是否通过价格规则。

    当前逻辑源自「根据条件过滤BS文件.py」：
    - 使用 main_menu + sub_menu 选择价格规则表
    - 从标题中解析出数量（pcs），根据数量找到对应的价格阈值
    - 若为 60pcs，则进一步根据 9inch / 7inch 细分规则
    - 价格达到阈值 => 通过；否则不通过
    - 如果规则是特殊规则（如 banners_rule），则使用特殊处理逻辑

    参数
    ------
    main_menu : str, optional
        一级类目，用于选择规则
    sub_menu : str, optional
        二级类目，用于选择规则
    sales : int, optional
        销量（当前规则未使用，预留扩展）
    price : optional
        价格，可以是 float / int / 字符串（如 '$19.75'）
    title : str, optional
        产品标题
    trend_result : str, optional
        价格趋势 上升/下降/波动/平稳

    返回
    ------
    Tuple[bool, str, Optional[int]]
        (是否通过规则, 原因, pcs数量)
        True 表示通过当前规则；False 表示不通过（包括缺少规则/解析失败等情况）。
    """
    if main_menu == 'toys&games' and sub_menu == 'plates':
        reason = None
        # 1. 标准化标题并解析 pcs 数量
        norm_title = normalize_title(str(title or ""))
        pcs = extract_pcs(norm_title)
        if pcs is None:
            reason = 'pcs解析失败'
            return False, reason, None

        # 2. 解析价格
        numeric_price = parse_price(price)
        if numeric_price is None:
            reason = '解析价格失败'
            return False,reason, pcs

        # 3. 获取对应类目的规则表
        price_rules = get_price_rules(main_menu, sub_menu)
        if not price_rules:
            # 未配置规则，默认不通过；如需“未配置也通过”，可在此返回 True
            reason = '该类目下没有指定规则'
            return False, reason, pcs

        rule = price_rules.get(pcs)
        if rule is None:
            reason = f'该类目下没有{pcs}pcs规则'
            return False, reason, pcs

        # 4. 应用规则
        if isinstance(rule, dict):
            # 60pcs 等特殊尺寸规则
            if "9inch" in norm_title:
                threshold = rule.get("9inch")
                if threshold is None:
                    return False, '该类目下没有9inch规则', pcs
                return numeric_price >= threshold, '通过规则校验', pcs
            if "7inch" in norm_title:
                threshold = rule.get("7inch")
                if threshold is None:
                    return False, '该类目下没有7inch规则', pcs
                return numeric_price >= threshold, '通过规则校验', pcs
            # 找不到尺寸信息则视为不通过
            reason = f'该类目下没有{pcs}pcs规则'
            return False, reason, pcs

        # 普通规则：只比较价格是否达到阈值
        if numeric_price >= float(rule):
            reason = '通过规则校验'
            return True, reason, pcs
        reason = '价格过低'
        return False, reason, pcs
    elif main_menu == 'toys&games' and sub_menu == 'banners':
        # 销量≥50 and 价格趋势上升

        if sales is None:
            reason = '没有销量'
            return False, reason, None

        if price_trend is None:
            reason = '没有价格趋势'
            return False, reason, None

        # 普通规则：只比较价格是否达到阈值
        if sales >= 50 and price_trend == '上升':
            norm_title = normalize_title(str(title or ""))
            pcs = extract_pcs(norm_title)
            if pcs is None:
                reason = '通过规则校验，pcs解析失败'
            else:
                reason = f'通过规则校验'
            return True, reason, pcs
        return False, '没有通过规则校验', None
    else:
        return False, None, None
