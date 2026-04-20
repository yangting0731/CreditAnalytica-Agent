"""全局样式 — 信贷分析仪表盘设计系统

设计理念：「精准洞察」
- 金融信贷领域 → 信任感、精确感、专业度
- 色彩世界：深海蓝黑为底，琥珀金为点睛，冷灰做结构
- 避免：过饱和色、紫色渐变、圆角卡片堆砌等 AI 默认风格
"""

# ============================================================
# Design Tokens — 信贷分析仪表盘
# ============================================================

# 主色板：从金融/信贷物理世界提取
PALETTE = {
    # 基础
    "ink": "#0B1426",           # 深墨蓝 — 主文字
    "slate": "#334155",         # 板岩灰 — 次级文字
    "mist": "#94A3B8",          # 雾灰 — 辅助文字
    "cloud": "#F1F5F9",         # 云白 — 背景面
    "paper": "#FFFFFF",         # 纸白 — 卡片

    # 数据色 — 机构对比用（保证色盲友好）
    "navy": "#1E3A5F",          # 藏蓝 — 主机构
    "teal": "#0D9488",          # 青碧 — 对比机构1
    "amber": "#D97706",         # 琥珀 — 对比机构2
    "coral": "#DC2626",         # 珊瑚红 — 风险/警示
    "sage": "#059669",          # 鼠尾草绿 — 安全/通过

    # 语义色
    "risk_low": "#059669",      # 低风险
    "risk_mid": "#D97706",      # 中风险
    "risk_high": "#DC2626",     # 高风险
    "risk_extreme": "#7C2D12",  # 极高风险

    # 图表网格和边框
    "grid": "rgba(148,163,184,0.12)",    # 极淡网格线
    "border": "rgba(148,163,184,0.2)",   # 边框
}

# 数据系列配色（6色，依次使用）
DATA_COLORS = [
    "#1E3A5F",  # 藏蓝
    "#D97706",  # 琥珀
    "#6B7280",  # 石灰
    "#DC2626",  # 珊瑚红
    "#0D9488",  # 青碧
    "#7C3AED",  # 紫罗兰（仅在需要第6色时）
]

# 风险梯度色（从安全到危险）
RISK_COLORS = ["#059669", "#D97706", "#EA580C", "#DC2626"]

# 收入等级色
INCOME_COLORS = {
    "低收入": "#DC2626",
    "中低收入": "#D97706",
    "中高收入": "#0D9488",
    "高收入": "#1E3A5F",
    "未命中": "#CBD5E1",
}


# ============================================================
# Plotly 图表全局配置
# ============================================================

CHART_FONT = dict(
    family="'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif",
    size=13,
    color=PALETTE["slate"],
)

CHART_LAYOUT_DEFAULTS = dict(
    font=CHART_FONT,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=48, r=24, t=48, b=48),
    hoverlabel=dict(
        bgcolor=PALETTE["ink"],
        font_size=13,
        font_color="#FFFFFF",
        bordercolor="rgba(0,0,0,0)",
    ),
    legend=dict(
        orientation="h",
        yanchor="top", y=-0.18,
        xanchor="center", x=0.5,
        font=dict(size=12, color=PALETTE["mist"]),
        itemsizing="constant",
        tracegroupgap=16,
    ),
    xaxis=dict(
        showgrid=False,
        linecolor=PALETTE["border"],
        linewidth=1,
        tickfont=dict(size=11, color=PALETTE["mist"]),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor=PALETTE["grid"],
        gridwidth=1,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(size=11, color=PALETTE["mist"]),
        zeroline=False,
    ),
)


def chart_title(text: str) -> dict:
    """标准图表标题"""
    return dict(
        text=text,
        font=dict(size=15, color=PALETTE["ink"], family=CHART_FONT["family"]),
        x=0, xanchor="left",
        y=0.98, yanchor="top",
    )


# ============================================================
# Streamlit 自定义 CSS
# ============================================================

