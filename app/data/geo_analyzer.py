"""地理维度分析函数 — 基于人口衍生数据的省份/城市分析"""
import pandas as pd
import streamlit as st
from app.data.loader import load_population, load_speciallist, load_fraudrelation, load_scorewis

# 省份名 → GeoJSON 全称映射
PROVINCE_SUFFIX = {
    "北京": "北京市", "天津": "天津市", "上海": "上海市", "重庆": "重庆市",
    "河北": "河北省", "山西": "山西省", "辽宁": "辽宁省", "吉林": "吉林省",
    "黑龙江": "黑龙江省", "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省",
    "福建": "福建省", "江西": "江西省", "山东": "山东省", "河南": "河南省",
    "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省", "海南": "海南省",
    "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "陕西": "陕西省",
    "甘肃": "甘肃省", "青海": "青海省", "台湾": "台湾省",
    "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区",
    "香港": "香港特别行政区", "澳门": "澳门特别行政区",
}

# Top 50 城市经纬度（用于迁移流向图）
CITY_COORDS = {
    "北京": (39.90, 116.40), "上海": (31.23, 121.47), "广州": (23.13, 113.26),
    "深圳": (22.54, 114.06), "成都": (30.57, 104.07), "重庆": (29.56, 106.55),
    "杭州": (30.27, 120.15), "武汉": (30.58, 114.30), "西安": (34.26, 108.94),
    "苏州": (31.30, 120.62), "南京": (32.06, 118.80), "天津": (39.13, 117.20),
    "长沙": (28.23, 112.94), "郑州": (34.75, 113.65), "东莞": (23.04, 113.75),
    "青岛": (36.07, 120.38), "沈阳": (41.80, 123.43), "宁波": (29.87, 121.55),
    "昆明": (25.04, 102.71), "大连": (38.91, 121.61), "福州": (26.07, 119.30),
    "厦门": (24.48, 118.09), "哈尔滨": (45.75, 126.65), "济南": (36.65, 116.98),
    "温州": (28.00, 120.67), "佛山": (23.02, 113.12), "合肥": (31.82, 117.23),
    "南昌": (28.68, 115.86), "贵阳": (26.65, 106.63), "南宁": (22.82, 108.37),
    "石家庄": (38.04, 114.51), "太原": (37.87, 112.55), "长春": (43.88, 125.32),
    "乌鲁木齐": (43.80, 87.60), "兰州": (36.06, 103.83), "呼和浩特": (40.84, 111.75),
    "海口": (20.02, 110.35), "银川": (38.49, 106.23), "西宁": (36.62, 101.78),
    "拉萨": (29.65, 91.13), "临沂": (35.10, 118.35), "阜阳": (32.89, 115.81),
    "菏泽": (35.23, 115.47), "周口": (33.63, 114.65), "济宁": (35.41, 116.59),
    "毕节": (27.30, 105.28), "潍坊": (36.71, 119.16), "南阳": (32.99, 112.53),
    "徐州": (34.26, 117.18), "保定": (38.87, 115.46),
}


def _add_province_full(df: pd.DataFrame, col: str = "province") -> pd.DataFrame:
    """将简称省份映射为 GeoJSON 全称"""
    df = df.copy()
    df["province_full"] = df[col].map(PROVINCE_SUFFIX)
    return df.dropna(subset=["province_full"])


