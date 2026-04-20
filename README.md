# CreditAnalytica-Agent

百融智能分析 Agent — 信贷场景客群分析平台

## 功能

- **报告生成** — 客群基础画像、风险分析、价值分析，一键导出 PPT
- **智能问答** — 基于 Claude 的信贷数据对话式分析
- **宏观环境** — 8 项宏观经济指标自动抓取与可视化
- **地图分析** — 省份维度客群分布、风险画像、收入资质

## 快速开始

### 1. 安装 Git LFS（必须）

数据文件通过 Git LFS 存储，**必须先安装再 clone**：

```bash
# macOS
brew install git-lfs

# Windows
# 从 https://git-lfs.github.com 下载安装

# 初始化
git lfs install
```

### 2. 克隆项目

```bash
git clone https://github.com/yangting0731/CreditAnalytica-Agent.git
cd CreditAnalytica-Agent
```

> 如果已经 clone 但没装 LFS，需要重新拉取数据文件：`git lfs pull`

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key（可选）

复制环境变量模板并填入你的 Claude API Key：

```bash
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY
```

> **没有 API Key 也能用！** 所有 AI 分析结论已预生成并缓存，打开即可查看。

### 5. 启动

```bash
streamlit run app/系统概览.py
```

浏览器打开 `http://localhost:8501`

## 项目结构

```
app/
  系统概览.py            # 首页
  config.py            # 配置
  styles.py            # 设计系统
  pages/
    1_客群洞察报告.py    # 客群分析报告（含地理分布）
    2_智能问答.py       # AI 对话
  data/                # 数据加载与分析
  report/              # 图表与 AI 结论
  agent/               # AI Agent
培训_数据源/            # 数据文件（LFS）
```

## 技术栈

Streamlit + Plotly + Pandas + Claude API + AKShare
