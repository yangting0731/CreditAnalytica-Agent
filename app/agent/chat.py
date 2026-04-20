"""对话 Agent 核心逻辑 — 使用 OpenAI 兼容接口 function calling"""
import json
from openai import OpenAI
from app.config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_MODEL
from app.agent.tools import TOOLS_DEFINITION, OPENAI_TOOLS, execute_tool, get_chart_for_tool


SYSTEM_PROMPT = """你是"小龙虾"，一个专业的信贷风控数据分析 Agent。你可以帮助用户查询和分析信贷客群数据。

你有以下数据分析工具可用：
- 客群画像：性别分布、年龄分布、城市等级分布
- 多头借贷：银行/非银申请次数和机构数趋势
- 风险分析：黑灰名单命中率、借贷风险勘测命中率、团伙欺诈风险
- 价值分析：融智分收入等级、融安云信用评分
- 风险联动：多头vs欺诈、收入vs黑名单的关联分析
- 风险热力图：年龄x城市等级的欺诈风险分布

数据涵盖 3 种机构类型：银行A、机构B、机构C。

回复要求：
1. 先调用相关工具获取数据
2. 基于数据给出专业、有洞察的分析
3. 用中文回复
4. 引用具体数字
5. 如果用户的问题不够明确，主动推荐可以分析的方向"""


def chat_with_agent(messages: list) -> tuple:
    """
    与 Agent 对话

    Args:
        messages: 对话历史 [{"role": "user"/"assistant", "content": "..."}]

    Returns:
        tuple: (response_text, chart_fig_or_none)
    """
    if not ANTHROPIC_API_KEY:
        return "请先配置 API_KEY（在 .env 文件中设置）", None

    client = OpenAI(api_key=ANTHROPIC_API_KEY, base_url=f"{ANTHROPIC_BASE_URL}/v1")

    # 只传纯文本历史
    clean_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        if isinstance(m.get("content"), str):
            clean_messages.append({"role": m["role"], "content": m["content"]})

    response = client.chat.completions.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=clean_messages,
        tools=OPENAI_TOOLS,
    )

    # Process tool calls
    chart_fig = None
    loop_messages = list(clean_messages)
    choice = response.choices[0]

    while choice.finish_reason == "tool_calls" and choice.message.tool_calls:
        tool_call = choice.message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_input = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

        # Execute tool
        tool_result = execute_tool(tool_name, tool_input)

        # Get chart
        chart_fig = get_chart_for_tool(tool_name, tool_input)

        # Continue conversation with tool result
        loop_messages.append(choice.message)
        loop_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result,
        })

        response = client.chat.completions.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=loop_messages,
            tools=OPENAI_TOOLS,
        )
        choice = response.choices[0]

    response_text = choice.message.content or ""
    return response_text, chart_fig
