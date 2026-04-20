import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.styles import inject_css, render_insight
from app.data.geo_analyzer import (
    province_distribution, province_risk_profile,
    province_income_profile,
)
from app.report.map_charts import (
    map_province_heatmap, map_province_risk,
    map_province_income,
)
from app.report.insights import generate_section_insight, get_cached_insight
from app.config import ANTHROPIC_API_KEY, INSTITUTION_TYPES

st.set_page_config(page_title="地图分析", page_icon="🗺️", layout="wide")
inject_css()
st.title("🗺️ 客群地理分析")
st.caption("基于人口衍生数据的省份维度分析 | 点击标签页切换不同维度")

with st.sidebar:
    st.header("分析设置")
    type_filter = st.selectbox("机构类型", INSTITUTION_TYPES, index=0)
    ai_enabled = st.toggle("启用 AI 解读", value=True)

# AI 结论缓存
if "geo_insight_cache" not in st.session_state:
    st.session_state.geo_insight_cache = {}


def _get_insight(section: str, data_summary: str):
    if not ai_enabled:
        return ""
    session_key = f"geo_{type_filter}_{section}"
    cache_key = f"geo_{section}_{type_filter}"
    # 1. session 缓存
    if session_key in st.session_state.geo_insight_cache:
        return st.session_state.geo_insight_cache[session_key]
    # 2. 有 API key → 调 API 并写磁盘缓存
    if ANTHROPIC_API_KEY:
        result = generate_section_insight(section, data_summary, cache_key=cache_key)
        if result:
            st.session_state.geo_insight_cache[session_key] = result
            return result
    # 3. 没 API key → 读磁盘缓存
    cached = get_cached_insight(cache_key)
    if cached:
        st.session_state.geo_insight_cache[session_key] = cached
        return cached
    return ""


# ============================================================
# Tabs — 每次只渲染 1 张地图
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "客群地理分布", "各省风险画像", "收入资质分布", "综合分析"
])

# ------ Tab 1: 客群地理分布 ------
with tab1:
    st.subheader("客群地理分布热力图")
    dist_data = province_distribution(type_filter)
    if not dist_data.empty:
        fig_dist = map_province_heatmap(dist_data)
        st.plotly_chart(fig_dist, use_container_width=True)

        with st.expander("Top 10 省份明细"):
            top10 = dist_data.nlargest(10, "count")[["province", "count", "pct"]].reset_index(drop=True)
            top10.columns = ["省份", "客群数量", "占比(%)"]
            top10.index = top10.index + 1
            st.dataframe(top10, use_container_width=True)

        insight_dist = _get_insight(
            "客群地理分布",
            f"各省客群数量 Top10: {dist_data.nlargest(10, 'count')[['province', 'count', 'pct']].to_json(orient='records', force_ascii=False)}"
        )
        if insight_dist:
            render_insight(st, insight_dist, "地理分布分析")
    else:
        st.info("暂无省份数据")

# ------ Tab 2: 各省风险画像 ------
with tab2:
    st.subheader("各省风险对比地图")
    risk_data = province_risk_profile()
    if not risk_data.empty:
        fig_risk = map_province_risk(risk_data)
        st.plotly_chart(fig_risk, use_container_width=True)

        with st.expander("风险最高 Top 10 省份"):
            top10_risk = risk_data.nlargest(10, "risk_score")[
                ["province", "risk_score", "blacklist_rate", "fraud_rate", "total"]
            ].reset_index(drop=True)
            top10_risk.columns = ["省份", "综合风险分", "黑名单命中率(%)", "欺诈高风险率(%)", "样本量"]
            top10_risk.index = top10_risk.index + 1
            st.dataframe(top10_risk, use_container_width=True)

        insight_risk = _get_insight(
            "各省风险画像分析",
            f"各省风险指标 Top10: {risk_data.nlargest(10, 'risk_score')[['province', 'risk_score', 'blacklist_rate', 'fraud_rate', 'total']].to_json(orient='records', force_ascii=False)}"
        )
        if insight_risk:
            render_insight(st, insight_risk, "各省风险分析")
    else:
        st.info("风险数据不足（需至少 100 样本的省份）")

# ------ Tab 3: 收入资质分布 ------
with tab3:
    st.subheader("各省高收入客群占比")
    income_data = province_income_profile()
    if not income_data.empty:
        fig_income = map_province_income(income_data)
        st.plotly_chart(fig_income, use_container_width=True)

        with st.expander("高收入占比 Top 10 省份"):
            top10_income = income_data.nlargest(10, "high_income_rate")[
                ["province", "high_income_rate", "total"]
            ].reset_index(drop=True)
            top10_income.columns = ["省份", "高收入占比(%)", "样本量"]
            top10_income.index = top10_income.index + 1
            st.dataframe(top10_income, use_container_width=True)

        insight_income = _get_insight(
            "各省收入资质分布",
            f"各省高收入占比 Top10: {income_data.nlargest(10, 'high_income_rate')[['province', 'high_income_rate', 'total']].to_json(orient='records', force_ascii=False)}"
        )
        if insight_income:
            render_insight(st, insight_income, "收入资质分析")
    else:
        st.info("收入资质数据不足")

# ------ Tab 4: AI 综合分析 ------
_geo_comp_key = f"geo_综合分析_{type_filter}"
with tab4:
    st.subheader("地理维度综合分析")

    if ai_enabled:
        if ANTHROPIC_API_KEY:
            if st.button("🤖 生成地理维度综合分析", use_container_width=True):
                with st.spinner("AI 正在分析地理维度数据..."):
                    summary_parts = []
                    _dist = province_distribution(type_filter)
                    if not _dist.empty:
                        summary_parts.append(f"客群分布Top5: {_dist.nlargest(5, 'count')[['province', 'count', 'pct']].to_json(orient='records', force_ascii=False)}")
                    _risk = province_risk_profile()
                    if not _risk.empty:
                        summary_parts.append(f"风险Top5: {_risk.nlargest(5, 'risk_score')[['province', 'risk_score', 'blacklist_rate', 'fraud_rate']].to_json(orient='records', force_ascii=False)}")
                    _income = province_income_profile()
                    if not _income.empty:
                        summary_parts.append(f"高收入Top5: {_income.nlargest(5, 'high_income_rate')[['province', 'high_income_rate']].to_json(orient='records', force_ascii=False)}")

                    combined = "\n".join(summary_parts)
                    insight_geo = generate_section_insight(
                        "客群地理维度综合分析",
                        f"""请结合以下地理维度数据，从信贷风控角度做综合分析：
{combined}

请从以下角度分析：
1. 客群集中度：哪些省份是主要客群来源，是否过于集中
2. 地域风险差异：高风险省份特征，是否与经济发展水平相关
3. 收入地域分化：高收入客群的地域分布规律
4. 区域策略建议：基于以上分析的差异化区域策略""",
                        cache_key=_geo_comp_key,
                    )
                    if insight_geo:
                        render_insight(st, insight_geo, "地理维度综合分析")
        else:
            cached = get_cached_insight(_geo_comp_key)
            if cached:
                render_insight(st, cached, "地理维度综合分析")
            else:
                st.info("暂无缓存的 AI 分析结论")
    else:
        st.info("启用 AI 解读后可自动生成地理维度综合分析")
