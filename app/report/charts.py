"""图表生成模块 — 使用 Plotly 生成所有分析图表"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.styles import PALETTE, DATA_COLORS, CHART_LAYOUT_DEFAULTS, chart_title, INCOME_COLORS, RISK_COLORS


def _base_layout(title: str, **kwargs) -> dict:
    """统一的图表样式 — 基于设计系统"""
    layout = dict(**CHART_LAYOUT_DEFAULTS)
    layout["title"] = chart_title(title)
    layout.update(kwargs)
    return layout


# ============================================================
# 基础画像图表
# ============================================================

def chart_gender_distribution(df: pd.DataFrame) -> go.Figure:
    """性别分布 — 堆叠条形图"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["group"], x=df["男"], name="男",
        orientation="h", marker_color=PALETTE["navy"],
        text=df["男"].apply(lambda x: f"{x:.1f}%"), textposition="inside",
        textfont=dict(color="#FFFFFF", size=12),
    ))
    fig.add_trace(go.Bar(
        y=df["group"], x=df["女"], name="女",
        orientation="h", marker_color=PALETTE["amber"],
        text=df["女"].apply(lambda x: f"{x:.1f}%"), textposition="inside",
        textfont=dict(color="#FFFFFF", size=12),
    ))
    fig.update_layout(**_base_layout("性别分布", barmode="stack",
                                     xaxis=dict(showgrid=False, showticklabels=False,
                                                linecolor="rgba(0,0,0,0)"),
                                     height=250))
    return fig


def chart_age_distribution(df: pd.DataFrame) -> go.Figure:
    """年龄分布 — 堆叠条形图"""
    age_cols = [c for c in df.columns if c != "group"]
    fig = go.Figure()
    for i, col in enumerate(age_cols):
        fig.add_trace(go.Bar(
            y=df["group"], x=df[col], name=col,
            orientation="h", marker_color=DATA_COLORS[i % len(DATA_COLORS)],
            text=df[col].apply(lambda x: f"{x:.1f}%"), textposition="inside",
            textfont=dict(color="#FFFFFF", size=11),
        ))
    fig.update_layout(**_base_layout("年龄分布", barmode="stack",
                                     xaxis=dict(showgrid=False, showticklabels=False,
                                                linecolor="rgba(0,0,0,0)"),
                                     height=250))
    return fig


def chart_city_tier_distribution(df: pd.DataFrame) -> go.Figure:
    """城市等级分布 — 堆叠条形图"""
    tier_cols = [c for c in df.columns if c != "group"]
    fig = go.Figure()
    for i, col in enumerate(tier_cols):
        fig.add_trace(go.Bar(
            y=df["group"], x=df[col], name=col,
            orientation="h", marker_color=DATA_COLORS[i % len(DATA_COLORS)],
            text=df[col].apply(lambda x: f"{x:.1f}%"), textposition="inside",
            textfont=dict(color="#FFFFFF", size=11),
        ))
    fig.update_layout(**_base_layout("城市等级分布", barmode="stack",
                                     xaxis=dict(showgrid=False, showticklabels=False,
                                                linecolor="rgba(0,0,0,0)"),
                                     height=250))
    return fig


def chart_trend_by_gender(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    """性别趋势折线图"""
    if df.empty:
        return _empty_chart(title)
    fig = go.Figure()
    for gender, color, dash in [("男", PALETTE["navy"], "solid"), ("女", PALETTE["amber"], "dot")]:
        sub = df[df["gender"] == gender]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub[metric], name=gender,
            mode="lines+markers", line=dict(color=color, dash=dash, width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout(title, height=350))
    return fig


def chart_trend_by_age(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    """年龄段趋势折线图"""
    if df.empty:
        return _empty_chart(title)
    fig = go.Figure()
    for i, age in enumerate(df["age_group"].unique()):
        sub = df[df["age_group"] == age]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub[metric], name=str(age),
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout(title, height=350))
    return fig


def chart_trend_by_city_tier(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    """城市等级趋势折线图"""
    if df.empty:
        return _empty_chart(title)
    fig = go.Figure()
    for i, tier in enumerate(df["city_tier"].unique()):
        sub = df[df["city_tier"] == tier]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub[metric], name=tier,
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout(title, height=350))
    return fig


# ============================================================
# 多头借贷图表
# ============================================================

def chart_multi_lending_trend(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    """多头借贷趋势 — 各机构类型折线图"""
    if df.empty:
        return _empty_chart(title)
    fig = go.Figure()
    for i, t in enumerate(df["type"].unique()):
        sub = df[df["type"] == t]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub[metric], name=t,
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout(title, height=350))
    return fig


# ============================================================
# 风险分析图表
# ============================================================

def chart_risk_trend(df: pd.DataFrame, rate_col: str, title: str) -> go.Figure:
    """风险趋势折线图 — 各机构类型"""
    if df.empty:
        return _empty_chart(title)
    fig = go.Figure()
    for i, t in enumerate(df["type"].unique()):
        sub = df[df["type"] == t]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub[rate_col], name=t,
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout(title, height=350,
                                     yaxis=dict(gridcolor=PALETTE["grid"],
                                                linecolor="rgba(0,0,0,0)",
                                                ticksuffix="%")))
    return fig


