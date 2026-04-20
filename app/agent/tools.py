"""Agent 可调用的数据查询工具"""
import json
import pandas as pd
from app.data import analyzer


TOOLS_DEFINITION = [
    {
        "name": "query_gender_distribution",
        "description": "查询客群的性别分布数据，可指定机构类型筛选",
        "input_schema": {
            "type": "object",
            "properties": {
                "type_filter": {
                    "type": "string",
                    "description": "机构类型：全部/银行A/机构B/机构C",
                    "default": "全部"
                }
            }
        }
    },
    {
        "name": "query_age_distribution",
        "description": "查询客群的年龄段分布数据，可指定机构类型筛选",
        "input_schema": {
            "type": "object",
            "properties": {
                "type_filter": {"type": "string", "default": "全部"}
            }
        }
    },
    {
        "name": "query_city_tier_distribution",
        "description": "查询客群的城市等级分布数据",
        "input_schema": {
            "type": "object",
            "properties": {
                "type_filter": {"type": "string", "default": "全部"}
            }
        }
    },
    {
        "name": "query_multi_lending_trend",
        "description": "查询各机构的多头借贷趋势（银行/非银申请次数和机构数均值）",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_blacklist_trend",
        "description": "查询特殊名单（黑灰名单）命中率趋势",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_loan_risk_trend",
        "description": "查询借贷风险勘测命中率趋势",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_fraud_trend",
        "description": "查询团伙欺诈高风险占比趋势",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_income_distribution",
        "description": "查询融智分收入等级分布（客群资质分析）",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_credit_score_trend",
        "description": "查询融安云信用评分均值趋势",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_risk_correlation",
        "description": "查询风险联动分析：多头借贷vs欺诈率、收入等级vs黑名单命中率",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "query_risk_heatmap",
        "description": "查询年龄x城市等级的欺诈风险热力图数据",
        "input_schema": {"type": "object", "properties": {}}
    },
]

# OpenAI function calling 格式
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        }
    }
    for t in TOOLS_DEFINITION
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """执行工具并返回结果"""
    type_filter = tool_input.get("type_filter", "全部")

    handlers = {
        "query_gender_distribution": lambda: analyzer.gender_distribution(type_filter),
        "query_age_distribution": lambda: analyzer.age_distribution(type_filter),
        "query_city_tier_distribution": lambda: analyzer.city_tier_distribution(type_filter),
        "query_multi_lending_trend": lambda: analyzer.multi_lending_trend_by_type(),
        "query_blacklist_trend": lambda: analyzer.blacklist_hit_rate_trend(),
        "query_loan_risk_trend": lambda: analyzer.loan_risk_hit_rate_trend(),
        "query_fraud_trend": lambda: analyzer.fraud_high_risk_trend(),
        "query_income_distribution": lambda: analyzer.scorewis_distribution_by_type(),
        "query_credit_score_trend": lambda: analyzer.credit_score_trend(),
        "query_risk_correlation": lambda: _risk_correlation_result(),
        "query_risk_heatmap": lambda: analyzer.risk_heatmap_data(),
    }

    handler = handlers.get(tool_name)
    if handler is None:
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)

    result = handler()
    if isinstance(result, pd.DataFrame):
        return result.to_json(orient="records", force_ascii=False)
    elif isinstance(result, dict):
        return json.dumps({
            k: v.to_json(orient="records", force_ascii=False) if isinstance(v, pd.DataFrame) else v
            for k, v in result.items()
        }, ensure_ascii=False)
    return str(result)


def _risk_correlation_result():
    corr = analyzer.risk_correlation_analysis()
    if not corr:
        return pd.DataFrame()
    return corr


def get_chart_for_tool(tool_name: str, tool_input: dict):
    """根据工具名返回对应的图表"""
    from app.report import charts

    type_filter = tool_input.get("type_filter", "全部")

    if tool_name == "query_gender_distribution":
        data = analyzer.gender_distribution(type_filter)
        return charts.chart_gender_distribution(data)
    elif tool_name == "query_age_distribution":
        data = analyzer.age_distribution(type_filter)
        return charts.chart_age_distribution(data)
    elif tool_name == "query_city_tier_distribution":
        data = analyzer.city_tier_distribution(type_filter)
        return charts.chart_city_tier_distribution(data)
    elif tool_name == "query_multi_lending_trend":
        data = analyzer.multi_lending_trend_by_type()
        return charts.chart_multi_lending_trend(data, "bank_avg", "近12月银行申请次数均值")
    elif tool_name == "query_blacklist_trend":
        data = analyzer.blacklist_hit_rate_trend()
        return charts.chart_risk_trend(data, "hit_rate", "特殊名单命中率趋势")
    elif tool_name == "query_loan_risk_trend":
        data = analyzer.loan_risk_hit_rate_trend()
        return charts.chart_risk_trend(data, "hit_rate", "借贷风险勘测命中率趋势")
    elif tool_name == "query_fraud_trend":
        data = analyzer.fraud_high_risk_trend()
        return charts.chart_risk_trend(data, "high_risk_rate", "团伙欺诈高风险占比趋势")
    elif tool_name == "query_income_distribution":
        data = analyzer.scorewis_distribution_by_type()
        return charts.chart_income_distribution(data)
    elif tool_name == "query_credit_score_trend":
        data = analyzer.credit_score_trend()
        return charts.chart_credit_score_trend(data)
    elif tool_name == "query_risk_correlation":
        corr = analyzer.risk_correlation_analysis()
        if corr:
            return charts.chart_lending_vs_fraud(corr["lending_vs_fraud"])
        return None
    elif tool_name == "query_risk_heatmap":
        data = analyzer.risk_heatmap_data()
        return charts.chart_risk_heatmap(data)
    return None
