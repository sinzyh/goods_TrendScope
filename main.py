import os
import sys

import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

from data_processor import (
    load_and_merge_data,
    extract_themes_from_titles,
    load_price_trend_data,
    process_row_data
)
from excel_handler import (
    insert_traffic_cycle_images,
    insert_sales_trend_images,
    insert_price_trend_images,
    insert_product_images,
    delete_column_from_excel
)
from format_excel_style import format_excel_style
from langchain_openai import ChatOpenAI
from analyze_product_value import analyze_product_value_nr, analyze_product_value_bs

# 加载环境变量
load_dotenv()


def prepare_dataframe_columns(df: pd.DataFrame) -> list:
    """准备DataFrame的列顺序"""
    columns_order = [
        "商品链接",
        "图片链接",
        "asin",
        "产品标题",
        "主题",
        "上架时间",
        "核心词周期图",
        "核心词周期",
        "销量趋势图",
        "上月销量",
        "价格趋势图",
        "价格趋势类型",
        "价格",
        "pcs",
        "规则层建议",
        "季度统计",
        "开发结论",
        "开发结论说明",

    ]

    # 只保留存在的列，防止 KeyError
    columns_order = [col for col in columns_order if col in df.columns]

    # 如果"销量趋势图"列不存在，创建它
    if "销量趋势图" not in df.columns:
        df["销量趋势图"] = None
        if "上月销量" in columns_order:
            sales_idx = columns_order.index("上月销量")
            columns_order.insert(sales_idx, "销量趋势图")
        else:
            columns_order.append("销量趋势图")

    # 如果"核心词周期图"列不存在，创建它
    if "核心词周期图" not in df.columns:
        df["核心词周期图"] = None
        if "核心词周期" in columns_order:
            core_word_idx = columns_order.index("核心词周期")
            columns_order.insert(core_word_idx, "核心词周期图")
        else:
            columns_order.append("核心词周期图")

    # 如果"价格趋势类型"列不存在，创建它（应该在价格趋势图之前）
    if "价格趋势类型" not in df.columns:
        df["价格趋势类型"] = None
        if "价格" in columns_order:
            price_idx = columns_order.index("价格")
            columns_order.insert(price_idx, "价格趋势类型")
        else:
            columns_order.append("价格趋势类型")

    # 如果"价格趋势图"列不存在，创建它（应该在价格趋势类型之后）
    if "价格趋势图" not in df.columns:
        df["价格趋势图"] = None
        if "价格趋势类型" in columns_order:
            trend_type_idx = columns_order.index("价格趋势类型")
            columns_order.insert(trend_type_idx, "价格趋势图")
        elif "价格" in columns_order:
            price_idx = columns_order.index("价格")
            columns_order.insert(price_idx, "价格趋势图")
        else:
            columns_order.append("价格趋势图")

    # 如果"商品链接"列不存在，创建它
    if "商品链接" not in df.columns:
        df["商品链接"] = None
        if "图片链接" in columns_order:
            img_link_idx = columns_order.index("图片链接")
            columns_order.insert(img_link_idx, "商品链接")  # 插入到图片链接之前
        else:
            columns_order.insert(0, "商品链接")

    # 如果"季度数据"列不存在，创建它
    if "季度统计" not in df.columns:
        df["季度统计"] = None
        if "开发结论" in columns_order:
            img_link_idx = columns_order.index("开发结论")
            columns_order.insert(img_link_idx, "季度统计")  # 插入到图片链接之前
        else:
            columns_order.insert(0, "季度统计")
    return columns_order


