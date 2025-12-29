# goods_TrendScope

商品流量周期分析与价格趋势预测系统

## 📋 项目背景

`goods_TrendScope` 是一个专为亚马逊产品开发设计的智能分析工具。在竞争激烈的电商市场中，准确把握产品的流量周期和价格趋势是成功开发新产品的关键。本系统通过分析竞品的核心关键词搜索量、历史销量和价格变化，帮助产品开发团队：

- **识别流量周期**：准确判断产品的季节性流量高峰和低谷
- **预测价格趋势**：分析价格变化方向（上升/下降/平稳/波动）
- **优化开发时机**：评估当前时间点是否适合开发新产品
- **数据驱动决策**：基于多维度数据分析提供开发建议

系统特别适用于具有明显季节性特征的产品（如节日用品、季节性装饰品等），通过科学的算法分析，为产品开发提供量化依据。

## 📥 输入数据

系统需要以下输入文件：

### 1. BS榜单数据 (`best-sellers-*.xlsx`)
包含竞品的基础信息：
- `asin`: 产品ASIN码
- `产品标题`: 产品标题
- `价格`: 当前价格
- `图片链接`: 产品图片URL
- 其他产品属性

### 2. 卖家精灵数据 (`crawl-*-bsr.xlsx`)
包含竞品的详细数据：
- `asin`: 产品ASIN码（用于关联）
- `sell_trend`: 历史销量数据（JSON格式，`[{'dk': 'YYYYMM', 'sales': int}, ...]`）
- `year`: 产品上架时间
- `search_trend`: 核心关键词搜索量数据（JSON格式，包含多个关键词的时间序列）

### 3. 价格趋势数据 (`crawl-*-price-trend.json`)
包含竞品的历史价格数据：
```json
{
  "ASIN码": {
    "price_trend": [价格1, 价格2, ...],
    "times": ["时间1", "时间2", ...]
  }
}
```

## 📤 输出结果

系统生成一个Excel分析报告（`流量周期分析结果_YYYYMMDD.xlsx`），包含以下列：

| 列名 | 说明 |
|------|------|
| 图片链接 | 产品图片URL |
| asin | 产品ASIN码 |
| 产品标题 | 产品标题 |
| 主题 | 从标题提取的核心主题（如"Christmas"、"New Year"等） |
| 上架时间 | 产品上架年份 |
| 核心词周期图 | 核心关键词搜索量趋势可视化图表 |
| 核心词周期 | 流量周期分析结果（文本描述） |
| 销量趋势图 | 历史销量柱状图 |
| 上月销量 | 最近一个月的销量 |
| 价格趋势图 | 价格变化趋势折线图 |
| 价格趋势类型 | 价格趋势分类（上升/下降/平稳/波动） |
| 价格 | 当前价格 |
| pcs | 推荐的产品数量 |
| 是否开发 | 开发建议（是/否/待定） |
| 原因 | 开发建议的详细原因 |

## 🔍 流量周期算法

### 算法概述

流量周期算法通过分析多个核心关键词的搜索量时间序列，识别产品的季节性流量模式。算法采用**多关键词投票机制**，综合多个关键词的分析结果，提高周期识别的准确性。

### 核心步骤

#### 1. 月度有效贡献度计算

对每个关键词的时间序列，计算每个月份的有效季节性贡献度：

```python
# 年内标准化
normalized = series / series.groupby(series.index.year).transform("mean")

# 只保留高于整体均值的"超额"部分
mean_val = normalized.mean()
excess = (normalized - mean_val).clip(lower=0)

# 按月份聚合超额贡献
monthly_contrib = excess.groupby(series.index.month).sum()

# 归一化到 0-1
monthly_ratio = monthly_contrib / monthly_contrib.sum()
```

**原理**：通过计算每个月份相对于年度均值的超额贡献，识别出哪些月份具有明显的季节性特征。

#### 2. 峰值窗口识别

在12个月度贡献度上寻找所有候选峰值窗口：

- **窗口大小**：支持2-11个月的连续月份窗口
- **约束条件**：
  - 窗口内所有月份必须连续
  - 窗口内所有月份贡献度必须为正
  - 窗口总贡献度必须 ≥ 0.05（可配置）
