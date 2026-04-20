import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.styles import inject_css
from app.agent.chat import chat_with_agent

st.set_page_config(page_title="智能问答", page_icon="💬", layout="wide")
inject_css()
st.title("💬 智能问答 — 小龙虾")
st.caption("你可以用自然语言提问，我会自动查询数据并给出分析")

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_charts" not in st.session_state:
    st.session_state.chat_charts = {}

# Suggested questions
with st.expander("💡 试试这些问题", expanded=not st.session_state.chat_messages):
    suggestions = [
        "客群的男女比例是多少？",
        "哪个年龄段的客群最多？",
        "各机构类型的黑名单命中率趋势如何？",
        "多头借贷严重的客群，欺诈风险是否更高？",
        "银行A的客群信用评分趋势怎么样？",
        "不同城市等级的客群分布如何？",
        "帮我分析一下客群的整体风险状况",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = s
                st.rerun()

# Display chat history
for i, msg in enumerate(st.session_state.chat_messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i in st.session_state.chat_charts:
            st.plotly_chart(st.session_state.chat_charts[i], use_container_width=True)

# Handle pending question from suggestions
pending = st.session_state.pop("pending_question", None)

# Chat input
user_input = st.chat_input("请输入你的问题...")
question = pending or user_input

if question:
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("小龙虾正在分析..."):
            # Build messages for API (only role + content text)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_messages
            ]
            response_text, chart_fig = chat_with_agent(api_messages)

        st.markdown(response_text)
        if chart_fig is not None:
            st.plotly_chart(chart_fig, use_container_width=True)
            st.session_state.chat_charts[len(st.session_state.chat_messages)] = chart_fig

    st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
