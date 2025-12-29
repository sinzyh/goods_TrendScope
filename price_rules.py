from typing import Dict, Tuple, Union, Mapping


# 单个数量对应的价格阈值类型：
# - float: 普通阈值
# - dict: 特殊规则（例如 60pcs 里区分 9inch / 7inch）
PriceRuleValue = Union[float, Dict[str, float]]
PriceRules = Dict[int, PriceRuleValue]


# Toys&Games / Plates 类目的价格规则（从「根据条件过滤BS文件.py」中抽离）
TOYS_GAMES_PLATES_RULES: PriceRules = {
    40: 16.99,
    48: 11.99,
    60: {  # 特殊尺寸规则
        "9inch": 14.99,
        "7inch": 11.99,
    },
    96: 15.99,
    100: 16.99,
    150: 18.99,
    162: 18.99,
    168: 25.99,
    200: 21.99,
    300: 24.99,
    350: 26.99,
}


# 通过 (main_menu, sub_menu) 组合来选择规则。
# 这里按照类目精确绑定，例如：
#   main_menu='Toys&Games', sub_menu='Plates'
# 时会使用 TOYS_GAMES_PLATES_RULES 这套规则。
PRICE_RULES_BY_MENU: Dict[Tuple[str, str], PriceRules] = {
    ("toys&games", "plates"): TOYS_GAMES_PLATES_RULES,
}


def get_price_rules(main_menu: str, sub_menu: str) -> PriceRules:
    """
    根据 main_menu + sub_menu 组合选择价格规则。

    当前策略：
    1. 只尝试精确匹配 (main_menu.lower(), sub_menu.lower())
    2. 若未命中，则返回空字典（表示当前类目未配置价格规则）
    """
    key = (main_menu.strip().lower(), sub_menu.strip().lower())

    return PRICE_RULES_BY_MENU.get(key, {})