# ============================================================
# 价值分析图表
# ============================================================

def chart_income_distribution(df: pd.DataFrame) -> go.Figure:
    """融智分收入等级分布 — 堆叠条形图"""
    income_cols = [c for c in df.columns if c != "group"]
    fig = go.Figure()
    for col in income_cols:
        color = INCOME_COLORS.get(col, PALETTE["mist"])
        fig.add_trace(go.Bar(
            y=df["group"], x=df[col], name=col,
            orientation="h", marker_color=color,
            text=df[col].apply(lambda x: f"{x:.1f}%"), textposition="inside",
            textfont=dict(color="#FFFFFF", size=11),
        ))
    fig.update_layout(**_base_layout("融智分整体收入分布对比", barmode="stack",
                                     xaxis=dict(showgrid=False, showticklabels=False,
                                                linecolor="rgba(0,0,0,0)"),
                                     height=250))
    return fig


def chart_high_income_trend(df: pd.DataFrame) -> go.Figure:
    """高收入人群占比趋势"""
    if df.empty:
        return _empty_chart("高收入人群占比趋势")
    fig = go.Figure()
    for i, t in enumerate(df["type"].unique()):
        sub = df[df["type"] == t]
        fig.add_trace(go.Scatter(
            x=sub["year_month"], y=sub["high_income_rate"], name=t,
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout("高收入人群占比趋势", height=350,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_credit_score_trend(df: pd.DataFrame) -> go.Figure:
    """融安云评分均值趋势"""
    if df.empty:
        return _empty_chart("融安云均值趋势")
    fig = go.Figure()
    for i, t in enumerate(df["type"].unique()):
        sub = df[df["type"] == t]
        fig.add_trace(go.Scatter(
            x=sub["quarter"], y=sub["avg_score"], name=t,
            mode="lines+markers", line=dict(color=DATA_COLORS[i % len(DATA_COLORS)], width=2.5),
            marker=dict(size=6),
        ))
    fig.update_layout(**_base_layout("融安云均值趋势", height=350))
    return fig


# ============================================================
# 扩展分析图表
# ============================================================

def chart_lending_vs_fraud(df: pd.DataFrame) -> go.Figure:
    """多头借贷分组 vs 欺诈率 — 柱状图"""
    if df.empty:
        return _empty_chart("多头借贷 vs 欺诈风险")
    fig = go.Figure()
    n = len(df)
    colors = RISK_COLORS[:n] if n <= len(RISK_COLORS) else [DATA_COLORS[i % len(DATA_COLORS)] for i in range(n)]
    fig.add_trace(go.Bar(
        x=df["lending_group"], y=df["fraud_rate"],
        marker_color=colors,
        text=df["fraud_rate"].apply(lambda x: f"{x:.1f}%"), textposition="outside",
        textfont=dict(size=12, color=PALETTE["slate"]),
    ))
    fig.update_layout(**_base_layout("多头借贷程度 vs 团伙欺诈高风险率", height=350,
                                     showlegend=False,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_income_vs_blacklist(df: pd.DataFrame) -> go.Figure:
    """收入等级 vs 黑名单命中率 — 柱状图"""
    if df.empty:
        return _empty_chart("收入等级 vs 黑名单命中率")
    fig = go.Figure()
    n = len(df)
    colors = list(reversed(RISK_COLORS[:n])) if n <= len(RISK_COLORS) else [DATA_COLORS[i % len(DATA_COLORS)] for i in range(n)]
    fig.add_trace(go.Bar(
        x=df["income_group"], y=df["blacklist_rate"],
        marker_color=colors,
        text=df["blacklist_rate"].apply(lambda x: f"{x:.1f}%"), textposition="outside",
        textfont=dict(size=12, color=PALETTE["slate"]),
    ))
    fig.update_layout(**_base_layout("收入等级 vs 特殊名单命中率", height=350,
                                     showlegend=False,
                                     yaxis=dict(gridcolor=PALETTE["grid"], ticksuffix="%")))
    return fig


def chart_risk_heatmap(df: pd.DataFrame) -> go.Figure:
    """年龄 x 城市等级 欺诈风险热力图"""
    if df.empty:
        return _empty_chart("风险热力图")
    pivot = df.pivot_table(values="fraud_rate", index="age_group", columns="city_tier", aggfunc="mean")
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0, PALETTE["sage"]],
            [0.33, "#FCD34D"],
            [0.66, PALETTE["amber"]],
            [1, PALETTE["coral"]],
        ],
        text=pivot.values.round(1),
        texttemplate="%{text}%",
        textfont=dict(size=12, color=PALETTE["ink"]),
        colorbar=dict(
            title=dict(text="欺诈率%", font=dict(size=12, color=PALETTE["slate"])),
            tickfont=dict(size=11, color=PALETTE["mist"]),
        ),
    ))
    fig.update_layout(**_base_layout("年龄 x 城市等级 团伙欺诈高风险率", height=400))
    return fig


# ============================================================
# Utility
# ============================================================

def _empty_chart(title: str) -> go.Figure:
    """空数据占位图表"""
    fig = go.Figure()
    fig.add_annotation(text="暂无数据", xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(size=16, color=PALETTE["mist"]))
    fig.update_layout(**_base_layout(title, height=300))
    return fig
