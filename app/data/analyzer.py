"""分析计算引擎 — 所有分析维度的计算逻辑"""
import pandas as pd
import numpy as np
from app.data.loader import (
    load_population, load_scorewis, load_scoreyxbasea,
    load_applyloanstr, load_applyloanusury,
    load_speciallist, load_fraudrelation, filter_by_type,
)
from app.config import INSTITUTION_TYPES


# ============================================================
# 基础画像
# ============================================================

def gender_distribution(type_filter: str = "全部") -> pd.DataFrame:
    """性别分布 — 返回各机构类型的男女占比"""
    df = load_population()
    types = [type_filter] if type_filter != "全部" else [t for t in INSTITUTION_TYPES if t != "全部"]
    results = []
    # 整体大盘
    total = df["gender"].value_counts(normalize=True) * 100
    results.append({"group": "整体", "男": round(total.get("男", 0), 2), "女": round(total.get("女", 0), 2)})
    for t in types:
        sub = df[df["type"] == t]
        dist = sub["gender"].value_counts(normalize=True) * 100
        results.append({"group": t, "男": round(dist.get("男", 0), 2), "女": round(dist.get("女", 0), 2)})
    return pd.DataFrame(results)


def gender_trend(type_filter: str = "全部") -> pd.DataFrame:
    """性别 x 季度 — 近12月在银行/非银的申请次数均值(按性别)"""
    pop = filter_by_type(load_population(), type_filter)[["cus_num", "user_date", "gender", "quarter"]]
    loan = filter_by_type(load_applyloanstr(), type_filter)
    merged = pop.merge(loan, on=["cus_num", "user_date"], how="left", suffixes=("", "_loan"))
    bank_col = "als_m12_id_bank_allnum"
    nbank_col = "als_m12_id_nbank_allnum"
    if bank_col not in merged.columns:
        return pd.DataFrame()
    result = merged.groupby(["quarter", "gender"]).agg(
        bank_avg=(bank_col, "mean"),
        nbank_avg=(nbank_col, "mean"),
    ).reset_index()
    return result.sort_values("quarter")


def age_distribution(type_filter: str = "全部") -> pd.DataFrame:
    """年龄段分布 — 返回各机构类型的年龄段占比"""
    df = load_population()
    types = [type_filter] if type_filter != "全部" else [t for t in INSTITUTION_TYPES if t != "全部"]
    results = []
    total = df["age_group"].value_counts(normalize=True).sort_index() * 100
    row = {"group": "整体"}
    for age in total.index:
        row[str(age)] = round(total[age], 2)
    results.append(row)
    for t in types:
        sub = df[df["type"] == t]
        dist = sub["age_group"].value_counts(normalize=True).sort_index() * 100
        row = {"group": t}
        for age in dist.index:
            row[str(age)] = round(dist[age], 2)
        results.append(row)
    return pd.DataFrame(results)


def age_trend(type_filter: str = "全部") -> pd.DataFrame:
    """年龄段 x 季度 — 银行/非银申请次数均值"""
    pop = filter_by_type(load_population(), type_filter)[["cus_num", "user_date", "age_group", "quarter"]]
    loan = filter_by_type(load_applyloanstr(), type_filter)
    merged = pop.merge(loan, on=["cus_num", "user_date"], how="left", suffixes=("", "_loan"))
    bank_col = "als_m12_id_bank_allnum"
    nbank_col = "als_m12_id_nbank_allnum"
    if bank_col not in merged.columns:
        return pd.DataFrame()
    result = merged.groupby(["quarter", "age_group"]).agg(
        bank_avg=(bank_col, "mean"),
        nbank_avg=(nbank_col, "mean"),
    ).reset_index()
    result["age_group"] = result["age_group"].astype(str)
    return result.sort_values("quarter")


def city_tier_distribution(type_filter: str = "全部") -> pd.DataFrame:
    """城市等级分布"""
    df = load_population()
    tier_order = ["一线+新一线", "二线", "三线", "四线+五线", "其他城市"]
    types = [type_filter] if type_filter != "全部" else [t for t in INSTITUTION_TYPES if t != "全部"]
    results = []
    total = df["city_tier"].value_counts(normalize=True) * 100
    row = {"group": "整体"}
    for tier in tier_order:
        row[tier] = round(total.get(tier, 0), 2)
    results.append(row)
    for t in types:
        sub = df[df["type"] == t]
        dist = sub["city_tier"].value_counts(normalize=True) * 100
        row = {"group": t}
        for tier in tier_order:
            row[tier] = round(dist.get(tier, 0), 2)
        results.append(row)
    return pd.DataFrame(results)


