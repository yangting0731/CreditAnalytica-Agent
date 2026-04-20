import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import streamlit.components.v1 as components
from app.styles import inject_css, render_insight
from app.config import INSTITUTION_TYPES, ANTHROPIC_API_KEY
from app.data import analyzer
from app.data.geo_analyzer import (
    province_distribution, province_risk_profile,
    province_income_profile,
)
from app.report import charts, insights, pptx_export
from app.report.map_charts import (
    map_province_heatmap, map_province_risk,
    map_province_income,
)
from app.report.insights import generate_section_insight, get_cached_insight

st.set_page_config(page_title="客群洞察报告", page_icon="📊", layout="wide")
inject_css()
st.title("📊 客群洞察报告")

# 用 session_state 记住当前展示的机构类型
if "report_type" not in st.session_state:
    st.session_state.report_type = "全部"

# 章节导航 — 注入到页面导航区域（客群洞察报告与智能问答之间）
_nav_inject_js = """
<script>
(function() {
  const doc = window.parent.document;
  // 移除旧注入（避免重复）
  const old = doc.getElementById('chapter-nav');
  if (old) old.remove();

  // 找到侧边栏里的页面导航链接
  const links = doc.querySelectorAll('[data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] li a, nav[data-testid="stSidebarNav"] a');
  let targetLink = null;
  for (const a of links) {
    if (a.textContent.includes('客群洞察报告')) { targetLink = a; break; }
  }
  // fallback: 找所有侧边栏链接
  if (!targetLink) {
    const allLinks = doc.querySelectorAll('[data-testid="stSidebar"] a');
    for (const a of allLinks) {
      if (a.textContent.includes('客群洞察报告')) { targetLink = a; break; }
    }
  }
  if (!targetLink) return;

  // 找到包含链接的 li 或最近的容器
  const container = targetLink.closest('li') || targetLink.parentElement;

  // 创建章节导航
  const nav = doc.createElement('div');
  nav.id = 'chapter-nav';
  nav.innerHTML = `
    <style>
      #chapter-nav .ch-link {
        display: block; padding: 4px 12px 4px 28px; margin: 1px 8px;
        font-size: 0.76rem; color: #94A3B8; text-decoration: none;
        border-radius: 4px; cursor: pointer; transition: all 0.15s;
      }
      #chapter-nav .ch-link:hover { background: rgba(255,255,255,0.08); color: #FFFFFF; }
    </style>
    <a class="ch-link" data-ch="一">一、客群基础画像</a>
    <a class="ch-link" data-ch="二">二、客群风险分析</a>
    <a class="ch-link" data-ch="三">三、客群价值分析</a>
    <a class="ch-link" data-ch="四">四、风险联动分析</a>
    <a class="ch-link" data-ch="五">五、客群地理分布</a>
    <a class="ch-link" data-ch="六">六、策略建议</a>
  `;

  // 插入到客群洞察报告之后
  container.after(nav);

  // 点击跳转
  nav.querySelectorAll('.ch-link').forEach(a => {
    a.addEventListener('click', () => {
      const prefix = a.dataset.ch;
      const headers = doc.querySelectorAll('h2, h1');
      for (const h of headers) {
        if (h.textContent.includes(prefix + '、')) {
          h.scrollIntoView({ behavior: 'smooth', block: 'start' });
          break;
        }
      }
    });
  });
})();
</script>
"""

# Sidebar controls
with st.sidebar:
    st.header("报告设置")
    type_filter = st.selectbox("选择机构类型", INSTITUTION_TYPES, index=0)
    if st.button("🚀 生成报告", type="primary", use_container_width=True):
        # 切换机构时清掉旧的 AI 结论缓存
        st.session_state.insight_cache = {}
        st.session_state.report_type = type_filter
        st.rerun()
    ai_enabled = st.toggle("启用 AI 分析结论", value=True)

# 当前展示的机构类型
type_filter = st.session_state.report_type
st.caption(f"当前机构：**{type_filter}** | 切换机构后点击「生成报告」刷新")

