import ast
import json
from typing import Dict, Optional
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from can_develop_today import can_develop
from detect_low_flow_months import detect_low_flow_months
from determining_traffic_cycle import determine_traffic_cycle
from extract_keyword_series import extract_keyword_series
from format_traffic_cycle_text import format_traffic_cycle_text
from get_last_month_saler import get_last_month_saler
from pass_rule import pass_rule
from plot_search_trend import plot_traffic_cycle_json_to_bytes, plot_sales_trend_to_bytes, plot_price_trend_to_bytes
from price_trend_detector import clean_price_and_time, classify_price_trend


def load_and_merge_data(file_path1: str, file_path2: str) -> pd.DataFrame:
    """加载并合并两个Excel文件"""
    df1 = pd.read_excel(file_path1)
    df2 = pd.read_excel(file_path2)
    # 确保 asin 是字符串（非常重要）
    df1["asin"] = df1["asin"].astype(str)
    df2["asin"] = df2["asin"].astype(str)
    df2_selected = df2[["asin", "sell_trend", "year", "search_trend"]]

    df = df1.merge(
        df2_selected,
        on="asin",
        how="left"
    )

    df = df.rename(columns={
        "sell_trend": "销量数据",
        "year": "上架时间",
        "search_trend": "核心词周期数据"
    })
    return df