if __name__ == '__main__':

    # 哪种模式开发
    development_kind = os.getenv('DEVELOPMENT_KIND')

    today = '2026-02-03'

    out_dir = ''
    if development_kind == '榜单开发':
        # 配置参数
        masterKind = 'toys&games'  # 主类目
        slaverKind = 'plates'  # 子类目，可选值: 'plates', 'banners', centerpieces

        # 1. 加载并合并数据
        file_path1 = f'input_file/rank/{today}/best-sellers-{today.replace("-", "")}.xlsx'
        file_path2 = f'input_file/rank/{today}/crawl-{today.replace("-", "")}-bsr.xlsx'
        price_trend_file_path = f'input_file/rank/{today}/crawl-{today.replace("-", "")}-price-trend.json'
        rank_name = 'bs'
        print(f'正在合并{development_kind}数据')
        df = load_and_merge_data(file_path1, file_path2)
        output_dir = f'./result/bs'
    elif development_kind == '店铺开发':
        file_path1 = f'input_file/store/{today}/crawl-{today.replace("-", "")}-store.xlsx'
        price_trend_file_path = f'input_file/store/{today}/crawl-{today.replace("-", "")}-price-trend.json'
        df = pd.read_excel(file_path1)
        df = df.rename(columns={
            'price':'价格',
            "title": "产品标题",
            "sell_trend": "销量数据",
            "year": "上架时间",
            "search_trend": "核心词周期数据"
        })

        if '产品标题' in df.columns:
            # 创建排序键：包含photography的为1（排后），不包含的为0（排前）
            df['_sort_key'] = df['产品标题'].astype(str).str.contains('photography', case=False, na=False).astype(int)
            # 按照排序键排序，然后删除临时列
            df = df.sort_values('_sort_key', kind='stable').drop(columns='_sort_key')
            # 重置索引
            df = df.reset_index(drop=True)
        output_dir = f'./result/store'
    elif development_kind == '类目开发':
        file_path1 = f'input_file/kinds/{today}/asin详细数据-{today}.xlsx'
        price_trend_file_path = f'input_file/kinds/{today}/asin详细数据-{today}.json'
        df = pd.read_excel(file_path1)
        df = df.rename(columns={
            'price':'价格',
            "title": "产品标题",
            "sell_trend": "销量数据",
            "year": "上架时间",
            "search_trend": "核心词周期数据"
        })
        output_dir = f'./result/kinds'
    else:
        df = None
        output_dir = f'./result/None'
    if df is None:
        sys.exit("df is None, exiting.")

    print(df.head())

    # 保存中间结果
    df.to_excel("merged.xlsx", index=False)

    # 2. 提取主题
    titles = df['产品标题'].dropna().astype(str).tolist()

    # 从环境变量读取API key
    api_key = os.getenv('AI_KEY_302')
    if not api_key:
        raise ValueError("未找到 OPENAI_API_KEY 环境变量，请在 .env 文件中设置")

    llm = ChatOpenAI(
        model="gpt-5",
        api_key=api_key,
        base_url="https://api.302.ai/v1"
    )

    title_theme = extract_themes_from_titles(titles, llm)
    df['主题'] = title_theme
    # df['主题'] = [i for i in range(0,100)]

    # 3. 加载价格趋势数据
    price_trend_data = load_price_trend_data(price_trend_file_path)

    # 4. 初始化图片存储字典
    traffic_cycle_images: Dict[int, Optional[bytes]] = {}
    sales_trend_images: Dict[int, Optional[bytes]] = {}
    price_trend_images: Dict[int, Optional[bytes]] = {}

    # 5. 处理每一行数据
    i = 0
    for idx, row in df.iterrows():
        print(f'第{i}行')
        if i in [21]:
            print(i)
        i = i + 1
        # if i == 21:
        #     break
        if development_kind == '榜单开发':
            process_row_data(
                idx=idx,
                row=row,
                df=df,
                price_trend_data=price_trend_data,
                traffic_cycle_images=traffic_cycle_images,
                sales_trend_images=sales_trend_images,
                price_trend_images=price_trend_images,
                masterKind=masterKind,
                slaverKind=slaverKind
            )
        elif development_kind == '店铺开发':
            process_row_data(
                idx=idx,
                row=row,
                df=df,
                price_trend_data=price_trend_data,
                traffic_cycle_images=traffic_cycle_images,
                sales_trend_images=sales_trend_images,
                price_trend_images=price_trend_images,
            )
        elif development_kind == '类目开发':
            process_row_data(
                idx=idx,
                row=row,
                df=df,
                price_trend_data=price_trend_data,
                traffic_cycle_images=traffic_cycle_images,
                sales_trend_images=sales_trend_images,
                price_trend_images=price_trend_images,
            )
        else:
            sys.exit("没有指定开发类型")

    # 6. 准备输出路径和列顺序
    date_str = datetime.now().strftime("%Y%m%d")

    os.makedirs(output_dir, exist_ok=True)
    output_path = f'{output_dir}/流量周期分析结果_{date_str}.xlsx'

    # 6.1 根据ASIN生成商品链接
    df['商品链接'] = df['asin'].apply(lambda asin: f'https://www.amazon.com/dp/{asin}' if pd.notna(asin) else None)

    # 6.2 分析产品潜在价值（在插入图片之前）
    print('开始分析产品潜在价值...')
    # df = analyze_product_value_nr(df, sales_threshold=5)
    if development_kind == '榜单开发':
        df = analyze_product_value_bs(data=df, masterKind=masterKind, slaverKind=slaverKind)
    elif development_kind == '店铺开发':
        df = analyze_product_value_bs(data=df)
    print('产品潜在价值分析完成')

    columns_order = prepare_dataframe_columns(df)
    df = df[columns_order]

    # 7. 保存DataFrame到Excel
    df.to_excel(output_path, index=False)

    # 8. 插入各种图片（需要传递索引映射）
    df_index_mapping = list(df.index)
    insert_traffic_cycle_images(output_path, traffic_cycle_images, df_index_mapping)
    insert_sales_trend_images(output_path, sales_trend_images, df_index_mapping)
    insert_price_trend_images(output_path, price_trend_images, df_index_mapping)
    insert_product_images(output_path)

    # 8.1 删除"图片链接"列
    delete_column_from_excel(output_path, "图片链接")

    # 9. 调整Excel文件样式
    print(f'调整{output_path}文件样式')
    format_excel_style(output_path)

    print(f'分析结果已保存到 {output_path}')

    #*
    # 按照不同类目调用不同分割文件函数
    # *#