def city_tier_trend(type_filter: str = "全部") -> pd.DataFrame:
    """城市等级 x 季度 — 银行/非银申请次数均值"""
    pop = filter_by_type(load_population(), type_filter)[["cus_num", "user_date", "city_tier", "quarter"]]
    loan = filter_by_type(load_applyloanstr(), type_filter)
    merged = pop.merge(loan, on=["cus_num", "user_date"], how="left", suffixes=("", "_loan"))
    bank_col = "als_m12_id_bank_allnum"
    nbank_col = "als_m12_id_nbank_allnum"
    if bank_col not in merged.columns:
        return pd.DataFrame()
    result = merged.groupby(["quarter", "city_tier"]).agg(
        bank_avg=(bank_col, "mean"),
        nbank_avg=(nbank_col, "mean"),
    ).reset_index()
    return result.sort_values("quarter")


# ============================================================
# 多头借贷分析
# ============================================================

def multi_lending_trend_by_type() -> pd.DataFrame:
    """各机构类型的近12月银行/非银申请次数均值趋势（按季度）"""
    loan = load_applyloanstr()
    bank_col = "als_m12_id_bank_allnum"
    nbank_col = "als_m12_id_nbank_allnum"
    if bank_col not in loan.columns:
        return pd.DataFrame()
    result = loan.groupby(["quarter", "type"]).agg(
        bank_avg=(bank_col, "mean"),
        nbank_avg=(nbank_col, "mean"),
    ).reset_index()
    return result.sort_values("quarter")


def multi_lending_org_trend_by_type() -> pd.DataFrame:
    """各机构类型的近12月银行/非银申请机构数均值趋势（按季度）"""
    loan = load_applyloanstr()
    bank_col = "als_m12_id_bank_orgnum"
    nbank_col = "als_m12_id_nbank_orgnum"
    if bank_col not in loan.columns:
        return pd.DataFrame()
    result = loan.groupby(["quarter", "type"]).agg(
        bank_avg=(bank_col, "mean"),
        nbank_avg=(nbank_col, "mean"),
    ).reset_index()
    return result.sort_values("quarter")


# ============================================================
# 风险分析
# ============================================================

def blacklist_hit_rate_trend() -> pd.DataFrame:
    """特殊名单命中率趋势（按季度 x 机构类型）"""
    df = load_speciallist()
    result = df.groupby(["quarter", "type"]).agg(
        hit_rate=("flag_specialList_c", "mean"),
        total=("flag_specialList_c", "count"),
    ).reset_index()
    result["hit_rate"] = (result["hit_rate"] * 100).round(2)
    return result.sort_values("quarter")


def loan_risk_hit_rate_trend() -> pd.DataFrame:
    """借贷风险勘测命中率趋势（按季度 x 机构类型）"""
    df = load_applyloanusury()
    result = df.groupby(["quarter", "type"]).agg(
        hit_rate=("flag_applyloanusury", "mean"),
        total=("flag_applyloanusury", "count"),
    ).reset_index()
    result["hit_rate"] = (result["hit_rate"] * 100).round(2)
    return result.sort_values("quarter")


def fraud_high_risk_trend() -> pd.DataFrame:
    """团伙欺诈高风险（等级>=8）占比趋势（按季度 x 机构类型）"""
    df = load_fraudrelation()
    df["is_high_risk"] = (df["frg_list_level"] >= 8).astype(int)
    result = df.groupby(["quarter", "type"]).agg(
        high_risk_rate=("is_high_risk", "mean"),
        total=("is_high_risk", "count"),
    ).reset_index()
    result["high_risk_rate"] = (result["high_risk_rate"] * 100).round(2)
    return result.sort_values("quarter")


# ============================================================
# 价值分析
# ============================================================

def scorewis_distribution_by_type() -> pd.DataFrame:
    """融智分收入等级分布（按机构类型）"""
    df = load_scorewis()
    df = df[df["flag_score"] == 1].copy()  # 只看有评分的
    income_order = ["低收入", "中低收入", "中高收入", "高收入"]
    results = []
    for t in [t for t in INSTITUTION_TYPES if t != "全部"]:
        sub = df[df["type"] == t]
        dist = sub["income_level"].value_counts(normalize=True) * 100
        row = {"group": t}
        for level in income_order:
            row[level] = round(dist.get(level, 0), 2)
        # 未命中
        all_type = load_scorewis()
        all_type = all_type[all_type["type"] == t]
        miss_rate = (1 - all_type["flag_score"].mean()) * 100
        row["未命中"] = round(miss_rate, 2)
        results.append(row)
    return pd.DataFrame(results)


def scorewis_high_income_trend() -> pd.DataFrame:
    """万元及以上收入人群占比趋势（融智分>=10 对应高收入）"""
    df = load_scorewis()
    df = df[df["flag_score"] == 1].copy()
    df["is_high_income"] = (df["scorewis"] >= 10).astype(int)
    result = df.groupby(["year_month", "type"]).agg(
        high_income_rate=("is_high_income", "mean"),
    ).reset_index()
    result["high_income_rate"] = (result["high_income_rate"] * 100).round(2)
    return result.sort_values("year_month")


def credit_score_trend() -> pd.DataFrame:
    """融安云评分均值趋势（按季度 x 机构类型）"""
    df = load_scoreyxbasea()
    df = df[df["flag_score"] == 1].copy()
    result = df.groupby(["quarter", "type"]).agg(
        avg_score=("scoreyxbasea", "mean"),
    ).reset_index()
    result["avg_score"] = result["avg_score"].round(1)
    return result.sort_values("quarter")


# ============================================================
# 扩展分析
# ============================================================

def risk_correlation_analysis() -> dict:
    """风险联动分析 — 高多头 vs 欺诈率，低收入 vs 黑名单命中率"""
    pop = load_population()[["cus_num", "user_date", "type"]]
    loan = load_applyloanstr()
    fraud = load_fraudrelation()
    scorewis = load_scorewis()
    speciallist = load_speciallist()

    # 合并多头和欺诈数据
    bank_col = "als_m12_id_bank_allnum"
    nbank_col = "als_m12_id_nbank_allnum"
    if bank_col not in loan.columns:
        return {}

    merged = pop.merge(loan[["cus_num", "user_date", bank_col, nbank_col]],
                       on=["cus_num", "user_date"], how="left")
    merged = merged.merge(fraud[["cus_num", "user_date", "frg_list_level"]],
                          on=["cus_num", "user_date"], how="left")
    merged = merged.merge(scorewis[["cus_num", "user_date", "scorewis", "flag_score"]],
                          on=["cus_num", "user_date"], how="left")
    merged = merged.merge(speciallist[["cus_num", "user_date", "flag_specialList_c"]],
                          on=["cus_num", "user_date"], how="left")

    # 1) 多头借贷分组 vs 欺诈率
    merged["total_lending"] = merged[bank_col].fillna(0) + merged[nbank_col].fillna(0)
    merged["lending_group"] = pd.cut(merged["total_lending"],
                                     bins=[-1, 5, 15, 30, 999999],
                                     labels=["低(0-5)", "中(6-15)", "高(16-30)", "极高(30+)"])
    merged["is_fraud_high"] = (merged["frg_list_level"] >= 8).astype(int)
    lending_fraud = merged.groupby("lending_group", observed=True).agg(
        fraud_rate=("is_fraud_high", "mean"),
        count=("is_fraud_high", "count"),
    ).reset_index()
    lending_fraud["fraud_rate"] = (lending_fraud["fraud_rate"] * 100).round(2)

    # 2) 收入等级 vs 黑名单命中率
    score_df = merged[merged["flag_score"] == 1].copy()
    score_df["income_group"] = pd.cut(score_df["scorewis"],
                                      bins=[0, 3, 6, 9, 15],
                                      labels=["低收入", "中低收入", "中高收入", "高收入"])
    income_blacklist = score_df.groupby("income_group", observed=True).agg(
        blacklist_rate=("flag_specialList_c", "mean"),
        count=("flag_specialList_c", "count"),
    ).reset_index()
    income_blacklist["blacklist_rate"] = (income_blacklist["blacklist_rate"] * 100).round(2)

    return {
        "lending_vs_fraud": lending_fraud,
        "income_vs_blacklist": income_blacklist,
    }


def risk_heatmap_data() -> pd.DataFrame:
    """年龄 x 城市等级 的欺诈风险热力图"""
    pop = load_population()[["cus_num", "user_date", "age_group", "city_tier"]]
    fraud = load_fraudrelation()[["cus_num", "user_date", "frg_list_level"]]
    merged = pop.merge(fraud, on=["cus_num", "user_date"], how="left")
    merged["is_fraud_high"] = (merged["frg_list_level"] >= 8).astype(int)
    result = merged.groupby(["age_group", "city_tier"], observed=True).agg(
        fraud_rate=("is_fraud_high", "mean"),
        count=("is_fraud_high", "count"),
    ).reset_index()
    result["fraud_rate"] = (result["fraud_rate"] * 100).round(2)
    result["age_group"] = result["age_group"].astype(str)
    return result


def get_report_summary(type_filter: str = "全部") -> dict:
    """汇总所有分析数据，用于 AI 生成策略建议"""
    summary = {}
    summary["gender"] = gender_distribution(type_filter).to_dict("records")
    summary["age"] = age_distribution(type_filter).to_dict("records")
    summary["city"] = city_tier_distribution(type_filter).to_dict("records")
    summary["blacklist_trend"] = blacklist_hit_rate_trend().to_dict("records")[-4:]  # 最近4季度
    summary["loan_risk_trend"] = loan_risk_hit_rate_trend().to_dict("records")[-4:]
    summary["fraud_trend"] = fraud_high_risk_trend().to_dict("records")[-4:]
    summary["credit_score"] = credit_score_trend().to_dict("records")[-4:]
    summary["income"] = scorewis_distribution_by_type().to_dict("records")
    risk = risk_correlation_analysis()
    if risk:
        summary["lending_vs_fraud"] = risk["lending_vs_fraud"].to_dict("records")
        summary["income_vs_blacklist"] = risk["income_vs_blacklist"].to_dict("records")
    return summary
