import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "培训_数据源" / "数据产品"

# Data files
DATA_FILES = {
    "scorewis": DATA_DIR / "融智分-scorewis.csv",
    "population": DATA_DIR / "人口衍生-PopulationDerivation.csv",
    "scoreyxbasea": DATA_DIR / "融安云评分-scoreyxbasea.csv",
    "applyloanstr": DATA_DIR / "借贷意向验证-ApplyLoanStr.csv",
    "applyloanusury": DATA_DIR / "借贷风险勘测-ApplyLoanUsury.csv",
    "speciallist": DATA_DIR / "特殊名单验证-SpecialList_c.csv",
    "fraudrelation": DATA_DIR / "团伙欺诈排查（通用版）-FraudRelation_g.csv",
}
DATA_DICT = PROJECT_ROOT / "培训_数据源" / "数据字典.xlsx"

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
CLAUDE_MODEL = "claude-sonnet-4-6"

# Institution type mapping
INSTITUTION_TYPES = ["全部", "银行A", "机构B", "机构C"]

# Age bins
AGE_BINS = [18, 28, 38, 45, 60, 100]
AGE_LABELS = ["[18,28)", "[28,38)", "[38,45)", "[45,60)", "60+"]

# City tier mapping
CITY_TIER_MAP = {
    1: "一线+新一线",
    2: "二线",
    3: "三线",
    4: "四线+五线",
    5: "四线+五线",
    6: "其他城市",
    7: "其他城市",
}

# Scorewis (融智分) income level mapping
SCOREWIS_LABELS = {
    1: "低收入", 2: "低收入", 3: "低收入",
    4: "中低收入", 5: "中低收入", 6: "中低收入",
    7: "中高收入", 8: "中高收入", 9: "中高收入",
    10: "高收入", 11: "高收入", 12: "高收入",
    13: "高收入", 14: "高收入", 15: "高收入",
}

# Chart colors (百融风格)
COLORS = {
    "primary": "#2563EB",
    "secondary": "#F97316",
    "accent": "#8B5CF6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "gray": "#6B7280",
}

COLOR_PALETTE = [
    "#2563EB", "#F97316", "#6B7280", "#EF4444",
    "#8B5CF6", "#10B981", "#F59E0B",
]
