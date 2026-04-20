import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.styles import inject_css, render_insight
from app.data.macro_crawler import (
    fetch_social_financing, fetch_pmi, fetch_money_supply,
    fetch_lpr, fetch_npl_ratio, get_macro_summary, refresh_all_data,
    fetch_cpi, fetch_unemployment, fetch_house_price, fetch_retail_sales,
)
from app.report.macro_charts import (
    chart_social_financing, chart_pmi, chart_money_supply, chart_lpr,
    chart_cpi, chart_unemployment, chart_house_price, chart_retail_sales,
)
from app.report.insights import generate_section_insight, get_cached_insight
from app.config import ANTHROPIC_API_KEY
import json

st.set_page_config(page_title="宏观环境", page_icon="🌐", layout="wide")
inject_css()
st.title("🌐 宏观经济环境")
st.caption("数据来源：AKShare（央行/统计局公开数据）| 默认展示缓存数据，点击刷新获取最新")

with st.sidebar:
    ai_enabled = st.toggle("启用 AI 解读", value=True)
    st.divider()
    if st.button("🔄 刷新全部数据", type="primary", use_container_width=True):
        with st.spinner("正在从 AKShare 拉取最新数据（约30秒）..."):
            results = refresh_all_data()
        ok_count = sum(1 for v in results.values() if v == "ok")
        st.success(f"刷新完成：{ok_count}/{len(results)} 个数据源更新成功")
        for name, status in results.items():
            if status != "ok":
                st.warning(f"{name}: {status}")
        st.rerun()


def _render_section(title: str, fetch_fn, chart_fn, insight_topic: str, insight_data_fn=None):
    """通用 section 渲染：读缓存 → 画图 → AI 解读"""
    st.header(title)
    try:
        df = fetch_fn()  # 默认 force=False，只读缓存
        if df is None or df.empty:
            st.info("暂无缓存数据，请点击左侧「刷新全部数据」获取")
            return
        if "message" in df.columns:
            st.warning(f"{insight_topic}数据暂不可用")
            return
        fig = chart_fn(df)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("查看原始数据"):
            st.dataframe(df.tail(12), use_container_width=True)
        if ai_enabled:
            cache_key = f"macro_{insight_topic}"
            if ANTHROPIC_API_KEY:
                data_str = insight_data_fn(df) if insight_data_fn else df.tail(6).to_json(orient="records", force_ascii=False)
                insight = generate_section_insight(insight_topic, f"最近数据: {data_str}", cache_key=cache_key)
            else:
                insight = get_cached_insight(cache_key)
            if insight:
                render_insight(st, insight, f"{insight_topic}解读")
    except Exception as e:
        st.error(f"加载失败: {e}")


# ============================================================
# 各 Section
# ============================================================

_render_section("一、社会融资规模", fetch_social_financing, chart_social_financing, "社会融资规模")
st.divider()

_render_section("二、制造业PMI", fetch_pmi, chart_pmi, "制造业PMI")
st.divider()

_render_section("三、M2货币供应量", fetch_money_supply, chart_money_supply, "M2货币供应")
st.divider()

_render_section("四、LPR贷款市场报价利率", fetch_lpr, chart_lpr, "LPR利率")
st.divider()

_render_section("五、CPI 居民消费价格指数", fetch_cpi, chart_cpi, "CPI通胀率对信贷的影响")
st.divider()

_render_section("六、城镇调查失业率", fetch_unemployment, chart_unemployment, "城镇失业率对信贷风险的影响")
st.divider()

_render_section("七、70城新建商品住宅价格指数", fetch_house_price, chart_house_price, "房价走势对信贷的影响")
st.divider()

_render_section("八、社会消费品零售总额", fetch_retail_sales, chart_retail_sales, "消费景气度对信贷需求的影响")
st.divider()

# 九、不良贷款率（特殊处理）
st.header("九、商业银行不良贷款率")
try:
    npl_data = fetch_npl_ratio()
    if npl_data is not None and not npl_data.empty and "message" not in npl_data.columns:
        st.dataframe(npl_data.tail(12), use_container_width=True)
    else:
        st.info("不良贷款率数据需要从金融监管总局手动收集，暂未自动化。"
                "当前可参考：2024Q3 商业银行不良贷款率约 1.56%。")
except Exception:
    st.info("不良贷款率数据暂不可用。当前可参考公开报道数据。")

st.divider()

# 十、AI 综合解读
st.header("十、宏观环境综合解读")
_macro_cache_key = "macro_宏观环境综合分析"
if ai_enabled:
    if ANTHROPIC_API_KEY:
        if st.button("🤖 生成宏观环境综合分析", use_container_width=True):
            with st.spinner("AI 正在分析宏观经济环境..."):
                macro_summary = get_macro_summary()
                if macro_summary:
                    insight = generate_section_insight(
                        "宏观经济环境对信贷业务的影响",
                        f"""请结合以下宏观数据，分析当前宏观经济环境对信贷业务的影响：
{json.dumps(macro_summary, ensure_ascii=False, default=str)}

请从以下角度分析：
1. 信贷供给端：货币政策宽松/收紧程度，LPR变化对贷款定价的影响
2. 信贷需求端：经济活跃度（PMI）、消费景气度（社零）、就业情况对借贷需求的影响
3. 资产端：房价走势对抵押品价值和房贷质量的影响
4. 风险端：CPI通胀、失业率变化对借款人还款能力的影响
5. 对客群质量的预判""",
                        cache_key=_macro_cache_key,
                    )
                    render_insight(st, insight, "宏观环境综合分析")
                else:
                    st.warning("暂无缓存数据，请先点击「刷新全部数据」")
    else:
        cached = get_cached_insight(_macro_cache_key)
        if cached:
            render_insight(st, cached, "宏观环境综合分析")
        else:
            st.info("暂无缓存的 AI 分析结论")
else:
    st.info("启用 AI 解读后可自动生成宏观环境综合分析")
