"""地图图表模块 — 中国省份地图可视化"""
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from pathlib import Path
from app.styles import PALETTE

# GeoJSON 缓存路径
_GEOJSON_CACHE = Path(__file__).parent.parent.parent / "培训_数据源" / "宏观数据缓存" / "china_provinces.json"

_MAP_CENTER = {"lat": 35.8, "lon": 104.1}
_MAP_ZOOM = 2.8


@st.cache_data(ttl=86400)
def _load_china_geojson() -> dict:
    """加载中国省份 GeoJSON（优先本地缓存）"""
    if _GEOJSON_CACHE.exists():
        with open(_GEOJSON_CACHE, "r") as f:
            return json.load(f)
    import requests
    r = requests.get("https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json", timeout=15)
    geo = r.json()
    with open(_GEOJSON_CACHE, "w") as f:
        json.dump(geo, f)
    return geo


def _map_layout() -> dict:
    return dict(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        font=dict(
            family="'PingFang SC', 'Microsoft YaHei', sans-serif",
            size=12, color=PALETTE["slate"],
        ),
        paper_bgcolor="white",
    )


def map_province_heatmap(df: pd.DataFrame) -> go.Figure:
    """省份客群分布热力图"""
    geojson = _load_china_geojson()
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="province_full",
        featureidkey="properties.name",
        color="count",
        color_continuous_scale=[
            [0, "#F1F5F9"],
            [0.3, "#93C5FD"],
            [0.6, "#3B82F6"],
            [1, PALETTE["navy"]],
        ],
        hover_name="province",
        hover_data={"count": ":,", "pct": ":.1f", "province_full": False},
        labels={"count": "客群数量", "pct": "占比(%)"},
        mapbox_style="white-bg",
        center=_MAP_CENTER,
        zoom=_MAP_ZOOM,
        opacity=0.85,
        title="客群地理分布",
    )
    fig.update_layout(**_map_layout(), height=550)
    fig.update_coloraxes(colorbar=dict(
        title="客群数", tickfont=dict(size=11),
        len=0.6, thickness=15,
    ))
    return fig


def map_province_risk(df: pd.DataFrame) -> go.Figure:
    """各省风险对比地图"""
    geojson = _load_china_geojson()
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="province_full",
        featureidkey="properties.name",
        color="risk_score",
        color_continuous_scale=[
            [0, PALETTE["sage"]],
            [0.4, "#FCD34D"],
            [0.7, PALETTE["amber"]],
            [1, PALETTE["coral"]],
        ],
        hover_name="province",
        hover_data={
            "blacklist_rate": ":.2f",
            "fraud_rate": ":.2f",
            "risk_score": ":.2f",
            "total": ":,",
            "province_full": False,
        },
        labels={
            "blacklist_rate": "黑名单命中率(%)",
            "fraud_rate": "欺诈高风险率(%)",
            "risk_score": "综合风险分",
            "total": "样本量",
        },
        mapbox_style="white-bg",
        center=_MAP_CENTER,
        zoom=_MAP_ZOOM,
        opacity=0.85,
        title="各省风险画像",
    )
    fig.update_layout(**_map_layout(), height=550)
    fig.update_coloraxes(colorbar=dict(
        title="风险分", tickfont=dict(size=11),
        len=0.6, thickness=15,
    ))
    return fig


def map_province_income(df: pd.DataFrame) -> go.Figure:
    """各省收入资质分布地图"""
    geojson = _load_china_geojson()
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="province_full",
        featureidkey="properties.name",
        color="high_income_rate",
        color_continuous_scale=[
            [0, "#FEE2E2"],
            [0.3, "#FCD34D"],
            [0.6, PALETTE["teal"]],
            [1, PALETTE["navy"]],
        ],
        hover_name="province",
        hover_data={
            "high_income_rate": ":.1f",
            "total": ":,",
            "province_full": False,
        },
        labels={
            "high_income_rate": "高收入占比(%)",
            "total": "样本量",
        },
        mapbox_style="white-bg",
        center=_MAP_CENTER,
        zoom=_MAP_ZOOM,
        opacity=0.85,
        title="各省高收入客群占比",
    )
    fig.update_layout(**_map_layout(), height=550)
    fig.update_coloraxes(colorbar=dict(
        title="高收入%", tickfont=dict(size=11),
        len=0.6, thickness=15,
    ))
    return fig


def map_migration_flow(df: pd.DataFrame) -> go.Figure:
    """客群迁移流向图"""
    fig = go.Figure()

    max_count = df["count"].max() if not df.empty else 1

    # 画流向线
    for _, row in df.iterrows():
        width = max(1, row["count"] / max_count * 6)
        opacity = min(0.8, 0.3 + row["count"] / max_count * 0.5)
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[row["from_lon"], row["to_lon"]],
            lat=[row["from_lat"], row["to_lat"]],
            line=dict(width=width, color=f"rgba(220,38,38,{opacity})"),
            hoverinfo="text",
            text=f"{row['from_city']} → {row['to_city']}: {row['count']}人",
            showlegend=False,
        ))

    # 画目的地城市点
    dest_cities = df.groupby("to_city").agg(
        total=("count", "sum"),
        lat=("to_lat", "first"),
        lon=("to_lon", "first"),
    ).reset_index()

    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=dest_cities["lon"],
        lat=dest_cities["lat"],
        marker=dict(
            size=dest_cities["total"] / dest_cities["total"].max() * 20 + 5,
            color=PALETTE["navy"],
            opacity=0.8,
        ),
        text=dest_cities["to_city"],
        textposition="top center",
        textfont=dict(size=10, color=PALETTE["ink"]),
        hoverinfo="text",
        hovertext=dest_cities.apply(lambda r: f"{r['to_city']}: 流入 {r['total']}人", axis=1),
        name="流入城市",
    ))

    fig.update_layout(
        **_map_layout(),
        height=550,
        title=dict(text="客群迁移流向（户籍地 → 现居地）", font=dict(size=15, color=PALETTE["ink"])),
        mapbox=dict(
            style="white-bg",
            center=_MAP_CENTER,
            zoom=_MAP_ZOOM,
        ),
        showlegend=False,
    )
    return fig