# 注入章节导航到页面导航区域（不可见组件）
components.html(_nav_inject_js, height=0)

# AI 结论缓存 — 同一机构不重复调 API
if "insight_cache" not in st.session_state:
    st.session_state.insight_cache = {}


def _get_insight(section: str, generator_fn):
    """带缓存的 AI 结论获取（session → 磁盘 → API 三级 fallback）"""
    if not ai_enabled:
        return ""
    full_key = f"{type_filter}_{section}"
    cache_key = f"report_{section}_{type_filter}"
    # 1. session_state 缓存
    if full_key in st.session_state.insight_cache:
        return st.session_state.insight_cache[full_key]
    # 2. 磁盘缓存（没 API key 时兜底）
    cached = get_cached_insight(cache_key)
    if cached and not ANTHROPIC_API_KEY:
        st.session_state.insight_cache[full_key] = cached
        return cached
    # 3. API 调用
    result = generator_fn(cache_key)
    if result:
        st.session_state.insight_cache[full_key] = result
    elif cached:
        st.session_state.insight_cache[full_key] = cached
        return cached
    return result


# ============================================================
# Generate report
# ============================================================
report_sections = []  # For PPT export

# ------ Part 1: 基础画像 ------
st.header("一、客群基础画像")

# 1.1 性别
st.subheader("1.1 性别分布")
gender_data = analyzer.gender_distribution(type_filter)
col1, col2 = st.columns([1, 1])
with col1:
    fig_gender = charts.chart_gender_distribution(gender_data)
    st.plotly_chart(fig_gender, use_container_width=True)
with col2:
    gender_trend_data = analyzer.gender_trend(type_filter)
    if not gender_trend_data.empty:
        fig_gt = charts.chart_trend_by_gender(gender_trend_data, "bank_avg",
                                               f"{type_filter}_近12月在银行的申请次数均值")
        st.plotly_chart(fig_gt, use_container_width=True)
insight_gender = _get_insight("gender",
    lambda ck: insights.SECTION_GENERATORS["gender"](gender_data.to_dict("records"), ck))
if insight_gender:
    render_insight(st, insight_gender, "性别分布分析")
report_sections.append({"title": "基础画像-性别", "fig": fig_gender, "insight": insight_gender})

st.divider()

# 1.2 年龄
st.subheader("1.2 年龄分布")
age_data = analyzer.age_distribution(type_filter)
col1, col2 = st.columns([1, 1])
with col1:
    fig_age = charts.chart_age_distribution(age_data)
    st.plotly_chart(fig_age, use_container_width=True)
with col2:
    age_trend_data = analyzer.age_trend(type_filter)
    if not age_trend_data.empty:
        fig_at = charts.chart_trend_by_age(age_trend_data, "bank_avg",
                                            f"{type_filter}_近12月在银行的申请次数均值(按年龄)")
        st.plotly_chart(fig_at, use_container_width=True)
insight_age = _get_insight("age",
    lambda ck: insights.SECTION_GENERATORS["age"](age_data.to_dict("records"), ck))
if insight_age:
    render_insight(st, insight_age, "年龄分布分析")
report_sections.append({"title": "基础画像-年龄", "fig": fig_age, "insight": insight_age})

st.divider()

# 1.3 城市等级
st.subheader("1.3 城市等级分布")
city_data = analyzer.city_tier_distribution(type_filter)
col1, col2 = st.columns([1, 1])
with col1:
    fig_city = charts.chart_city_tier_distribution(city_data)
    st.plotly_chart(fig_city, use_container_width=True)
with col2:
    city_trend_data = analyzer.city_tier_trend(type_filter)
    if not city_trend_data.empty:
        fig_ct = charts.chart_trend_by_city_tier(city_trend_data, "bank_avg",
                                                  f"{type_filter}_近12月在银行的申请次数均值(按城市等级)")
        st.plotly_chart(fig_ct, use_container_width=True)