- **去重**：移除被更大窗口完全包含的子窗口

**示例**：如果识别出 `[10, 11, 12]` 和 `[11, 12]` 两个窗口，则只保留 `[10, 11, 12]`。

#### 3. 稳定性评估

计算峰值窗口在不同年份之间的稳定性：

```python
stability = min(窗口均值 / 全年均值)  # 跨所有年份
```

**稳定性指标**：
- `stability < 1.15`: 全年流量型（流量分布相对均匀）
- `1.15 ≤ stability < 1.3`: 混合季节型（有一定季节性但不强烈）
- `stability ≥ 1.3`: 强周期型（季节性特征明显）

#### 4. 流量类型分类

根据主峰的**季节性强度（score）**和**稳定性（stability）**进行分类：

- **强周期型**：`score ≥ 0.65` 且 `stability ≥ 1.3`
- **全年流量型**：`0 < stability < 1.15`
- **混合季节型**：其他情况
- **未知**：无法识别有效周期

#### 5. 多关键词投票

对每个关键词独立分析后，采用投票机制确定最终周期：

1. **周期投票**：统计每个周期窗口的出现次数
2. **流量类型投票**：统计每个流量类型的出现次数
3. **最终选择**：选择出现次数最多的周期和流量类型

**特殊情况处理**：
- 如果所有周期出现次数都为1，则统计每个月份的出现次数，找出最长的连续月份周期
- 如果多个周期有交集，计算交集作为最终周期
- 如果所有关键词都无法识别周期，返回"未知"

#### 6. 低谷月份识别

在识别出旺季周期后，进一步识别低谷月份：

1. **排除旺季**：只从非旺季月份中选择
2. **贡献比例**：计算每个非旺季月份对全年流量的贡献比例
3. **累积筛选**：选择贡献比例累积 ≤ 20% 的月份作为低谷月份
4. **关键词投票**：多个关键词投票决定最终低谷月份

## 💰 价格趋势算法

### 算法概述

价格趋势算法通过Mann-Kendall趋势检验、分位数分析和波动率计算，综合判断价格的变化趋势。算法特别考虑了**销量数据**，只分析有销量的月份对应的价格，提高趋势判断的准确性。

### 核心步骤

#### 1. 数据清洗

- **时间解析**：将时间字符串转换为datetime对象
- **价格规范化**：处理列表、元组、标量等不同格式的价格数据
- **有效性过滤**：排除None值和无效数据

#### 2. 销量筛选（可选）

如果提供了销量数据，只使用有销量的月份对应的价格数据：

```python
# 提取有销量的月份（销量 > 0）
sales_months = {item['dk'] for item in sales_data if item.get('sales', 0) > 0}

# 筛选价格数据
filtered_prices = [p for p, t in zip(prices, times) 
                   if t.strftime('%Y%m') in sales_months]
```

**优势**：避免无销量期间的价格波动干扰趋势判断。

#### 3. 时间窗口选择

- **有销量数据**：使用所有筛选后的数据（不限制天数）
- **无销量数据**：选择最近60天的数据（可配置）

#### 4. Mann-Kendall趋势检验

使用Mann-Kendall非参数检验判断价格序列是否存在显著趋势：

```python
mk_result = mk.original_test(recent_prices)
has_trend = mk_result.p < 0.05  # 显著性水平
trend_dir = mk_result.trend  # increasing / decreasing / no trend
```

**优势**：Mann-Kendall检验对异常值不敏感，适合价格数据。

#### 5. 分位数分析

计算价格的分位数，判断当前价格在历史价格中的位置：

```python
high_q = np.percentile(prices, 90)  # 90分位数
low_q = np.percentile(prices, 10)   # 10分位数
latest = recent_prices[-1]

high_position = latest >= 0.8 * high_q  # 接近高位
low_position = latest <= 1.2 * low_q    # 接近低位
```

#### 6. 波动率计算

计算价格的变异系数（CV）：

```python
volatility = np.std(recent_prices) / (np.mean(recent_prices) + 1e-9)
```

#### 7. 趋势分类

综合多个指标进行分类：

