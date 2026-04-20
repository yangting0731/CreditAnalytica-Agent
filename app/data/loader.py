import pandas as pd
import streamlit as st
from pathlib import Path
from app.config import DATA_FILES, AGE_BINS, AGE_LABELS, CITY_TIER_MAP, SCOREWIS_LABELS


def _read_csv(path, **kwargs):
    """统一的 CSV 读取：跳过第2行（中文说明行），低内存模式关闭"""
    return pd.read_csv(path, skiprows=[1], low_memory=False, **kwargs)


def _add_time_cols(df: pd.DataFrame) -> pd.DataFrame:
    """添加时间衍生列"""
    df["user_date"] = pd.to_datetime(df["user_date"], format="%Y-%m-%d")
    df["year_month"] = df["user_date"].dt.to_period("M").astype(str)
    df["quarter"] = df["user_date"].dt.to_period("Q").astype(str)
    return df


@st.cache_data(ttl=3600)
def load_population() -> pd.DataFrame:
    """加载人口衍生数据（基础画像：性别、年龄、城市等级）"""
    df = _read_csv(DATA_FILES["population"], usecols=[
        "cus_num", "user_date", "type",
        "pd_id_gender", "pd_id_apply_age",
        "pd_cell_city_level", "pd_id_city_level",
        "pd_cell_province", "pd_cell_city", "pd_id_city",
    ])
    df = _add_time_cols(df)
    # Ensure numeric
    df["pd_id_gender"] = pd.to_numeric(df["pd_id_gender"], errors="coerce")
    df["pd_id_apply_age"] = pd.to_numeric(df["pd_id_apply_age"], errors="coerce")
    df["pd_cell_city_level"] = pd.to_numeric(df["pd_cell_city_level"], errors="coerce")
    df["pd_id_city_level"] = pd.to_numeric(df["pd_id_city_level"], errors="coerce")
    # Gender: 1=男, 0=女 (confirmed by PDF: 男性占比~70%)
    df["gender"] = df["pd_id_gender"].map({1: "男", 0: "女"})
    # Age bins
    df["age_group"] = pd.cut(
        df["pd_id_apply_age"], bins=AGE_BINS, labels=AGE_LABELS, right=False
    )
    # City tier (use phone city tier, fallback to ID city tier)
    city_tier = df["pd_cell_city_level"].fillna(df["pd_id_city_level"])
    df["city_tier"] = city_tier.map(CITY_TIER_MAP).fillna("其他城市")
    return df


@st.cache_data(ttl=3600)
def load_scorewis() -> pd.DataFrame:
    """加载融智分（收入/资质等级评估）"""
    df = _read_csv(DATA_FILES["scorewis"])
    df = _add_time_cols(df)
    df["flag_score"] = pd.to_numeric(df["flag_score"], errors="coerce")
    df["scorewis"] = pd.to_numeric(df["scorewis"], errors="coerce")
    # Map score to income level
    df["income_level"] = df["scorewis"].map(SCOREWIS_LABELS)
    return df


@st.cache_data(ttl=3600)
def load_scoreyxbasea() -> pd.DataFrame:
    """加载融安云评分（信用风险评分 300-1000）"""
    df = _read_csv(DATA_FILES["scoreyxbasea"])
    # Fix column name bug: scorewis -> scoreyxbasea
    if "scoreyxbasea" not in df.columns and "scorewis" in df.columns:
        df = df.rename(columns={"scorewis": "scoreyxbasea"})
    df = _add_time_cols(df)
    df["flag_score"] = pd.to_numeric(df["flag_score"], errors="coerce")
    df["scoreyxbasea"] = pd.to_numeric(df["scoreyxbasea"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_applyloanstr() -> pd.DataFrame:
    """加载借贷意向验证（多头借贷数据）— 只加载关键列"""
    key_cols = [
        "cus_num", "user_date", "type", "flag_applyloanstr",
        # 各时间窗口-银行/非银-总次数和机构数
        "als_m12_id_bank_allnum", "als_m12_id_bank_orgnum",
        "als_m12_id_nbank_allnum", "als_m12_id_nbank_orgnum",
        "als_m6_id_bank_allnum", "als_m6_id_bank_orgnum",
        "als_m6_id_nbank_allnum", "als_m6_id_nbank_orgnum",
        "als_m3_id_bank_allnum", "als_m3_id_bank_orgnum",
        "als_m3_id_nbank_allnum", "als_m3_id_nbank_orgnum",
        "als_m1_id_bank_allnum", "als_m1_id_bank_orgnum",
        "als_m1_id_nbank_allnum", "als_m1_id_nbank_orgnum",
    ]
    # Read header to find valid columns
    all_cols = pd.read_csv(DATA_FILES["applyloanstr"], nrows=0).columns.tolist()
    valid_cols = [c for c in key_cols if c in all_cols]
    df = _read_csv(DATA_FILES["applyloanstr"], usecols=valid_cols)
    df = _add_time_cols(df)
    # Ensure numeric for analysis columns
    for col in valid_cols:
        if col not in ("cus_num", "user_date", "type"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_applyloanusury() -> pd.DataFrame:
    """加载借贷风险勘测"""
    df = _read_csv(DATA_FILES["applyloanusury"])
    df = _add_time_cols(df)
    df["flag_applyloanusury"] = pd.to_numeric(df["flag_applyloanusury"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_speciallist() -> pd.DataFrame:
    """加载特殊名单验证（黑灰名单）"""
    df = _read_csv(DATA_FILES["speciallist"])
    df = _add_time_cols(df)
    df["flag_specialList_c"] = pd.to_numeric(df["flag_specialList_c"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_fraudrelation() -> pd.DataFrame:
    """加载团伙欺诈排查"""
    df = _read_csv(DATA_FILES["fraudrelation"])
    df = _add_time_cols(df)
    df["frg_list_level"] = pd.to_numeric(df["frg_list_level"], errors="coerce")
    return df


def filter_by_type(df: pd.DataFrame, type_filter: str) -> pd.DataFrame:
    """按机构类型筛选"""
    if type_filter == "全部":
        return df
    return df[df["type"] == type_filter].copy()
