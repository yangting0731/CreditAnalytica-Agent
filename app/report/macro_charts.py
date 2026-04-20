"""宏观经济数据图表"""
import plotly.graph_objects as go
import pandas as pd
from app.styles import PALETTE, DATA_COLORS, CHART_LAYOUT_DEFAULTS, chart_title


def _base_layout(title: str, **kwargs) -> dict:
    layout = dict(**CHART_LAYOUT_DEFAULTS)
    layout["title"] = chart_title(title)
    layout.update(kwargs)
    return layout


def chart_social_financing(df: pd.DataFrame) -> go.Figure:
    """社会融资规模增量趋势"""
    if df.empty or "message" in df.columns:
        return _empty("社会融资规模")
    date_col = df.columns[0]
    val_col = None
    for c in df.columns:
        if "社会融资" in c or "增量" in c:
            val_col = c
            break
    if val_col is None:
        val_col = df.columns[1]
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce")
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=recent[date_col], y=recent[val_col],
        marker_color=PALETTE["navy"], name="社融增量(亿元)",
        marker_line=dict(width=0),
    ))
    fig.update_layout(**_base_layout("社会融资规模增量（月度）", height=400))
    return fig


def chart_pmi(df: pd.DataFrame) -> go.Figure:
    """PMI趋势"""
    if df.empty or "message" in df.columns:
        return _empty("PMI指数")
    date_col = df.columns[0]
    val_col = None
    for c in df.columns:
        if "制造业" in c or "pmi" in c.lower():
            val_col = c
            break
    if val_col is None:
        val_col = df.columns[1]
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce")
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent[date_col], y=recent[val_col],
        mode="lines+markers", name="PMI",
        line=dict(color=PALETTE["navy"], width=2.5),
        marker=dict(size=6),
    ))
    fig.add_hline(y=50, line_dash="dash", line_color=PALETTE["coral"],
                  annotation_text="荣枯线(50)",
                  annotation_font=dict(color=PALETTE["coral"], size=12))
    fig.update_layout(**_base_layout("制造业PMI（月度）", height=400))
    return fig


def chart_money_supply(df: pd.DataFrame) -> go.Figure:
    """M2货币供应量趋势"""
    if df.empty or "message" in df.columns:
        return _empty("货币供应量")
    date_col = df.columns[0]
    m2_col = None
    for c in df.columns:
        if "M2" in c and ("同比" in c or "增长" in c):
            m2_col = c
            break
    if m2_col is None:
        for c in df.columns:
            if "M2" in c:
                m2_col = c
                break
    if m2_col is None:
        m2_col = df.columns[1]
    df = df.copy()
    df[m2_col] = pd.to_numeric(df[m2_col], errors="coerce")
    df = df.dropna(subset=[m2_col])
    df = df.sort_values(date_col).reset_index(drop=True)
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent[date_col], y=recent[m2_col],
        mode="lines+markers", name="M2同比增速",
        line=dict(color=PALETTE["teal"], width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(13,148,136,0.08)",
    ))
    fig.update_layout(**_base_layout("M2货币供应量增速", height=400,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_lpr(df: pd.DataFrame) -> go.Figure:
    """LPR利率趋势"""
    if df.empty or "message" in df.columns:
        return _empty("LPR利率")
    date_col = df.columns[0]
    fig = go.Figure()
    for i, col in enumerate(df.columns[1:4]):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        recent = df.tail(24)
        fig.add_trace(go.Scatter(
            x=recent[date_col], y=recent[col],
            mode="lines+markers", name=col,
            line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout("LPR贷款市场报价利率", height=400,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def _empty(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text="数据获取中...", xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(size=16, color=PALETTE["mist"]))
    fig.update_layout(**_base_layout(title, height=300))
    return fig


# ============================================================
# 新增数据图表
# ============================================================

def chart_cpi(df: pd.DataFrame) -> go.Figure:
    """CPI 通胀率趋势"""
    if df.empty or "message" in df.columns:
        return _empty("CPI 通胀率")
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent["日期"], y=recent["今值"],
        mode="lines+markers", name="CPI 同比(%)",
        line=dict(color=PALETTE["amber"], width=2.5),
        marker=dict(size=6),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=PALETTE["mist"],
                  annotation_text="0%",
                  annotation_font=dict(color=PALETTE["mist"], size=11))
    fig.update_layout(**_base_layout("CPI 居民消费价格指数（同比）", height=400,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_unemployment(df: pd.DataFrame) -> go.Figure:
    """城镇调查失业率趋势"""
    if df.empty or "message" in df.columns:
        return _empty("城镇调查失业率")
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent["date"], y=recent["value"],
        mode="lines+markers", name="失业率(%)",
        line=dict(color=PALETTE["coral"], width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.06)",
    ))
    fig.update_layout(**_base_layout("城镇调查失业率（月度）", height=400,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_house_price(df: pd.DataFrame) -> go.Figure:
    """70城房价指数趋势"""
    if df.empty or "message" in df.columns:
        return _empty("房价指数")
    recent = df.tail(24)
    fig = go.Figure()
    yoy_col = "新建商品住宅价格指数-同比"
    mom_col = "新建商品住宅价格指数-环比"
    if yoy_col in recent.columns:
        fig.add_trace(go.Scatter(
            x=recent["日期"], y=recent[yoy_col],
            mode="lines+markers", name="同比",
            line=dict(color=PALETTE["navy"], width=2.5),
            marker=dict(size=6),
        ))
    if mom_col in recent.columns:
        fig.add_trace(go.Scatter(
            x=recent["日期"], y=recent[mom_col],
            mode="lines+markers", name="环比",
            line=dict(color=PALETTE["teal"], width=2, dash="dot"),
            marker=dict(size=5),
        ))
    fig.add_hline(y=100, line_dash="dash", line_color=PALETTE["mist"],
                  annotation_text="持平线(100)",
                  annotation_font=dict(color=PALETTE["mist"], size=11))
    fig.update_layout(**_base_layout("70城新建商品住宅价格指数（均值）", height=400))
    return fig


def chart_retail_sales(df: pd.DataFrame) -> go.Figure:
    """社会消费品零售总额趋势"""
    if df.empty or "message" in df.columns:
        return _empty("社会消费品零售总额")
    recent = df.tail(24)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=recent["月份"], y=recent["当月"],
        marker_color=PALETTE["navy"], name="当月(亿元)",
        marker_line=dict(width=0), opacity=0.7,
    ))
    if "同比增长" in recent.columns:
        fig.add_trace(go.Scatter(
            x=recent["月份"], y=recent["同比增长"],
            mode="lines+markers", name="同比增长(%)",
            line=dict(color=PALETTE["amber"], width=2.5),
            marker=dict(size=6),
            yaxis="y2",
        ))
    fig.update_layout(**_base_layout("社会消费品零售总额（月度）", height=400,
                                     yaxis2=dict(
                                         overlaying="y", side="right",
                                         gridcolor="rgba(0,0,0,0)",
                                         ticksuffix="%",
                                         tickfont=dict(size=11, color=PALETTE["amber"]),
                                     ))
                      )
    return fig
