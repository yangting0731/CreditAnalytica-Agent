"""宏观经济数据爬虫 — 使用 AKShare 获取公开金融数据

加载策略：
- 默认只读本地 CSV 缓存，页面秒开
- 用户点击「刷新数据」时才调用 AKShare API 拉取最新数据
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

# 缓存目录
CACHE_DIR = Path(__file__).parent.parent.parent / "培训_数据源" / "宏观数据缓存"
CACHE_DIR.mkdir(exist_ok=True)


def _load_cache(cache_name: str) -> pd.DataFrame | None:
    """只读本地缓存，不触发网络请求"""
    cache_file = CACHE_DIR / f"{cache_name}.csv"
    if cache_file.exists():
        return pd.read_csv(cache_file)
    return None


def _fetch_and_save(cache_name: str, fetch_fn) -> pd.DataFrame:
    """强制从 AKShare 拉取并保存到缓存"""
    cache_file = CACHE_DIR / f"{cache_name}.csv"
    try:
        df = fetch_fn()
        df.to_csv(cache_file, index=False)
        return df
    except Exception as e:
        # 拉取失败，降级用旧缓存
        if cache_file.exists():
            return pd.read_csv(cache_file)
        raise e


# ============================================================
# 原有数据源
# ============================================================

def fetch_social_financing(force: bool = False) -> pd.DataFrame:
    """社会融资规模增量（月度）"""
    if not force:
        cached = _load_cache("social_financing")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_shrzgm()
        df.columns = [c.strip() for c in df.columns]
        return df
    return _fetch_and_save("social_financing", _fetch)


def fetch_new_credit(force: bool = False) -> pd.DataFrame:
    """新增人民币贷款（月度）"""
    if not force:
        cached = _load_cache("new_credit")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_new_financial_credit()
        df.columns = [c.strip() for c in df.columns]
        return df
    return _fetch_and_save("new_credit", _fetch)


def fetch_money_supply(force: bool = False) -> pd.DataFrame:
    """货币供应量 M2（月度）"""
    if not force:
        cached = _load_cache("money_supply")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_supply_of_money()
        df.columns = [c.strip() for c in df.columns]
        return df
    return _fetch_and_save("money_supply", _fetch)


def fetch_pmi(force: bool = False) -> pd.DataFrame:
    """制造业PMI（月度）"""
    if not force:
        cached = _load_cache("pmi")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_pmi_yearly()
        df.columns = [c.strip() for c in df.columns]
        return df
    return _fetch_and_save("pmi", _fetch)


def fetch_lpr(force: bool = False) -> pd.DataFrame:
    """LPR利率（贷款市场报价利率）"""
    if not force:
        cached = _load_cache("lpr")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_lpr()
        df.columns = [c.strip() for c in df.columns]
        return df
    return _fetch_and_save("lpr", _fetch)


def fetch_npl_ratio(force: bool = False) -> pd.DataFrame:
    """商业银行不良贷款率（季度）"""
    if not force:
        cached = _load_cache("npl_ratio")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        try:
            df = ak.macro_china_bank_supervision()
            df.columns = [c.strip() for c in df.columns]
            return df
        except (AttributeError, Exception):
            pass
        try:
            df = ak.bank_financial_report_em()
            return df
        except (AttributeError, Exception):
            pass
        return pd.DataFrame({"message": ["不良贷款率数据暂不可用，需要手动收集"]})
    return _fetch_and_save("npl_ratio", _fetch)


# ============================================================
# 新增数据源
# ============================================================

def fetch_cpi(force: bool = False) -> pd.DataFrame:
    """CPI 居民消费价格指数（月度同比）"""
    if not force:
        cached = _load_cache("cpi")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_cpi_monthly()
        df.columns = [c.strip() for c in df.columns]
        yr = df[df["商品"].str.contains("年率", na=False)]
        if yr.empty:
            yr = df[df["商品"].str.contains("CPI", na=False)]
        yr = yr.copy()
        yr["今值"] = pd.to_numeric(yr["今值"], errors="coerce")
        yr = yr.dropna(subset=["今值"])
        yr = yr.sort_values("日期").reset_index(drop=True)
        return yr
    return _fetch_and_save("cpi", _fetch)


def fetch_unemployment(force: bool = False) -> pd.DataFrame:
    """城镇调查失业率（月度）"""
    if not force:
        cached = _load_cache("unemployment")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_urban_unemployment()
        df.columns = [c.strip() for c in df.columns]
        df = df[df["item"] == "全国城镇调查失业率"].copy()
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
        df = df.sort_values("date").reset_index(drop=True)
        return df
    return _fetch_and_save("unemployment", _fetch)


def fetch_house_price(force: bool = False) -> pd.DataFrame:
    """70城新建商品住宅价格指数"""
    if not force:
        cached = _load_cache("house_price")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_new_house_price()
        df.columns = [c.strip() for c in df.columns]
        for col in ["新建商品住宅价格指数-同比", "新建商品住宅价格指数-环比"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        agg = df.groupby("日期").agg({
            "新建商品住宅价格指数-同比": "mean",
            "新建商品住宅价格指数-环比": "mean",
        }).reset_index()
        agg = agg.sort_values("日期").reset_index(drop=True)
        return agg
    return _fetch_and_save("house_price", _fetch)


def fetch_retail_sales(force: bool = False) -> pd.DataFrame:
    """社会消费品零售总额（月度）"""
    if not force:
        cached = _load_cache("retail_sales")
        if cached is not None:
            return cached

    import akshare as ak
    def _fetch():
        df = ak.macro_china_consumer_goods_retail()
        df.columns = [c.strip() for c in df.columns]
        for col in ["当月", "同比增长", "累计", "累计-同比增长"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values("月份").reset_index(drop=True)
        return df
    return _fetch_and_save("retail_sales", _fetch)


# ============================================================
# 汇总
# ============================================================

def get_macro_summary() -> dict:
    """获取宏观数据摘要（只读缓存），用于 AI 分析"""
    summary = {}
    fetchers = {
        "social_financing_latest": fetch_social_financing,
        "pmi_latest": fetch_pmi,
        "lpr_latest": fetch_lpr,
        "cpi_latest": fetch_cpi,
        "unemployment_latest": fetch_unemployment,
        "house_price_latest": fetch_house_price,
        "retail_sales_latest": fetch_retail_sales,
    }
    for key, fn in fetchers.items():
        try:
            df = fn()  # 默认 force=False，只读缓存
            if df is not None and not df.empty and "message" not in df.columns:
                summary[key] = df.tail(6).to_dict("records")
        except Exception:
            pass
    return summary


def refresh_all_data():
    """强制刷新所有数据源（用户点击刷新按钮时调用）"""
    results = {}
    fetchers = {
        "社融": fetch_social_financing,
        "PMI": fetch_pmi,
        "M2": fetch_money_supply,
        "LPR": fetch_lpr,
        "不良贷款率": fetch_npl_ratio,
        "CPI": fetch_cpi,
        "失业率": fetch_unemployment,
        "房价": fetch_house_price,
        "社零": fetch_retail_sales,
    }
    for name, fn in fetchers.items():
        try:
            fn(force=True)
            results[name] = "ok"
        except Exception as e:
            results[name] = str(e)
    return results