insight_city = _get_insight("city",
    lambda ck: insights.SECTION_GENERATORS["city"](city_data.to_dict("records"), ck))
if insight_city:
    render_insight(st, insight_city, "城市等级分析")
report_sections.append({"title": "基础画像-城市等级", "fig": fig_city, "insight": insight_city})

st.divider()

# ------ Part 2: 风险分析 ------
st.header("二、客群风险分析")

# 2.1 黑灰名单
st.subheader("2.1 黑灰名单分析")
col1, col2 = st.columns([1, 1])
with col1:
    blacklist_data = analyzer.blacklist_hit_rate_trend()
    fig_bl = charts.chart_risk_trend(blacklist_data, "hit_rate", "特殊名单命中率趋势")
    st.plotly_chart(fig_bl, use_container_width=True)
with col2:
    loan_risk_data = analyzer.loan_risk_hit_rate_trend()
    fig_lr = charts.chart_risk_trend(loan_risk_data, "hit_rate", "借贷风险勘测命中率趋势")
    st.plotly_chart(fig_lr, use_container_width=True)
insight_bl = _get_insight("blacklist", lambda ck: insights.SECTION_GENERATORS["blacklist"]({
    "blacklist": blacklist_data.to_dict("records")[-8:],
    "loan_risk": loan_risk_data.to_dict("records")[-8:],
}, ck))
if insight_bl:
    render_insight(st, insight_bl, "黑灰名单风险分析")
report_sections.append({"title": "黑灰名单分析", "fig": fig_bl, "insight": insight_bl})

st.divider()

# 2.2 多头趋势
st.subheader("2.2 客群多头趋势")
multi_data = analyzer.multi_lending_trend_by_type()
col1, col2 = st.columns([1, 1])
with col1:
    fig_mb = charts.chart_multi_lending_trend(multi_data, "bank_avg",
                                               "近12月在银行机构申请次数均值")
    st.plotly_chart(fig_mb, use_container_width=True)
with col2:
    fig_mnb = charts.chart_multi_lending_trend(multi_data, "nbank_avg",
                                                "近12月在非银机构申请次数均值")
    st.plotly_chart(fig_mnb, use_container_width=True)
org_data = analyzer.multi_lending_org_trend_by_type()
col3, col4 = st.columns([1, 1])
with col3:
    fig_ob = charts.chart_multi_lending_trend(org_data, "bank_avg",
                                               "近12月在银行机构申请机构数均值")
    st.plotly_chart(fig_ob, use_container_width=True)
with col4:
    fig_onb = charts.chart_multi_lending_trend(org_data, "nbank_avg",
                                                "近12月在非银机构申请机构数均值")
    st.plotly_chart(fig_onb, use_container_width=True)
insight_multi = _get_insight("multi_lending", lambda ck: insights.SECTION_GENERATORS["multi_lending"]({
    "count_trend": multi_data.to_dict("records")[-8:],
    "org_trend": org_data.to_dict("records")[-8:],
}, ck))
if insight_multi:
    render_insight(st, insight_multi, "多头借贷趋势分析")
report_sections.append({"title": "客群多头趋势", "fig": fig_mb, "insight": insight_multi})

st.divider()

# 2.3 欺诈风险
st.subheader("2.3 客群欺诈风险")
fraud_data = analyzer.fraud_high_risk_trend()
fig_fraud = charts.chart_risk_trend(fraud_data, "high_risk_rate", "团伙欺诈高风险人群占比(等级>=8)")
st.plotly_chart(fig_fraud, use_container_width=True)
insight_fraud = _get_insight("fraud",
    lambda ck: insights.SECTION_GENERATORS["fraud"](fraud_data.to_dict("records")[-8:], ck))
if insight_fraud:
    render_insight(st, insight_fraud, "欺诈风险分析")
report_sections.append({"title": "客群欺诈风险", "fig": fig_fraud, "insight": insight_fraud})

st.divider()