CUSTOM_CSS = """
<style>
/* ---- 全局排版 ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    font-family: 'PingFang SC', 'Microsoft YaHei', Inter, -apple-system, sans-serif;
}

/* ---- 页面标题 ---- */
.stApp h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #0B1426 !important;
    letter-spacing: -0.02em;
    padding-bottom: 0.25rem;
    border-bottom: 3px solid #1E3A5F;
    display: inline-block;
}

/* ---- 区块标题 ---- */
.stApp h2 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #1E3A5F !important;
    margin-top: 2rem !important;
    padding-left: 12px;
    border-left: 4px solid #D97706;
}

.stApp h3 {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
}

/* ---- 指标卡片 ---- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 8px;
    padding: 16px 20px;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #1E3A5F !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ---- Blockquote (AI 分析结论) ---- */
.stApp blockquote {
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%) !important;
    border-left: 4px solid #D97706 !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 16px 20px !important;
    margin: 12px 0 !important;
    color: #78350F !important;
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
}

/* ---- 按钮 ---- */
.stApp button[kind="primary"] {
    background: #1E3A5F !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
}

.stApp button[kind="primary"]:hover {
    background: #0B1426 !important;
}

/* ---- 侧边栏 ---- */
[data-testid="stSidebar"] {
    background: #0B1426 !important;
}

[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    border: none !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #94A3B8 !important;
}

/* ---- 分割线 ---- */
hr {
    border: none !important;
    border-top: 1px solid rgba(148,163,184,0.15) !important;
    margin: 2rem 0 !important;
}

/* ---- 表格 ---- */
.stApp table {
    font-size: 0.88rem !important;
}

.stApp thead th {
    background: #F1F5F9 !important;
    color: #334155 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.78rem !important;
    letter-spacing: 0.04em;
}

/* ---- Plotly 图表容器 ---- */
[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 8px;
    padding: 8px;
    background: #FFFFFF;
}

/* ---- Expander ---- */
.streamlit-expanderHeader {
    font-size: 0.88rem !important;
    color: #64748B !important;
}

/* ---- AI 分析结论卡片 ---- */
.ai-insight-box {
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF9EE 100%);
    border: 1px solid rgba(217,119,6,0.2);
    border-left: 4px solid #D97706;
    border-radius: 0 10px 10px 0;
    padding: 20px 24px 16px 24px;
    margin: 16px 0 20px 0;
}

.ai-insight-box .ai-insight-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(217,119,6,0.15);
}

.ai-insight-box .ai-insight-header span.ai-icon {
    font-size: 1rem;
}

.ai-insight-box .ai-insight-header span.ai-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #92400E;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.ai-insight-box .ai-insight-header span.ai-model {
    font-size: 0.72rem;
    font-weight: 500;
    color: #B45309;
    text-transform: none;
    letter-spacing: 0;
    opacity: 0.75;
}

.ai-insight-box .ai-insight-body {
    font-size: 0.82rem !important;
    line-height: 1.8;
    color: #78350F;
}

.ai-insight-box .ai-insight-body p {
    font-size: 0.82rem !important;
    margin-bottom: 4px;
}

.ai-insight-box .ai-insight-body strong {
    color: #92400E;
}

.ai-insight-box .ai-insight-body ul, .ai-insight-box .ai-insight-body ol {
    padding-left: 16px;
    margin: 4px 0;
}

.ai-insight-box .ai-insight-body li {
    font-size: 0.82rem !important;
    margin-bottom: 6px;
}

/* ---- 隐藏侧边栏 View more/less 按钮 ---- */
[data-testid="stSidebarNav"] button,
[data-testid="stSidebarNav"] [data-testid="collapsedControl"] {
    display: none !important;
}

/* ---- Chat ---- */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
}
</style>
"""


def inject_css():
    """在页面顶部注入自定义CSS"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_insight(st_module, text: str, title: str = "AI 分析结论"):
    """在好看的卡片框中渲染 AI 分析结论"""
    from app.config import CLAUDE_MODEL
    import markdown as _md_lib
    try:
        html_body = _md_lib.markdown(text)
    except Exception:
        # fallback: 简单换行处理
        html_body = text.replace("\n", "<br>")
    model_tag = f' · <span class="ai-model">{CLAUDE_MODEL}</span>' if CLAUDE_MODEL else ""
    st_module.markdown(f"""
<div class="ai-insight-box">
  <div class="ai-insight-header">
    <span class="ai-icon">🤖</span>
    <span class="ai-title">{title}{model_tag}</span>
  </div>
  <div class="ai-insight-body">{html_body}</div>
</div>
""", unsafe_allow_html=True)


def show_model_badge(st_module):
    """在侧边栏底部显示当前 AI 模型名"""
    from app.config import CLAUDE_MODEL, ANTHROPIC_API_KEY
    with st_module.sidebar:
        st_module.divider()
        if ANTHROPIC_API_KEY:
            st_module.caption(f"🤖 当前模型：**{CLAUDE_MODEL}**")
        else:
            st_module.caption("🤖 AI 模型：未配置（使用缓存结论）")