| 条件 | 分类结果 |
|------|---------|
| 有上升趋势 + 波动率低 + 价格高于均值 + 接近高位 | **上升** |
| 有下降趋势 + 波动率低 + 价格低于均值 + 接近低位 | **下降** |
| 波动率 ≥ 阈值（0.05） | **波动** |
| 其他情况 | **平稳** |

**判断逻辑**：
- **上升**：需要同时满足趋势向上、价格处于高位、且当前价格高于近期均值
- **下降**：需要同时满足趋势向下、价格处于低位、且当前价格低于近期均值
- **波动**：价格变化剧烈，波动率超过阈值
- **平稳**：无明显趋势且波动较小

## 🏗️ 项目结构

```
goods_TrendScope/
├── main.py                    # 主程序入口
├── data_processor.py          # 数据处理模块
├── excel_handler.py           # Excel操作模块
├── price_trend_detector.py    # 价格趋势检测模块
├── determining_traffic_cycle.py  # 流量周期判断模块
├── detect_low_flow_months.py   # 低谷月份检测模块
├── extract_keyword_series.py   # 关键词序列提取模块
├── format_traffic_cycle_text.py # 流量周期文本格式化
├── get_last_month_saler.py     # 上月销量提取
├── pass_rule.py               # 开发规则判断
├── can_develop_today.py       # 开发时机判断
├── plot_search_trend.py      # 图表绘制模块
├── format_excel_style.py      # Excel样式格式化
├── input_file/                # 输入数据目录
│   └── YYYY-MM-DD/           # 按日期组织的输入文件
└── result/                    # 输出结果目录
```

## 🚀 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，请手动安装依赖包。

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. 准备输入数据

将以下文件放置在 `input_file/YYYY-MM-DD/` 目录下：
- `best-sellers-*.xlsx`: BS榜单数据
- `crawl-*-bsr.xlsx`: 卖家精灵数据
- `crawl-*-price-trend.json`: 价格趋势数据

### 4. 配置参数

在 `main.py` 中修改文件路径：

```python
file_path1 = 'input_file/2025-12-26/best-sellers-20251224_154540.xlsx'
file_path2 = 'input_file/2025-12-26/crawl-20251226-bsr.xlsx'
price_trend_file_path = 'input_file/2025-12-26/crawl-20251226-price-trend.json'
```

### 5. 运行分析

```bash
python main.py
```

### 6. 查看结果

分析结果保存在 `result/流量周期分析结果_YYYYMMDD.xlsx`

## 📊 算法参数说明

### 流量周期算法参数

- `min_score` (默认 0.05): 峰值窗口最小贡献度阈值
- `min_ratio` (默认 0.0): 窗口内月份最小贡献度阈值
- `window_sizes` (默认 [2-11]): 候选窗口大小范围

### 价格趋势算法参数

- `days` (默认 60): 无销量数据时使用的最近天数
- `alpha` (默认 0.05): Mann-Kendall检验的显著性水平
- `vol_threshold` (默认 0.05): 波动率阈值
- `quantile_level` (默认 0.9): 分位数水平（用于判断高位/低位）

## 🔧 依赖环境

### Python 包依赖

```txt
pandas
numpy
openpyxl
matplotlib
pymannkendall
langchain-openai
requests
python-dotenv
```

### 环境变量配置

1. **创建 `.env` 文件**

   在项目根目录创建 `.env` 文件，内容如下：

   ```env
   # OpenAI API配置
   OPENAI_API_KEY=your_api_key_here
   ```

2. **获取 API Key**

   - 将 `your_api_key_here` 替换为你的实际 API key
   - API key 可以从你的 OpenAI 或 302.ai 账户获取

3. **安全提示**

   - `.env` 文件包含敏感信息，请勿提交到版本控制系统
   - 项目已包含 `.env.example` 作为模板（不含真实 key）

## 📝 注意事项

1. **数据质量**：确保输入数据的完整性和准确性，缺失数据会影响分析结果
2. **时间范围**：建议使用至少2年的历史数据，以获得更准确的周期识别
3. **关键词数量**：多个核心关键词可以提高周期识别的准确性
4. **销量筛选**：启用销量筛选可以提高价格趋势判断的准确性

## 📄 许可证

本项目仅供内部使用。

## 👥 贡献者

项目开发团队

---yh z