# ------ Part 3: 价值分析 ------
st.header("三、客群价值分析")

# 3.1 收入资质
st.subheader("3.1 客群资质分析（融智分）")
income_data = analyzer.scorewis_distribution_by_type()
col1, col2 = st.columns([1, 1])
with col1:
    fig_income = charts.chart_income_distribution(income_data)
    st.plotly_chart(fig_income, use_container_width=True)
with col2:
    hi_data = analyzer.scorewis_high_income_trend()
    fig_hi = charts.chart_high_income_trend(hi_data)
    st.plotly_chart(fig_hi, use_container_width=True)
insight_income = _get_insight("income", lambda ck: insights.SECTION_GENERATORS["income"]({
    "distribution": income_data.to_dict("records"),
    "high_income_trend": hi_data.to_dict("records")[-6:],
}, ck))
if insight_income:
    render_insight(st, insight_income, "客群资质分析")
report_sections.append({"title": "客群资质分析", "fig": fig_income, "insight": insight_income})

st.divider()

# 3.2 信用风险
st.subheader("3.2 客群信用风险（融安云）")
credit_data = analyzer.credit_score_trend()
fig_credit = charts.chart_credit_score_trend(credit_data)
st.plotly_chart(fig_credit, use_container_width=True)
insight_credit = _get_insight("credit_score",
    lambda ck: insights.SECTION_GENERATORS["credit_score"](credit_data.to_dict("records")[-8:], ck))
if insight_credit:
    render_insight(st, insight_credit, "信用风险分析")
report_sections.append({"title": "客群信用风险", "fig": fig_credit, "insight": insight_credit})

st.divider()

# ------ Part 4: 扩展分析 ------
st.header("四、风险联动分析")

risk_corr = analyzer.risk_correlation_analysis()
if risk_corr:
    col1, col2 = st.columns([1, 1])
    with col1:
        fig_lf = charts.chart_lending_vs_fraud(risk_corr["lending_vs_fraud"])
        st.plotly_chart(fig_lf, use_container_width=True)
    with col2:
        fig_ib = charts.chart_income_vs_blacklist(risk_corr["income_vs_blacklist"])
        st.plotly_chart(fig_ib, use_container_width=True)

heatmap_data = analyzer.risk_heatmap_data()
fig_hm = charts.chart_risk_heatmap(heatmap_data)
st.plotly_chart(fig_hm, use_container_width=True)

if risk_corr:
    insight_corr = _get_insight("risk_correlation", lambda ck: insights.SECTION_GENERATORS["risk_correlation"]({
        "lending_vs_fraud": risk_corr["lending_vs_fraud"].to_dict("records"),
        "income_vs_blacklist": risk_corr["income_vs_blacklist"].to_dict("records"),
    }, ck))
else:
    insight_corr = ""
if insight_corr:
    render_insight(st, insight_corr, "风险联动分析")
report_sections.append({"title": "风险联动分析", "fig": fig_hm, "insight": insight_corr})

st.divider()

# ------ Part 5: 客群地理分布 ------
st.header("五、客群地理分布")

# 5.1 客群地理分布热力图
st.subheader("5.1 客群地理分布热力图")
dist_data = province_distribution(type_filter)
if not dist_data.empty:
    fig_geo_dist = map_province_heatmap(dist_data)
    st.plotly_chart(fig_geo_dist, use_container_width=True)
    with st.expander("Top 10 省份明细"):
        top10 = dist_data.nlargest(10, "count")[["province", "count", "pct"]].reset_index(drop=True)
        top10.columns = ["省份", "客群数量", "占比(%)"]
        top10.index = top10.index + 1
        st.dataframe(top10, use_container_width=True)
    insight_geo_dist = _get_insight("geo_distribution",
        lambda ck: generate_section_insight(
            "客群地理分布",
            f"各省客群数量 Top10: {dist_data.nlargest(10, 'count')[['province', 'count', 'pct']].to_json(orient='records', force_ascii=False)}",
            cache_key=ck))
    if insight_geo_dist:
        render_insight(st, insight_geo_dist, "地理分布分析")
    report_sections.append({"title": "客群地理分布", "fig": fig_geo_dist, "insight": insight_geo_dist or ""})
