import os
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
    insert_product_images
)
from format_excel_style import format_excel_style
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()


def prepare_dataframe_columns(df: pd.DataFrame) -> list:
    """准备DataFrame的列顺序"""
    columns_order = [
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
        "是否开发",
        "原因",
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
    
    # 如果"价格趋势图"列不存在，创建它
    if "价格趋势图" not in df.columns:
        df["价格趋势图"] = None
        if "价格" in columns_order:
            price_idx = columns_order.index("价格")
            columns_order.insert(price_idx, "价格趋势图")
        else:
            columns_order.append("价格趋势图")
    
    # 如果"价格趋势类型"列不存在，创建它
    if "价格趋势类型" not in df.columns:
        df["价格趋势类型"] = None
        if "价格" in columns_order:
            price_idx = columns_order.index("价格")
            columns_order.insert(price_idx, "价格趋势类型")
        else:
            columns_order.append("价格趋势类型")

    return columns_order


if __name__ == '__main__':
    # 1. 加载并合并数据
    file_path1 = 'input_file/2025-12-26/best-sellers-20251224_154540.xlsx'
    file_path2 = 'input_file/2025-12-26/crawl-20251226-bsr.xlsx'
    
    df = load_and_merge_data(file_path1, file_path2)
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
    
    # 3. 加载价格趋势数据
    price_trend_file_path = 'input_file/2025-12-26/crawl-20251226-price-trend.json'
    price_trend_data = load_price_trend_data(price_trend_file_path)
    
    # 4. 初始化图片存储字典
    traffic_cycle_images: Dict[int, Optional[bytes]] = {}
    sales_trend_images: Dict[int, Optional[bytes]] = {}
    price_trend_images: Dict[int, Optional[bytes]] = {}
    
    # 5. 处理每一行数据
    i = 0
    for idx, row in df.iterrows():
        print(f'第{i}行')
        if i in [90]:
            print(i)
        i = i + 1
        
        process_row_data(
            idx=idx,
            row=row,
            df=df,
            price_trend_data=price_trend_data,
            traffic_cycle_images=traffic_cycle_images,
            sales_trend_images=sales_trend_images,
            price_trend_images=price_trend_images
        )
    
    # 6. 准备输出路径和列顺序
    date_str = datetime.now().strftime("%Y%m%d")
    output_path = f'./result/流量周期分析结果_{date_str}.xlsx'
    
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
    
    # 9. 调整Excel文件样式
    print(f'调整{output_path}文件样式')
    format_excel_style(output_path)
    
    print(f'分析结果已保存到 {output_path}')
