"""AI 分析结论生成 — 使用 Claude API 生成专业的分析结论和策略建议"""
import json
from pathlib import Path
import anthropic
from app.config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_MODEL

# ---- 磁盘缓存 ----
_INSIGHT_CACHE_PATH = Path(__file__).parent.parent.parent / "培训_数据源" / "insight_cache.json"


def load_insight_cache() -> dict:
    """读取磁盘缓存"""
    if _INSIGHT_CACHE_PATH.exists():
        with open(_INSIGHT_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_insight(key: str, text: str):
    """写入单条缓存到 JSON"""
    cache = load_insight_cache()
    cache[key] = text
    with open(_INSIGHT_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_cached_insight(key: str) -> str:
    """读取单条缓存，不存在返回空字符串"""
    return load_insight_cache().get(key, "")


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)


def generate_section_insight(section_name: str, data_summary: str, cache_key: str = "") -> str:
    """为单个分析维度生成 2-3 句分析结论（生成后自动写入磁盘缓存）"""
    if not ANTHROPIC_API_KEY:
        # 没有 API key，尝试读缓存
        if cache_key:
            cached = get_cached_insight(cache_key)
            if cached:
                return cached
        return ""

    client = _get_client()
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""你是一位资深的信贷风控分析师，正在撰写客群分析报告的"{section_name}"部分。

以下是该维度的数据摘要：
{data_summary}

请根据数据写出专业、简洁的分析结论。格式与内容要求：

**输出格式（严格遵守）：**
- 分 2-3 个要点，每个要点独占一行
- 每个要点以 **加粗的小标题** 开头，后接冒号和具体分析
- 格式示例：
  **核心发现**：该客群男性占比 71.2%，显著高于行业平均水平...
  **趋势观察**：近 6 个月该指标呈下降趋势，从 xx% 降至 xx%...
  **风险提示**：xx 维度的异常值得关注，建议...

**内容要求：**
1. 引用具体数字，不要泛泛而谈
2. 指出值得关注的趋势或异常
3. 语言专业但易懂，用中文
4. 不要加总标题，直接输出分点内容"""
        }]
    )
    result = message.content[0].text
    if cache_key:
        save_insight(cache_key, result)
    return result


def generate_strategy_report(all_data_summary: dict, cache_key: str = "") -> str:
    """基于所有分析数据，生成综合策略建议"""
    if not ANTHROPIC_API_KEY:
        if cache_key:
            cached = get_cached_insight(cache_key)
            if cached:
                return cached
        return ""

    client = _get_client()
    summary_text = json.dumps(all_data_summary, ensure_ascii=False, default=str)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""你是一位资深的信贷风控分析师，已完成客群分析报告的所有维度分析。以下是完整的数据汇总：

{summary_text}

请基于以上数据，生成一份结构化的策略建议报告，包含以下 4 部分：

## 客群质量评估
概括该机构客群的整体质量水平，与行业大盘对比的优劣势。

## 风险预警信号
指出数据中发现的风险预警信号（如某指标恶化趋势、某人群风险集中等）。

## 准入策略建议
针对发现的风险，给出具体的准入策略调整建议。

## 重点监控指标
列出需要持续关注的关键指标及其预警阈值。

格式要求（严格遵守）：
- 每个 ## 大标题下，用分点（- ）列出 3-5 条具体建议或发现
- 每条分点以 **加粗关键词** 开头，后接冒号和具体说明
- 格式示例：
  ## 客群质量评估
  - **整体质量**：该机构客群信用评分均值 xxx 分，处于行业中上水平...
  - **优势维度**：高收入客群占比 xx%，优于行业大盘...
  - **短板**：多头借贷指标偏高，近 12 月平均申请 xx 次...

内容要求：
- 引用具体数据支撑每个观点
- 语言专业但易懂
- 用中文"""
        }]
    )
    result = message.content[0].text
    if cache_key:
        save_insight(cache_key, result)
    return result


# Pre-built insight generators for each section
# 每个 generator 接受 (data, cache_key="") 两个参数
SECTION_GENERATORS = {
    "gender": lambda data, ck="": generate_section_insight(
        "基础画像-性别",
        f"性别分布数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "age": lambda data, ck="": generate_section_insight(
        "基础画像-年龄",
        f"年龄分布数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "city": lambda data, ck="": generate_section_insight(
        "基础画像-城市等级",
        f"城市等级分布数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "multi_lending": lambda data, ck="": generate_section_insight(
        "客群多头趋势",
        f"多头借贷数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "blacklist": lambda data, ck="": generate_section_insight(
        "客群黑灰名单分析",
        f"黑名单及风险勘测命中率数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "fraud": lambda data, ck="": generate_section_insight(
        "客群欺诈风险分析",
        f"团伙欺诈高风险占比数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "income": lambda data, ck="": generate_section_insight(
        "客群资质分析",
        f"融智分收入分布数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "credit_score": lambda data, ck="": generate_section_insight(
        "客群信用风险分析",
        f"融安云评分趋势数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
    "risk_correlation": lambda data, ck="": generate_section_insight(
        "风险联动分析",
        f"多头vs欺诈、收入vs黑名单关联数据: {json.dumps(data, ensure_ascii=False, default=str)}", cache_key=ck,
    ),
}