else:
    st.info("暂无省份数据")

st.divider()

# 5.2 各省风险画像
st.subheader("5.2 各省风险对比")
risk_geo_data = province_risk_profile()
if not risk_geo_data.empty:
    fig_geo_risk = map_province_risk(risk_geo_data)
    st.plotly_chart(fig_geo_risk, use_container_width=True)
    with st.expander("风险最高 Top 10 省份"):
        top10_risk = risk_geo_data.nlargest(10, "risk_score")[
            ["province", "risk_score", "blacklist_rate", "fraud_rate", "total"]
        ].reset_index(drop=True)
        top10_risk.columns = ["省份", "综合风险分", "黑名单命中率(%)", "欺诈高风险率(%)", "样本量"]
        top10_risk.index = top10_risk.index + 1
        st.dataframe(top10_risk, use_container_width=True)
    insight_geo_risk = _get_insight("geo_risk",
        lambda ck: generate_section_insight(
            "各省风险画像分析",
            f"各省风险指标 Top10: {risk_geo_data.nlargest(10, 'risk_score')[['province', 'risk_score', 'blacklist_rate', 'fraud_rate', 'total']].to_json(orient='records', force_ascii=False)}",
            cache_key=ck))
    if insight_geo_risk:
        render_insight(st, insight_geo_risk, "各省风险分析")
    report_sections.append({"title": "各省风险画像", "fig": fig_geo_risk, "insight": insight_geo_risk or ""})
else:
    st.info("风险数据不足")

st.divider()

# 5.3 各省收入资质
st.subheader("5.3 各省高收入客群占比")
income_geo_data = province_income_profile()
if not income_geo_data.empty:
    fig_geo_income = map_province_income(income_geo_data)
    st.plotly_chart(fig_geo_income, use_container_width=True)
    with st.expander("高收入占比 Top 10 省份"):
        top10_income_geo = income_geo_data.nlargest(10, "high_income_rate")[
            ["province", "high_income_rate", "total"]
        ].reset_index(drop=True)
        top10_income_geo.columns = ["省份", "高收入占比(%)", "样本量"]
        top10_income_geo.index = top10_income_geo.index + 1
        st.dataframe(top10_income_geo, use_container_width=True)
    insight_geo_income = _get_insight("geo_income",
        lambda ck: generate_section_insight(
            "各省收入资质分布",
            f"各省高收入占比 Top10: {income_geo_data.nlargest(10, 'high_income_rate')[['province', 'high_income_rate', 'total']].to_json(orient='records', force_ascii=False)}",
            cache_key=ck))
    if insight_geo_income:
        render_insight(st, insight_geo_income, "收入资质分析")
    report_sections.append({"title": "各省收入资质", "fig": fig_geo_income, "insight": insight_geo_income or ""})
else:
    st.info("收入资质数据不足")

st.divider()

# ------ Part 6: 策略建议 ------
st.header("六、策略建议")
strategy_text = _get_insight("strategy", lambda ck: insights.generate_strategy_report(
    analyzer.get_report_summary(type_filter), cache_key=ck))
if strategy_text:
    render_insight(st, strategy_text, "综合策略建议")
else:
    st.info("启用 AI 分析结论后可自动生成策略建议")

# ------ PPT Export ------
st.divider()
st.subheader("导出报告")
if st.button("📥 导出为 PPT", use_container_width=True):
    with st.spinner("正在生成 PPT..."):
        pptx_bytes = pptx_export.generate_pptx(
            report_sections, strategy_text or "",
            title=f"{type_filter} 客群分析报告"
        )
    st.download_button(
        "⬇️ 下载 PPT 文件",
        data=pptx_bytes,
        file_name=f"{type_filter}_客群分析报告.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )
