from io import BytesIO
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, Fill, PatternFill, Border, Side
import os


def excel_colwidth_to_pixels(width):
    if width is None:
        return 100
    return int(width * 7)


def excel_rowheight_to_pixels(height):
    if height is None:
        return 80
    return int(height * 1.33)


def split_excel_by_description_with_images(
    input_path: str,
    output_path: str,
    desc_col_name: str = "是否开发"
):
    wb = load_workbook(input_path)
    src_ws = wb.worksheets[0]

    headers = [cell.value for cell in src_ws[1]]
    if desc_col_name not in headers:
        raise ValueError(f"未找到列：{desc_col_name}")

    desc_col_idx = headers.index(desc_col_name) + 1
    
    # 找到"图片"列的索引（如果存在）
    img_col_idx = None
    if "图片" in headers:
        img_col_idx = headers.index("图片") + 1
    
    # 需要设置文本换行的列
    wrap_text_columns = ["商品链接", "产品标题", "主题", "核心词周期", "原因", "商品潜力说明"]
    wrap_text_col_indices = {}
    for col_name in wrap_text_columns:
        if col_name in headers:
            wrap_text_col_indices[headers.index(col_name) + 1] = col_name
    
    # 创建文本换行的对齐方式
    wrap_alignment = Alignment(wrap_text=True, vertical='top')

    # 记录列宽
    src_col_widths = {
        idx: src_ws.column_dimensions[get_column_letter(idx)].width
        for idx in range(1, len(headers) + 1)
    }

    # 记录行高
    src_row_heights = {
        row: src_ws.row_dimensions[row].height
        for row in range(1, src_ws.max_row + 1)
    }

    # 行 → 图片（预先读取所有图片数据到内存）
    row_images = {}
    for img in src_ws._images:
        row = img.anchor._from.row + 1
        try:
            # 立即读取图片数据到内存，避免文件流关闭的问题
            img_data = img._data()
            # 确保数据被完全读取到内存（转换为bytes）
            if hasattr(img_data, 'read'):
                # 如果是文件流，读取所有数据
                img_bytes = img_data.read()
                img_data.close()  # 关闭原始流
            else:
                # 如果已经是bytes，直接使用
                img_bytes = img_data
            # 将字节数据存储为元组：(图片字节数据, 列索引, 宽度, 高度)
            col_idx = img.anchor._from.col + 1
            row_images.setdefault(row, []).append((img_bytes, col_idx, img.width, img.height))
        except Exception as e:
            print(f"读取图片数据失败（行 {row}）: {e}")

    # 分组
    group_rows = {}
    for row_idx in range(2, src_ws.max_row + 1):
        desc = src_ws.cell(row=row_idx, column=desc_col_idx).value
        desc = str(desc).strip() if desc else "未分类"
        group_rows.setdefault(desc, []).append(row_idx)

    new_wb = Workbook()
    ws_original = new_wb.active
    ws_original.title = "源数据"
    
    # 定义sheet创建顺序和说明内容
    sheet_order = ["源数据", "开发", "追踪", "待定", "不开发"]
    sheet_descriptions = {
        "开发": ["（1）开发", "\t经验判断为是，价格上升"],
        "追踪": [
            "（2）追踪",
            "\t经验判断为是，价格下降",
            "\t经验判断为是，价格波动",
            "\t经验判断为否，赶不上流量周期 and 价格上升",
            "\t经验判断为否，识别不到流量周期 and 价格上升",
            "\t经验判断为否，没有规则 and 价格上升",
            "\t经验判断为待定，价格上升"
        ],
        "待定": [
            "（3）待定",    
            "\t经验判断为待定，价格趋势需要人为判断"
        ],
        "不开发": [
            "（4）不开发",
            "\t经验判断为否，赶不上流量周期 and 价格下降",
            "\t经验判断为否，赶不上流量周期 and 价格波动",
            "\t经验判断为否，价格过低",
            "\t经验判断为否，识别不到流量周期 and 其它价格趋势",
            "\t经验判断为否，没有对应规则 and 其它价格趋势",
            "\t经验判断为待定，价格下降"
        ]
    }

    # 复制函数，用于复制一行数据到目标工作表
    def copy_row_to_sheet(src_ws, target_ws, old_row, new_row_idx, headers, wrap_text_col_indices, wrap_alignment, src_row_heights, row_images, src_col_widths, img_col_idx):
        # 写单元格
        for col_idx in range(1, len(headers) + 1):
            cell = target_ws.cell(
                row=new_row_idx,
                column=col_idx,
                value=src_ws.cell(row=old_row, column=col_idx).value
            )
            # 如果是需要换行的列，设置对齐方式为换行
            if col_idx in wrap_text_col_indices:
                cell.alignment = wrap_alignment

        # 复制行高
        if src_row_heights.get(old_row):
            target_ws.row_dimensions[new_row_idx].height = src_row_heights[old_row]

        # 复制图片（核心修复）
        if old_row in row_images:
            for img_data_tuple in row_images[old_row]:
                try:
                    img_bytes, col_idx, original_width, original_height = img_data_tuple
                    # 从内存中的字节数据创建新的图片
                    stream = BytesIO(img_bytes)
                    new_img = XLImage(stream)

                    col_letter = get_column_letter(col_idx)

                    # 计算目标像素尺寸
                    col_width = src_col_widths.get(col_idx)
                    row_height = src_row_heights.get(old_row)

                    max_w = excel_colwidth_to_pixels(col_width)
                    max_h = excel_rowheight_to_pixels(row_height)
                    
                    # 如果当前图片是"图片"列中的内容，则高度只取一半
                    if img_col_idx is not None and col_idx == img_col_idx:
                        max_h = max_h // 2

                    # 限制尺寸（关键）
                    new_img.width = min(new_img.width, max_w)
                    new_img.height = min(new_img.height, max_h)

                    target_ws.add_image(new_img, f"{col_letter}{new_row_idx}")

                except Exception as e:
                    print(f"图片复制失败（行 {old_row}）: {e}")

    # 1. 第一个sheet：复制所有原始数据
    # 写表头
    for col_idx, header in enumerate(headers, 1):
        ws_original.cell(row=1, column=col_idx, value=header)

    # 复制列宽
    for col_idx, width in src_col_widths.items():
        if width:
            ws_original.column_dimensions[get_column_letter(col_idx)].width = width

    original_row_idx = 2
    for old_row in range(2, src_ws.max_row + 1):
        copy_row_to_sheet(
            src_ws, ws_original, old_row, original_row_idx,
            headers, wrap_text_col_indices, wrap_alignment,
            src_row_heights, row_images, src_col_widths, img_col_idx
        )
        original_row_idx += 1

    # 定义说明内容的样式
    title_font = Font(name='Microsoft YaHei', size=12, bold=True, color='FFFFFF')
    title_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    content_font = Font(name='Microsoft YaHei', size=10)
    content_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    border_style = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000')
    )
    
    # 2. 其他sheet：按照指定顺序创建
    for sheet_name in sheet_order[1:]:  # 跳过"源数据"，从"开发"开始
        if sheet_name not in group_rows:
            continue  # 如果该分组没有数据，跳过
            
        rows = group_rows[sheet_name]
        ws_new = new_wb.create_sheet(sheet_name[:31])
        
        # 添加说明内容（如果存在）
        description_start_row = 1
        if sheet_name in sheet_descriptions:
            descriptions = sheet_descriptions[sheet_name]
            max_col = min(len(headers), 10)  # 最多合并10列，让说明内容跨越多列
            for desc_row_idx, desc_text in enumerate(descriptions, start=1):
                cell = ws_new.cell(row=desc_row_idx, column=1, value=desc_text)
                # 应用样式
                if desc_text.startswith('（'):  # 标题行（以括号开头的）
                    cell.font = title_font
                    cell.fill = title_fill
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                else:  # 内容行
                    cell.font = content_font
                    cell.fill = content_fill
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                cell.border = border_style
                # 合并单元格，让说明内容跨越多列
                ws_new.merge_cells(start_row=desc_row_idx, start_column=1, 
                                  end_row=desc_row_idx, end_column=max_col)
            # 设置说明区域的行高
            for desc_row_idx in range(1, len(descriptions) + 1):
                ws_new.row_dimensions[desc_row_idx].height = 20
            description_start_row = len(descriptions) + 2  # 说明内容后空一行再写表头

        # 写表头
        for col_idx, header in enumerate(headers, 1):
            ws_new.cell(row=description_start_row, column=col_idx, value=header)

        # 复制列宽
        for col_idx, width in src_col_widths.items():
            if width:
                ws_new.column_dimensions[get_column_letter(col_idx)].width = width

        # 数据从表头下一行开始
        new_row_idx = description_start_row + 1

        for old_row in rows:
            copy_row_to_sheet(
                src_ws, ws_new, old_row, new_row_idx,
                headers, wrap_text_col_indices, wrap_alignment,
                src_row_heights, row_images, src_col_widths, img_col_idx
            )
            new_row_idx += 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_wb.save(output_path)

    print(f"✅ 已完成拆分并保持图片大小：{output_path}")


if __name__ == '__main__':
    split_excel_by_description_with_images(input_path='result/bs/流量周期分析结果_20260104.xlsx', output_path='result/bs/潜在价值结果/分类后_潜在价值_20260104-2.xlsx')