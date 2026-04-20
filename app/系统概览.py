import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.styles import inject_css

st.set_page_config(
    page_title="系统概览",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
st.title("🦞 百融智能分析 Agent")
st.markdown("### 信贷场景客群智能分析系统")

st.markdown("""
---

欢迎使用百融智能分析 Agent！本系统基于百融数据产品，提供以下核心功能：

#### 📊 客群洞察报告
一键生成完整的客群分析报告，包含：
- **客群基础画像** — 性别、年龄、城市等级分布及趋势
- **风险分析** — 黑灰名单、多头借贷、团伙欺诈风险
- **价值分析** — 收入资质、信用评分
- **风险联动分析** — 多维度交叉分析，发现隐藏风险
- **地理分布分析** — 省份维度客群分布、风险、收入热力图
- **AI 策略建议** — 自动生成客群评估和准入策略建议
- **PPT 导出** — 一键下载分析报告

#### 💬 智能问答
用自然语言提问，AI 自动查询数据、生成图表、给出分析：
- "客群的男女比例是多少？"
- "多头借贷严重的客群，欺诈风险是否更高？"
- "帮我分析一下客群的整体风险状况"

---

**👈 从左侧导航选择功能开始使用**
""")

# Data overview
st.markdown("#### 数据概览")
col1, col2, col3, col4 = st.columns(4)
col1.metric("数据产品", "7 个")
col2.metric("样本量", "325,510 条")
col3.metric("机构类型", "3 种")
col4.metric("时间跨度", "2024.01 - 2025.02")

st.markdown("""
| 数据产品 | 说明 |
|---------|------|
| 人口衍生 | 性别、年龄、城市等级等基础画像 |
| 借贷意向验证 | 多头借贷行为（银行/非银申请次数、机构数） |
| 借贷风险勘测 | 高风险机构借贷行为 |
| 特殊名单验证 | 法院失信、银行不良、逾期等黑灰名单 |
| 团伙欺诈排查 | 欺诈团伙风险等级和规模 |
| 融智分 | 收入/资质等级评估（1-15） |
| 融安云评分 | 信用风险评分（300-1000） |
""")