@st.cache_data(ttl=3600)
def province_distribution(type_filter: str = "全部") -> pd.DataFrame:
    """各省客群数量分布"""
    pop = load_population()
    if type_filter != "全部":
        pop = pop[pop["type"] == type_filter]
    counts = pop["pd_cell_province"].value_counts().reset_index()
    counts.columns = ["province", "count"]
    counts["pct"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    return _add_province_full(counts)


@st.cache_data(ttl=3600)
def province_risk_profile() -> pd.DataFrame:
    """各省风险指标（黑名单命中率 + 欺诈高风险率）"""
    pop = load_population()[["cus_num", "user_date", "type", "pd_cell_province"]].copy()
    pop = pop.dropna(subset=["pd_cell_province"])

    # Join 特殊名单
    sl = load_speciallist()
    merged = pop.merge(sl[["cus_num", "user_date", "type", "flag_specialList_c"]],
                       on=["cus_num", "user_date", "type"], how="left")

    # Join 欺诈
    fraud = load_fraudrelation()
    merged = merged.merge(fraud[["cus_num", "user_date", "type", "frg_list_level"]],
                          on=["cus_num", "user_date", "type"], how="left")

    # 按省聚合
    agg = merged.groupby("pd_cell_province").agg(
        total=("cus_num", "count"),
        blacklist_hits=("flag_specialList_c", lambda x: (pd.to_numeric(x, errors="coerce") == 1).sum()),
        fraud_high=("frg_list_level", lambda x: (pd.to_numeric(x, errors="coerce") >= 8).sum()),
    ).reset_index()
    agg.columns = ["province", "total", "blacklist_hits", "fraud_high"]
    agg["blacklist_rate"] = (agg["blacklist_hits"] / agg["total"] * 100).round(2)
    agg["fraud_rate"] = (agg["fraud_high"] / agg["total"] * 100).round(2)
    agg["risk_score"] = (agg["blacklist_rate"] * 0.5 + agg["fraud_rate"] * 0.5).round(2)
    agg = agg[agg["total"] >= 100]  # 过滤样本太少的省份
    return _add_province_full(agg)


@st.cache_data(ttl=3600)
def province_income_profile() -> pd.DataFrame:
    """各省收入资质分布（高收入占比）"""
    pop = load_population()[["cus_num", "user_date", "type", "pd_cell_province"]].copy()
    pop = pop.dropna(subset=["pd_cell_province"])

    scorewis = load_scorewis()
    if "scorewis" not in scorewis.columns:
        return pd.DataFrame()

    merged = pop.merge(scorewis[["cus_num", "user_date", "type", "scorewis"]],
                       on=["cus_num", "user_date", "type"], how="left")
    merged["scorewis"] = pd.to_numeric(merged["scorewis"], errors="coerce")
    merged = merged.dropna(subset=["scorewis"])

    # 高收入: scorewis 1-5 (等级1为最高)
    merged["is_high_income"] = merged["scorewis"].isin([1, 2, 3, 4, 5])

    agg = merged.groupby("pd_cell_province").agg(
        total=("cus_num", "count"),
        high_income=("is_high_income", "sum"),
    ).reset_index()
    agg.columns = ["province", "total", "high_income"]
    agg["high_income_rate"] = (agg["high_income"] / agg["total"] * 100).round(2)
    agg = agg[agg["total"] >= 100]
    return _add_province_full(agg)


@st.cache_data(ttl=3600)
def migration_flows(top_n: int = 30) -> pd.DataFrame:
    """手机城市 vs 身份证城市 迁移流向 Top N"""
    pop = load_population()[["pd_cell_city", "pd_id_city"]].copy()
    pop = pop.dropna(subset=["pd_cell_city", "pd_id_city"])
    # 只保留不同城市的记录（迁移）
    pop = pop[pop["pd_cell_city"] != pop["pd_id_city"]]

    flows = pop.groupby(["pd_id_city", "pd_cell_city"]).size().reset_index(name="count")
    flows.columns = ["from_city", "to_city", "count"]
    flows = flows.sort_values("count", ascending=False).head(top_n)

    # 添加经纬度
    flows["from_lat"] = flows["from_city"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    flows["from_lon"] = flows["from_city"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])
    flows["to_lat"] = flows["to_city"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    flows["to_lon"] = flows["to_city"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])

    # 过滤掉找不到经纬度的
    flows = flows.dropna(subset=["from_lat", "to_lat"])
    return flows