def extract_themes_from_titles(titles: list, llm: ChatOpenAI) -> list:
    """从标题中提取主题（使用LLM）"""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
    你是一名亚马逊产品开发专家，擅长从竞品标题中提取【核心主题】。

    【什么是主题】
    主题是产品围绕的核心概念、IP 或派对类型，通常是一个或两个英文名词，
    例如节日、IP、派对主题，而不是产品规格或配件名称。

    【提取规则（非常重要）】
    1. 主题必须是一个简短英文名词或名词短语
    2. 只提取"最核心的主题"，不要包含产品类型
    3. 忽略以下信息：
       - 数量与规格（如：PCS、Serves 16、197 Pcs）
       - 年份（如：2024、2025、2026）
       - 泛品类词（Party Supplies, Decorations, Tableware, Plates, Napkins 等）
    4. 如果是节日类，主题就是节日名称（如：New Years）
    5. 如果是派对 / IP / 图案类，主题就是该派对或 IP 名称（如：Building Blocks）
    6. 每个标题只返回一个主题
    7. 只返回结果，不要解释
    8. 返回结果应该是一个数组，主题顺序应与输入标题的顺序相同。
    【示例】
    输入标题：
    New Years Eve Party Supplies 2026, Happy New Years Party Decorations...

    输出：
    New Years

    输入标题：
    197 Pcs Building Blocks Birthday Paper Plates Tableware Set...

    输出：
    Building Blocks
            """.strip()
        ),
        (
            "human",
            "请按上述规则，从以下竞品标题中提取主题（按顺序，一一对应）：\n{titles}"
        )
    ])

    messages = prompt.format_messages(titles=titles)
    # resp = llm.invoke(messages)
    # return resp.content
    
    # 模拟数据（实际使用时取消注释上面的代码）
    return ["Grinch", "New Year", "Demon Hunters", "New Year", "New Year", "New Year", "New Year", "New Year",
            "New Year", "New Year", "Christmas", "New Year", "New Year", "New Year", "New Year", "Christmas", 
            "Christmas", "Birthday", "New Year", "Gingerbread House", "Christmas", "Christmas", "Winter Wonderland", 
            "Christmas", "Christmas", "New Year", "Christmas", "New Year", "Winter Wonderland", "Black and Gold", 
            "Christmas", "Christmas", "New Year", "Santa Claus", "Christmas", "Christmas Tree", "Monster", "New Year", 
            "North Pole", "New Year", "New Year", "New Year", "New Year", "New Year", "Mario", "Half Birthday", 
            "Cheetah Print", "Apres Ski", "Race Car", "Christmas", "Christmas", "Winter Wonderland", "Christmas", 
            "New Year", "New Year", "Christmas", "Christmas", "Christmas", "New Year", "New Year", "New Year", 
            "Christmas", "Winter Wonderland", "Christmas", "Valentines Day", "New Year", "Christmas", "Candy Cane", 
            "Winter Forest", "Winter Wonderland", "Half Birthday", "New Year", "North Pole", "New Year", "Showgirl", 
            "Stranger Things", "Tet", "Christmas", "New Year", "Christmas", "New Year", "Christmas", "Oh Twodles", 
            "Christmas", "New Year", "25th Birthday", "Gingerbread House", "New Year", "Coffee", "Christmas", 
            "Christmas", "New Year", "Christmas", "New Year", "Jesus", "New Year", "Winter Wonderland", "New Year", 
            "New Year"]


def load_price_trend_data(file_path: str) -> Dict:
    """加载价格趋势JSON文件"""
    price_trend_data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            price_trend_data = json.load(f)
        print(f'成功读取价格趋势数据，共 {len(price_trend_data)} 个ASIN')
    except FileNotFoundError:
        print(f'警告: 未找到价格趋势文件 {file_path}，将跳过价格趋势图')
    except Exception as e:
        print(f'读取价格趋势文件时出错: {e}')
        import traceback
        traceback.print_exc()
    return price_trend_data


def parse_json_data(data_str):
    """解析JSON字符串数据"""
    if isinstance(data_str, str):
        try:
            return ast.literal_eval(data_str)
        except:
            return None
    return data_str


def process_row_data(
    idx: int,
    row: pd.Series,
    df: pd.DataFrame,
    price_trend_data: Dict,
    traffic_cycle_images: Dict[int, Optional[bytes]],
    sales_trend_images: Dict[int, Optional[bytes]],
    price_trend_images: Dict[int, Optional[bytes]]
):
    """处理单行数据"""
    title = row['产品标题']
    asin = row['asin']
    traffic_cycle_json = row['核心词周期数据']
    sales_json = row['销量数据']
    price = row['价格']

    # 解析JSON数据
    if isinstance(traffic_cycle_json, str):
        try:
            traffic_cycle_json = parse_json_data(traffic_cycle_json)
        except:
            print('核心词周期数据太长被截断')
            return

    if isinstance(sales_json, str):
        try:
            sales_json = parse_json_data(sales_json)
        except:
            print('销量json太长被截断')
            return

    # 添加流量周期图
    try:
        if traffic_cycle_json:
            if isinstance(traffic_cycle_json, str):
                try:
                    traffic_cycle_json = parse_json_data(traffic_cycle_json)
                except:
                    print(f"  第{idx}行: 无法解析 traffic_cycle_json 字符串")
                    traffic_cycle_images[idx] = None
                    return

            if isinstance(traffic_cycle_json, dict):
                data_list = traffic_cycle_json.get("data", [])
                if data_list and len(data_list) > 0:
                    image_bytes = plot_traffic_cycle_json_to_bytes(traffic_cycle_json)
                    if image_bytes:
                        traffic_cycle_images[idx] = image_bytes.getvalue()
                        print(f"  第{idx}行: 成功绘制流量周期图（{len(data_list)}个关键词）")
                    else:
                        print(f"  第{idx}行: 绘制失败，data 有 {len(data_list)} 项但无法生成图片")
                        traffic_cycle_images[idx] = None
                else:
                    print(f"  第{idx}行: traffic_cycle_json 的 data 为空")
                    traffic_cycle_images[idx] = None
            else:
                print(f"  第{idx}行: traffic_cycle_json 不是字典格式，类型为 {type(traffic_cycle_json)}")
                traffic_cycle_images[idx] = None
        else:
            print(f"  第{idx}行: traffic_cycle_json 为空")
            traffic_cycle_images[idx] = None
    except Exception as e:
        print(f"  第{idx}行: 绘制流量周期图时出错: {e}")
        import traceback
        traceback.print_exc()
        traffic_cycle_images[idx] = None

    # 添加销量趋势图
    try:
        if sales_json and isinstance(sales_json, list) and len(sales_json) > 0:
            image_bytes = plot_sales_trend_to_bytes(sales_json)
            if image_bytes:
                sales_trend_images[idx] = image_bytes.getvalue()
                print(f"  第{idx}行: 成功绘制销量趋势图")
            else:
                print(f"  第{idx}行: 绘制销量趋势图失败")
                sales_trend_images[idx] = None
        else:
            if not sales_json:
                print(f"  第{idx}行: sales_json 为空")
            elif not isinstance(sales_json, list):
                print(f"  第{idx}行: sales_json 不是列表格式，类型为 {type(sales_json)}")
            else:
                print(f"  第{idx}行: sales_json 列表为空")
            sales_trend_images[idx] = None
    except Exception as e:
        print(f"  第{idx}行: 绘制销量趋势图时出错: {e}")
        import traceback
        traceback.print_exc()
        sales_trend_images[idx] = None

    # 添加价格趋势图和判断价格趋势类型
    try:
        if asin in price_trend_data:
            price_info = price_trend_data[asin]
            price_trend = price_info.get("price_trend", [])
            times = price_info.get("times", [])
            
            # 清洗价格和时间数据
            times_clean, prices_clean = clean_price_and_time(times, price_trend)
            
            # 判断价格趋势类型
            if prices_clean and len(prices_clean) >= 3:
                try:
                    trend_result, detail = classify_price_trend(prices_clean, times_clean, sales_data=sales_json)
                    df.loc[idx, '价格趋势类型'] = trend_result
                    print(f"  第{idx}行: 价格趋势类型 = {trend_result}（有效数据点: {len(prices_clean)}，使用销量筛选）")
                except Exception as e:
                    print(f"  第{idx}行: 判断价格趋势类型时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    df.loc[idx, '价格趋势类型'] = "未知"
            else:
                print(f"  第{idx}行: 价格数据不足（有效数据点: {len(prices_clean) if prices_clean else 0}，需要至少3个）")
                df.loc[idx, '价格趋势类型'] = "数据不足"
            
            # 绘制价格趋势图
            if price_trend and times and len(price_trend) == len(times):
                image_bytes = plot_price_trend_to_bytes(price_trend, times)
                if image_bytes:
                    price_trend_images[idx] = image_bytes.getvalue()
                    print(f"  第{idx}行: 成功绘制价格趋势图")
                else:
                    print(f"  第{idx}行: 绘制价格趋势图失败（数据过滤后为空或无有效数据）")
                    price_trend_images[idx] = None
            else:
                print(f"  第{idx}行: 价格趋势数据不完整（price_trend: {len(price_trend) if price_trend else 0}, times: {len(times) if times else 0}）")
                price_trend_images[idx] = None
        else:
            print(f"  第{idx}行: 未找到ASIN {asin} 的价格趋势数据")
            df.loc[idx, '价格趋势类型'] = "无数据"
            price_trend_images[idx] = None
    except Exception as e:
        print(f"  第{idx}行: 处理价格趋势时出错: {e}")
        import traceback
        traceback.print_exc()
        df.loc[idx, '价格趋势类型'] = "处理失败"
        price_trend_images[idx] = None

    # 处理核心词搜索量数据
    traffic_cycle_series, start_month_str, end_month_str = extract_keyword_series(traffic_cycle_json)
    traffic_cycle_list = list(traffic_cycle_series.values())
    
    # 解析销量数据
    sales = get_last_month_saler(sales_json)
    df.loc[idx, '上月销量'] = sales
    
    # 计算流量周期
    if start_month_str is None or end_month_str is None:
        traffic_cycle = []
        flow_type = []
    else:
        traffic_cycle, flow_type = determine_traffic_cycle(traffic_cycle_list, start_month_str, end_month_str)
    
    # 计算低谷流量周期
    if start_month_str is None or end_month_str is None or len(traffic_cycle) == 0:
        low_months = []
    else:
        low_months = detect_low_flow_months(
            traffic_values=traffic_cycle_list,
            start_time=start_month_str,
            end_time=end_month_str,
            traffic_cycle=traffic_cycle
        )
    
    # 格式化流量周期文本
    if flow_type is None or traffic_cycle is None or low_months is None:
        core_word_cell_text = '采集的数据不全'
    else:
        core_word_cell_text = format_traffic_cycle_text(
            flow_type=flow_type,
            traffic_cycle=traffic_cycle,
            low_months=low_months
        )

    df.loc[idx, '核心词周期'] = str(core_word_cell_text)
    
    # 根据规则判断是否开发
    if sales is None or price is None:
        result = False
        reason = '销量或价格是空'
        pcs = None
    else:
        result, reason, pcs = pass_rule(main_menu='Toys&Games', sub_menu='Plates', sales=sales, price=price, title=title)
    
    df.loc[idx, 'pcs'] = str(pcs) + ' pcs' if pcs is not None else ''
    
    if pcs is None:
        df.loc[idx, '是否开发'] = '待定'
        df.loc[idx, '原因'] = reason
        return
    
    if price is None:
        df.loc[idx, '是否开发'] = '待定'
        df.loc[idx, '原因'] = '上月无参照价格'
        return
    
    if result:
        can_dev, timing_reason = can_develop(traffic_cycle)
        if result and can_dev:
            df.loc[idx, '是否开发'] = '是'
            df.loc[idx, '原因'] = reason + '；' + timing_reason
        else:
            df.loc[idx, '是否开发'] = '否'
            df.loc[idx, '原因'] = reason + '；' + timing_reason
    else:
        df.loc[idx, '是否开发'] = '否'
        df.loc[idx, '原因'] = reason

