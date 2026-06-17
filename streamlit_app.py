import json
import html
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

# =====================================================
# Memento v5 — onboarding · personal risk profile
# =====================================================
st.set_page_config(
    page_title="Memento",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');

/* =====================================================================
   Memento — single design system
   Brief: a calm analyst's terminal for prediction markets.
   Identity: hairlines, tabular numerics, one indigo accent, a verdict
   system (dot + word + pill) repeated identically everywhere.
   Every class name below is also used by the Python render helpers, so
   this stylesheet is purely visual — it changes no app logic.
   ===================================================================== */
:root {
  --bg:        #fbfbfc;
  --surface:   #ffffff;
  --surface-2: #f4f5f7;
  --surface-3: #fafafb;
  --ink:       #15161a;
  --ink2:      #3c3e46;
  --gray:      #71747e;
  --gray2:     #a2a5af;
  --hairline:  #e9eaee;
  --hairline-2:#f0f1f4;

  --accent:      #3b4ef0;   /* deep indigo — the one accent */
  --accent-press:#2c3ed4;
  --accent-soft: #eef0fe;

  --green:      #0f7a43;  --green-soft: #e7f5ec;  --green-soft2:#eaf6f0;
  --amber:      #a45e07;  --amber-soft: #fdf3e3;
  --red:        #c5362f;  --red-soft:   #fdeeed;

  --radius-s: 10px;
  --radius-m: 16px;
  --radius-l: 22px;

  --shadow-1: 0 1px 1px rgba(20,22,30,.03);
  --shadow-2: 0 1px 2px rgba(20,22,30,.04), 0 10px 30px rgba(20,22,30,.05);

  --mono: ui-monospace, "SF Mono", "JetBrains Mono", "Cascadia Mono", Menlo, monospace;
}

html, body, .stApp { background: var(--bg) !important; color: var(--ink) !important; }

*:not([data-testid="stIconMaterial"]):not(.material-icons):not([class*="material-symbols"]) {
  font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}
span[data-testid="stIconMaterial"] {
  font-family: 'Material Symbols Rounded' !important;
  font-size: 19px !important; color: var(--gray) !important;
}

.block-container {
  max-width: 1080px;
  padding-top: 3.2rem !important;
  padding-bottom: 5rem !important;
  overflow: visible !important;
}
section[data-testid="stSidebar"] { display: none; }
.stApp, .main, div[data-testid="stAppViewContainer"] { overflow: visible !important; }
header[data-testid="stHeader"] {
  background: rgba(251,251,252,.82) !important;
  backdrop-filter: saturate(180%) blur(16px); -webkit-backdrop-filter: saturate(180%) blur(16px);
  height: auto !important; min-height: 2.6rem !important; z-index: 50 !important; border: none !important;
}
h1,h2,h3,h4,p,span,div,label { color: var(--ink); }
:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

/* ---------- masthead + page intros ---------- */
.masthead { padding: 4px 0 2px 0 !important; margin: 0 !important; overflow: visible !important; }
.masthead .name {
  font-size: 23px; font-weight: 760; letter-spacing: -.04em;
  display: inline-flex; align-items: center; gap: 9px;
}
.masthead .name::before {
  content: ""; width: 13px; height: 13px; border-radius: 4px; transform: rotate(45deg);
  background: linear-gradient(135deg, var(--accent), #6b7bff);
}
.masthead .tag { font-size: 12px; color: var(--gray2); margin-top: 4px; }
.mh-chip {
  display: inline-block; margin: 8px 0 16px 0 !important;
  font-size: 11.5px; color: var(--gray); background: var(--surface-2);
  border: 1px solid var(--hairline); border-radius: 999px; padding: 5px 13px;
  letter-spacing: .005em;
}

.headline { font-size: 29px; font-weight: 760; letter-spacing: -.04em; line-height: 1.1; margin: 10px 0 4px 0; }
.subline  { font-size: 14px; color: var(--gray); line-height: 1.55; margin-bottom: 20px; max-width: 740px; }
.eyebrow  {
  margin: 22px 0 9px 0; font-size: 11px; font-weight: 750; color: var(--gray);
  letter-spacing: .09em; text-transform: uppercase;
}

/* ---------- verdict band (the signature element) ---------- */
.verdict {
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-radius: var(--radius-l);
  box-shadow: var(--shadow-2);
  padding: 22px 24px;
  margin: 14px 0 18px 0;
}
.verdict .eyebrow { margin-top: 0; }
.verdict .v-title { font-size: 33px; font-weight: 770; letter-spacing: -.045em; line-height: 1.1; }
.verdict .v-sub   { margin-top: 9px; font-size: 14px; color: var(--gray); line-height: 1.6; }

.dot { display:inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 11px; vertical-align: 3px; }
.dot.g { background: var(--green); }
.dot.w { background: var(--amber); }
.dot.b { background: var(--red); }
.dot.i { background: var(--gray2); }

/* ---------- pills / state chips ---------- */
.state, .pill {
  display:inline-block; border-radius: 999px; padding: 5px 11px;
  font-size: 12px; font-weight: 680; letter-spacing: -.005em; white-space: nowrap;
}
.state.g, .pill.g { background: var(--green-soft2); color: var(--green); }
.state.w, .pill.w { background: var(--amber-soft);  color: var(--amber); }
.state.b, .pill.b { background: var(--red-soft);    color: var(--red); }
.state.i, .pill.i { background: var(--surface-2);   color: var(--gray); }

/* ---------- stat grid (KPI strip) ---------- */
.stats {
  display: grid; grid-template-columns: repeat(4, 1fr);
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: var(--radius-l); box-shadow: var(--shadow-1);
  margin: 10px 0 22px 0; overflow: hidden;
}
.stats.three { grid-template-columns: repeat(3, 1fr); }
.stat { padding: 17px 18px; border-right: 1px solid var(--hairline-2); }
.stat:last-child { border-right: none; }
.stat .s-label { font-size: 11.5px; font-weight: 650; color: var(--gray); }
.stat .s-value {
  margin-top: 7px; font-size: 25px; font-weight: 750; letter-spacing: -.04em;
  font-variant-numeric: tabular-nums; line-height: 1.05;
}
.stat .s-value.pos { color: var(--green); }
.stat .s-value.neg { color: var(--red); }
.stat .s-note { margin-top: 5px; font-size: 11.5px; color: var(--gray2); line-height: 1.4; }

/* ---------- spec rows (labelled key/value cards) ---------- */
.spec { display: block; }
.spec-row {
  display: grid; grid-template-columns: 180px 1fr auto; gap: 18px; align-items: start;
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: var(--radius-m); padding: 14px 16px; margin: 9px 0; box-shadow: var(--shadow-1);
}
.spec-key { font-size: 12.5px; font-weight: 650; color: var(--gray); padding-top: 1px; }
.spec-val { font-size: 14px; color: var(--ink2); line-height: 1.6; font-variant-numeric: tabular-nums; }
.spec-val b { color: var(--ink); font-weight: 700; }

/* ---------- list lines ---------- */
.line {
  display: flex; gap: 11px; padding: 11px 2px; border-bottom: 1px solid var(--hairline-2);
  font-size: 14px; color: var(--ink2); line-height: 1.6; align-items: baseline;
}
.line:last-child { border-bottom: none; }
.line b { color: var(--ink); font-weight: 700; }

/* ---------- meter (gauge motif) ---------- */
.meter {
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: var(--radius-m); padding: 14px 16px; margin: 9px 0; box-shadow: var(--shadow-1);
}
.meter .m-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px; }
.meter .m-label { font-size: 13px; color: var(--ink2); font-weight: 650; }
.meter .m-right { display: flex; gap: 10px; align-items: center; }
.meter .m-num { font-size: 15px; font-weight: 720; font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
.meter .m-num.g { color: var(--green); } .meter .m-num.w { color: var(--amber); }
.meter .m-num.b { color: var(--red); }   .meter .m-num.i { color: var(--ink); }
.meter .m-track { height: 6px; border-radius: 999px; background: var(--surface-2); overflow: hidden; }
.meter .m-fill  { height: 100%; border-radius: 999px; transition: width .4s cubic-bezier(.2,.7,.2,1); }

/* ---------- empty / quiet states ---------- */
.quiet {
  border: 1px dashed var(--hairline); border-radius: var(--radius-l);
  padding: 50px 24px; text-align: center; background: var(--surface-3);
}
.quiet .q-title { font-size: 16px; font-weight: 700; }
.quiet .q-body  { margin-top: 9px; font-size: 13.5px; color: var(--gray); line-height: 1.65; }

/* ---------- portfolio + activity cards ---------- */
.pf-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; margin: 10px 0 20px 0; }
.pf-card {
  border: 1px solid var(--hairline); border-radius: var(--radius-l);
  padding: 19px 20px; background: var(--surface); box-shadow: var(--shadow-1);
}
.pf-card-head { display:flex; justify-content:space-between; gap:14px; align-items:flex-start; margin-bottom: 14px; }
.pf-title { font-size: 15px; font-weight: 700; letter-spacing: -.018em; line-height: 1.35; }
.pf-sub   { margin-top: 5px; font-size: 12.5px; color: var(--gray); line-height: 1.45; }
.pf-big   { font-size: 29px; font-weight: 760; letter-spacing: -.04em; font-variant-numeric: tabular-nums; margin: 2px 0; }
.pf-big.pos { color: var(--green); } .pf-big.neg { color: var(--red); }
.pf-metrics { display:grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin: 14px 0; }
.pf-metric { border-top: 1px solid var(--hairline); padding-top: 10px; min-width: 0; }
.pf-metric .k { font-size: 11px; color: var(--gray); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pf-metric .v { margin-top: 4px; font-size: 14px; font-weight: 700; color: var(--ink2); font-variant-numeric: tabular-nums; }
.pf-note { font-size: 12.5px; line-height: 1.6; color: var(--ink2); padding-top: 12px; border-top: 1px solid var(--hairline); }

.trade-grid { display:grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin: 10px 0 16px 0; }
.trade-card { border: 1px solid var(--hairline); border-radius: var(--radius-m); padding: 16px; background: var(--surface); box-shadow: var(--shadow-1); }
.trade-card .k { font-size: 11.5px; color: var(--gray); }
.trade-card .v { margin-top: 6px; font-size: 23px; font-weight: 750; letter-spacing: -.035em; font-variant-numeric: tabular-nums; }
.trade-insight { border-top: 1px solid var(--hairline-2); padding: 12px 2px; font-size: 14px; line-height: 1.6; color: var(--ink2); }
.trade-insight:first-child { border-top: none; }

/* ---------- profile hero (P&L summary) ---------- */
.profile-hero {
  border: 1px solid var(--hairline); border-radius: var(--radius-l);
  padding: 22px 24px; background: var(--surface); box-shadow: var(--shadow-2); margin: 12px 0 22px 0;
}
.profile-hero-head { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; margin-bottom: 18px; }
.profile-hero .title { font-size: 17px; font-weight: 760; letter-spacing: -.02em; }
.profile-hero .sub   { margin-top: 6px; font-size: 12.5px; color: var(--gray); line-height: 1.5; }
.profile-grid { display:grid; grid-template-columns: repeat(4,1fr); gap: 14px 12px; }
.profile-cell { border-top: 1px solid var(--hairline); padding-top: 12px; min-width: 0; }
.profile-cell .k { font-size: 11px; color: var(--gray); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.profile-cell .v { margin-top: 6px; font-size: 20px; font-weight: 760; letter-spacing: -.035em; font-variant-numeric: tabular-nums; }
.profile-cell .v.pos { color: var(--green); } .profile-cell .v.neg { color: var(--red); }

/* ---------- market cards ---------- */
.market-grid { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; margin: 10px 0 20px 0; }
.market-card { border: 1px solid var(--hairline); border-radius: var(--radius-l); padding: 18px 20px; background: var(--surface); box-shadow: var(--shadow-1); margin-bottom: 12px; }
.market-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom: 12px; }
.market-title { font-size: 15px; font-weight: 720; line-height: 1.35; letter-spacing: -.018em; }
.market-sub { margin-top: 5px; font-size: 12.5px; color: var(--gray); line-height: 1.45; }
.market-price { font-size: 28px; font-weight: 760; letter-spacing: -.04em; font-variant-numeric: tabular-nums; }
.market-metrics { display:grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-top: 12px; }
.market-metric { border-top: 1px solid var(--hairline); padding-top: 10px; min-width:0; }
.market-metric .k { font-size: 11px; color: var(--gray); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.market-metric .v { margin-top: 4px; font-size: 13.5px; font-weight: 700; color: var(--ink2); font-variant-numeric: tabular-nums; }
.market-note { font-size: 12.5px; color: var(--gray); line-height: 1.55; margin-top: 10px; }

/* ---------- AI report cards ---------- */
.ai-report-grid { display:grid; grid-template-columns: repeat(2,1fr); gap: 14px; margin-top: 12px; }
.ai-report-card { border: 1px solid var(--hairline); border-radius: var(--radius-m); padding: 16px; background: var(--surface); box-shadow: var(--shadow-1); }
.ai-report-card .a-key { font-size: 11px; font-weight: 750; color: var(--gray); letter-spacing: .07em; text-transform: uppercase; }
.ai-report-card .a-body { margin-top: 8px; font-size: 14px; line-height: 1.65; color: var(--ink2); }

.rc-grid { display:grid; grid-template-columns: repeat(2,1fr); gap: 14px; margin-top: 12px; }
.rc-card, .rc-action {
  border: 1px solid var(--hairline); border-radius: var(--radius-m);
  padding: 16px 17px; background: var(--surface); box-shadow: var(--shadow-1); margin-top: 12px;
}
.rc-action { background: var(--accent-soft); border-color: #dfe3fd; }
.rc-h { font-size: 11px; font-weight: 750; color: var(--gray); letter-spacing:.07em; text-transform: uppercase; margin-bottom: 8px; }
.rc-row { display:flex; justify-content:space-between; gap: 14px; border-top: 1px solid var(--hairline-2); padding: 9px 0; font-size: 13.5px; }
.rc-row:first-of-type { border-top: none; }
.rc-k { color: var(--gray); flex: 0 0 36%; }
.rc-v { color: var(--ink2); text-align:right; flex:1; font-variant-numeric: tabular-nums; }
.rc-v b { color: var(--ink); }
.rc-note { font-size: 14px; line-height: 1.7; color: var(--ink2); }
.rc-missing {
  margin-top: 12px; border: 1px dashed var(--hairline); border-radius: var(--radius-m);
  padding: 15px 16px; color: var(--gray); font-size: 13px; line-height: 1.7; background: var(--surface-3);
}
.rc-missing .rc-h { color: var(--gray); }

.ai-block { border-top: 1px solid var(--hairline-2); padding: 15px 0; }
.ai-block .a-key { font-size: 11px; font-weight: 700; color: var(--gray); letter-spacing: .07em; text-transform: uppercase; }
.ai-block .a-body { margin-top: 7px; font-size: 14.5px; color: var(--ink2); line-height: 1.7; }

.footnote { font-size: 11.5px; color: var(--gray2); line-height: 1.6; margin-top: 10px; }
.ob-step { font-size: 12px; font-weight: 650; color: var(--accent); letter-spacing: .06em; text-transform: uppercase; margin-bottom: 6px; }

/* legacy card/metric helpers kept for compatibility */
.card, .card-lead, .pos-card {
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: var(--radius-l); box-shadow: var(--shadow-1); padding: 18px 20px; margin: 12px 0;
}
.card-lead { padding: 22px 24px; }
.card-title { font-size: 13px; font-weight: 650; color: var(--gray); margin-bottom: 8px; }
.card-value { font-size: 33px; font-weight: 760; letter-spacing: -.045em; font-variant-numeric: tabular-nums; }
.card-sub { font-size: 13px; color: var(--gray); line-height: 1.55; margin-top: 5px; }
.muted { color: var(--gray2) !important; font-size: 12px !important; }
.metric { display:flex; flex-direction:column; gap: 5px; }
.metric .metric-label, .metric-label { font-size: 12px; color: var(--gray); font-weight: 600; }
.metric .metric-value, .metric-value { font-size: 24px; color: var(--ink); font-weight: 750; letter-spacing: -.03em; font-variant-numeric: tabular-nums; }
.metric-lg .metric-value, .metric-value-lg { font-size: 33px; font-weight: 760; letter-spacing: -.045em; }
.metric-sub { font-size: 12px; color: var(--gray2); }

/* ---------- Streamlit inputs ---------- */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea {
  background: var(--surface) !important; border: 1px solid var(--hairline) !important;
  border-radius: 13px !important; color: var(--ink) !important;
  font-size: 15px !important; font-weight: 480 !important; min-height: 44px;
  box-shadow: var(--shadow-1) !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 4px rgba(59,78,240,.12) !important;
}
div[data-baseweb="select"] > div {
  background: var(--surface) !important; border: 1px solid var(--hairline) !important;
  border-radius: 13px !important; color: var(--ink) !important; min-height: 44px; box-shadow: var(--shadow-1) !important;
}
div[data-testid="stNumberInput"] button { background: transparent !important; border: none !important; color: var(--gray) !important; }
div[data-testid="stWidgetLabel"] p { font-size: 12.5px !important; font-weight: 600 !important; color: var(--ink2) !important; }

.stButton > button, .stFormSubmitButton > button {
  background: var(--accent) !important; color: #fff !important;
  border: none !important; border-radius: 12px !important;
  font-size: 14.5px !important; font-weight: 680 !important;
  min-height: 45px; box-shadow: none !important; transition: background .16s ease, transform .12s ease !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover { background: var(--accent-press) !important; color:#fff !important; transform: translateY(-1px); }
div[data-testid="stDownloadButton"] > button {
  background: var(--surface-2) !important; color: var(--ink) !important;
  border: 1px solid var(--hairline) !important; border-radius: 12px !important; font-weight: 650 !important;
}
div[data-testid="stDownloadButton"] > button:hover { background: #eceef1 !important; }

/* ---------- tabs ---------- */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--surface-2); border-radius: 13px; padding: 4px; gap: 2px;
  border: 1px solid var(--hairline); display: inline-flex; width: auto; flex-wrap: wrap;
}
div[data-testid="stTabs"] [data-baseweb="tab"] { border-radius: 10px !important; padding: 7px 15px !important; background: transparent !important; border: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] p { font-size: 13.5px !important; font-weight: 620 !important; color: var(--gray) !important; }
div[data-testid="stTabs"] [aria-selected="true"] { background: var(--surface) !important; box-shadow: var(--shadow-1) !important; }
div[data-testid="stTabs"] [aria-selected="true"] p { color: var(--ink) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"], div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

div[data-testid="stRadio"] > div { gap: 4px; }
div[data-testid="stRadio"] label p { font-size: 13.5px !important; color: var(--ink2) !important; }

div[data-testid="stExpander"] {
  border: 1px solid var(--hairline) !important; border-radius: var(--radius-m) !important;
  background: var(--surface) !important; box-shadow: var(--shadow-1) !important; overflow: hidden;
}
div[data-testid="stExpander"] summary { padding: 13px 16px !important; align-items: center !important; }
div[data-testid="stExpander"] summary p { font-size: 13.5px !important; font-weight: 650 !important; }

div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
  border: 1px solid var(--hairline) !important; border-radius: var(--radius-m); overflow: hidden;
}

code, pre {
  background: var(--surface-2) !important; border: 1px solid var(--hairline) !important;
  border-radius: 11px !important; color: var(--ink2) !important; font-size: 12.5px !important;
  font-family: var(--mono) !important; white-space: pre-wrap !important;
}
hr { border: none; border-top: 1px solid var(--hairline); margin: 24px 0; }

/* ---------- responsive ---------- */
@media (max-width: 900px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 3rem !important; }
  .stats, .stats.three { grid-template-columns: repeat(2,1fr); }
  .pf-grid, .market-grid, .ai-report-grid, .rc-grid { grid-template-columns: 1fr; }
  .pf-metrics { grid-template-columns: repeat(2,1fr); }
  .trade-grid { grid-template-columns: repeat(2,1fr); }
  .profile-grid { grid-template-columns: repeat(2,1fr); }
  .spec-row { grid-template-columns: 1fr; gap: 7px; }
  .verdict .v-title { font-size: 27px; }
  .headline { font-size: 25px; }
}
@media (max-width: 560px) {
  .stats, .stats.three, .trade-grid, .profile-grid { grid-template-columns: 1fr; }
  .stat { border-right: none; border-bottom: 1px solid var(--hairline-2); }
  .stat:last-child { border-bottom: none; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# State
# =====================================================
DEFAULT_PROFILE = {
    "assets": 1000.0,
    "start_capital": 1000.0,
    "start_when": "자동 시작",
    "freq": "",
    "cats": [],
    "emotional_limit": 50.0,
    "max_pct": 3.0,
    "block_pct": 12.0,
    "loss_reaction": "기본값",
}

DEFAULTS = {
    "lang": "ko",
    "profile": dict(DEFAULT_PROFILE),  # default risk profile; no onboarding gate
    "last_entry": None,
    "last_position": None,
    "trade_log": [],
    "portfolio": [],
    "cash": 0.0,
    "deposits": 0.0,          # extra deposits after start capital
    "withdrawals": 0.0,       # withdrawals taken out of wallet
    "adj_month": 0.0,          # pre-app P&L adjustments
    "adj_year": 0.0,
    "url_rows": [],
    "explore_markets": [],
    "explore_raw": [],
    "explore_url": "https://polymarket.com/event/",
    "_explorer_active": "",
    "prefill_entry": {},
    "entry_url": "",
    "entry_markets": [],
    "entry_raw": {},
    "ai_extra_context": "",
    "_entry_active": "",
    "_entry_sel": None,
    "explore_ai_text": "", "explore_ai_error": "", "explore_ai_prompt": "", "explore_ai_pair": "",
    "ai_text": "", "ai_error": "", "ai_prompt": "", "ai_pair": "",
    "wallet_raw": [],
    "activity_raw": [],
    "auto_trades": [],
    "wallet_addr": "",
    "imported_tx_ids": [],
    "trade_qf": "all",
    "trade_qf_select": "all",
    "trade_start_date": None,
    "trade_end_date": None,
    "watchlist": [],
    "watching_market": {},
    "live_price_cache": {},
    "price_history_cache": {},
    "order_candidates": [],
    "explore_book_raw": {},
    "explore_history_raw": {},
    "habit_cache": {},
    "pnl_raw": {},
    "profile_pnl": {},
    "ai_pending": {},
    "ai_report_cache": {},
    "ai_last_market_key": "",
    "ai_report_mode": "standard",
    "_ai_memo_cache": "",
    "_ai_bk_cache": "",
    "dev_mode": False,
    "reviews": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def t(ko, en):
    return ko if st.session_state.lang == "ko" else en


def profile():
    p = st.session_state.profile
    if isinstance(p, dict) and p:
        merged = dict(DEFAULT_PROFILE)
        merged.update(p)
        return merged
    st.session_state.profile = dict(DEFAULT_PROFILE)
    return dict(DEFAULT_PROFILE)


# =====================================================
# Utility
# =====================================================
def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def money(v):
    return f"-${abs(v):,.2f}" if v < 0 else f"${v:,.2f}"

def signed_money(v):
    return f"+${v:,.2f}" if v >= 0 else f"-${abs(v):,.2f}"

def signed_pct(v):
    return f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"

def cents(v):
    return f"{v:.1f}¢"

def stat(label, value, note="", tone=""):
    cls = " pos" if tone == "pos" else " neg" if tone == "neg" else ""
    return f"""<div class="stat"><div class="s-label">{label}</div><div class="s-value{cls}">{value}</div><div class="s-note">{note}</div></div>"""

def spec_row(key, val, state_text="", kind="i"):
    s = f'<span class="state {kind}">{state_text}</span>' if state_text else ""
    return f"""<div class="spec-row"><div class="spec-key">{key}</div><div class="spec-val">{val}</div><div>{s}</div></div>"""

def meter(label, value, kind, verdict, max_v=100, unit=""):
    """Meter with explicit colored verdict pill so good/bad is obvious."""
    color = {"g": "var(--green)", "w": "var(--amber)", "b": "var(--red)", "i": "var(--ink)"}.get(kind, "var(--ink)")
    width = clamp(value / max_v * 100 if max_v else 0)
    return f"""<div class="meter">
<div class="m-row">
  <span class="m-label">{label}</span>
  <span class="m-right"><span class="m-num {kind}">{value:.1f}{unit}</span><span class="state {kind}">{verdict}</span></span>
</div>
<div class="m-track"><div class="m-fill" style="width:{width:.1f}%;background:{color};"></div></div>
</div>"""

def line(text, kind="i"):
    return f'<div class="line"><span class="dot {kind}"></span><span>{text}</span></div>'

def verdict_dot(level):
    return {"good": "g", "warn": "w", "bad": "b"}.get(level, "i")

def grade_word(kind):
    return {"g": t("좋음", "Good"), "w": t("주의", "Caution"), "b": t("위험", "Risk"), "i": t("보통", "Neutral")}[kind]

def esc(v):
    return html.escape(str(v or ""), quote=True)


# =====================================================
# Rules — thresholds come from the user's profile
# =====================================================
def price_zone(price):
    if price >= 99: return t("99¢ 매수 금지", "Do not buy at 99¢"), "b", -32, t("99¢는 사는 가격이 아니라 파는 가격입니다.", "99¢ is a selling price, not a buying price.")
    if price >= 95: return t("상환 스캘핑", "Redemption scalping"), "b", -24, t("95~98¢는 거의 상환 스캘핑입니다. 고액 신규 매수 금지에 가깝습니다.", "95–98¢ is near-redemption scalping. Avoid large new buys.")
    if price >= 90: return t("신규매수 비추천", "New buys discouraged"), "b", -18, t("90~95¢는 신규 매수 비추천 구간입니다.", "90–95¢ is a discouraged range for new buys.")
    if price >= 85: return t("매우 신중", "Be very cautious"), "w", -10, t("85~90¢는 신규 진입을 매우 신중하게 봐야 합니다.", "85–90¢ requires extra caution.")
    if price >= 80: return t("익절 고려", "Take-profit zone"), "w", -6, t("80~85¢는 신규 매수보다 익절 고려 구간입니다.", "80–85¢ favors taking profit over new buys.")
    if 2 <= price <= 5: return t("초저가 Bounce", "Deep-value bounce"), "w", -12, t("2~5¢ Bounce Trade는 소액 전용입니다.", "2–5¢ bounce trades are small-size only.")
    if price < 2: return t("복권형", "Lottery ticket"), "b", -20, t("2¢ 미만은 거의 복권형 가격입니다.", "Below 2¢ is essentially a lottery ticket.")
    if price <= 20: return t("고변동", "High volatility"), "w", -4, t("저가 구간은 변동성이 큽니다. 소액만 적합합니다.", "Low prices are volatile. Small size only.")
    return t("정상 구간", "Normal range"), "g", 0, t("가격 구간 자체는 과도한 위험 신호가 크지 않습니다.", "No major risk signal from price alone.")

def purpose_options():
    return [t("경기승리 / 만기 보유", "Win bet / hold to expiry"),
            t("경기 시작 전 가격 상승 노림", "Pre-game price rise"),
            t("반반 경기 쏠림 이용 / 중간 익절", "Crowd-tilt / mid take-profit"),
            t("역배 / Bounce Trade", "Underdog / bounce trade"),
            t("99¢ 상환 스캘핑", "99¢ redemption scalp"),
            t("뉴스/이벤트 선반영", "News/event front-run")]

def purpose_rule(p):
    table = [
        (1.00, 0,  t("실제 승률 추정이 핵심인 기본 승리 베팅입니다.", "Standard win bet; true win-rate matters most.")),
        (0.70, -6, t("시장 심리와 타이밍이 중요합니다. 익절 기준을 먼저 정해야 합니다.", "Sentiment & timing; set a take-profit rule first.")),
        (0.60, -8, t("경기력이 아니라 시장 쏠림을 노리는 거래입니다.", "Targets crowd tilt, not team strength.")),
        (0.35, -13, t("역배와 bounce는 소액 전용입니다. 손실 제한이 핵심입니다.", "Underdog/bounce is small-size only.")),
        (0.20, -25, t("작은 수익을 위해 큰 금액을 위험에 노출하는 구조입니다.", "Risks a lot for very little.")),
        (0.50, -12, t("조건문과 resolution 기준 확인이 중요합니다.", "Check resolution criteria carefully.")),
    ]
    opts = purpose_options()
    try: return table[opts.index(p)]
    except ValueError: return (1.0, 0, t("일반 베팅으로 계산합니다.", "Calculated as a standard bet."))

def market_type_options():
    return ["Match Moneyline", "Game Winner", "Correct Score",
            t("정치 선거", "Political election"), t("뉴스/이벤트", "News / event"),
            t("99¢ 상환 스캘핑", "99¢ redemption scalp"), "2~5¢ Bounce Trade"]

def market_type_rule(m):
    table = [
        (1.00, 0,  t("가장 기본적인 시장입니다.", "The most standard market.")),
        (0.50, -10, t("단판 시장은 변동성이 커서 추천 금액을 50% 줄입니다.", "Single-game markets cut suggested size by 50%.")),
        (0.25, -25, t("Correct Score는 맞히기 어렵습니다.", "Correct Score is hard to hit.")),
        (0.50, -12, t("결과 기준과 이의제기 가능성을 확인해야 합니다.", "Verify result criteria & dispute risk.")),
        (0.50, -12, t("조건문과 resolution 기준 확인이 필수입니다.", "Resolution wording check is mandatory.")),
        (0.20, -25, t("고가 상환 스캘핑은 고액 금지입니다.", "No large size for redemption scalps.")),
        (0.20, -18, t("초저가 bounce는 소액 전용입니다.", "Deep-value bounce is small-size only.")),
    ]
    opts = market_type_options()
    try: return table[opts.index(m)]
    except ValueError: return (1.0, 0, t("일반 시장으로 계산합니다.", "Standard market."))

def size_thresholds():
    p = profile()
    g = max(p["max_pct"], 0.5)
    return g, g * 1.5, g * 2.5, max(p["block_pct"], g * 1.6)

def size_rule(pct):
    g, c1, c2, blk = size_thresholds()
    if pct >= 50: return t("시스템 실패", "System failure"), "b", -100, t("계좌 생존 리스크입니다. 50% 이상 노출은 절대 금지입니다.", "Account-survival risk. Never expose 50%+.")
    if pct >= blk: return t("진입 금지", "Entry blocked"), "b", -85, t(f"내 기준 진입 금지선({blk:.0f}%)을 넘었습니다.", f"Above your no-entry line ({blk:.0f}%).")
    if pct >= c2: return t("매우 위험", "Very risky"), "b", -38, t(f"내 적정 비율({g:.0f}%)의 2.5배가 넘는 포지션입니다.", f"Over 2.5× your comfort ratio ({g:.0f}%).")
    if pct >= c1: return t("위험", "Risky"), "w", -20, t(f"내 적정 비율({g:.0f}%)을 크게 넘었습니다.", f"Well above your comfort ratio ({g:.0f}%).")
    if pct > g: return t("주의", "Caution"), "w", -8, t(f"내 적정 비율({g:.0f}%)을 약간 넘었습니다.", f"Slightly above your comfort ratio ({g:.0f}%).")
    return t("정상", "Normal"), "g", 5, t(f"내 적정 비율({g:.0f}%) 이내입니다.", f"Within your comfort ratio ({g:.0f}%).")

def exposure_rule(pct):
    g, c1, c2, blk = size_thresholds()
    if pct >= blk: return t("중복 노출 금지", "Stacked exposure blocked"), "b", -60, t(f"같은 경기·방향 총 노출이 진입 금지선({blk:.0f}%)을 넘었습니다.", f"Same-game/side exposure above your no-entry line ({blk:.0f}%).")
    if pct >= c2: return t("중복 노출 위험", "Stacked exposure risky"), "b", -35, t("같은 경기·방향 총 노출이 큽니다.", "Stacked exposure is large.")
    if pct >= c1: return t("중복 노출 주의", "Stacked exposure caution"), "w", -12, t("같은 경기·방향 노출이 쌓이고 있습니다.", "Exposure is stacking up.")
    return t("정상", "Normal"), "g", 0, t("중복 노출은 관리 가능한 범위입니다.", "Stacked exposure is manageable.")

def confidence_options():
    return [t("관찰용", "Watching"), t("낮은 확신", "Low conviction"), t("중간 확신", "Medium"),
            t("높은 확신", "High conviction"), t("초고확신", "Very high")]

def confidence_caps():
    el = profile()["emotional_limit"]
    return [el * .3, el * .5, el * 1.0, el * 1.4, el * 1.4]

def portfolio_caps(bankroll):
    g = profile()["max_pct"] / 100
    return [bankroll * g * .3, bankroll * g * .5, bankroll * g * 1.0, bankroll * g * 1.3, bankroll * g * 1.5]


def effective_bankroll():
    pos_value = sum((p.get("shares", 0) or 0) * ((p.get("cur", 0) or 0) / 100) for p in st.session_state.portfolio)
    total = st.session_state.cash + pos_value
    return total if total > 0 else profile()["assets"]


# =====================================================
# Entry engine
# =====================================================
def calculate_entry(d):
    prof = profile()
    current_price, fair_price = d["current_price"], d["fair_price"]
    stake, bankroll = d["stake"], d["bankroll"]
    edge = fair_price - current_price
    position_pct = stake / bankroll * 100 if bankroll else 0

    zone_label, zone_kind, zone_pen, zone_note = price_zone(current_price)
    p_mult, p_pen, p_note = purpose_rule(d["purpose"])
    m_mult, m_pen, m_note = market_type_rule(d["market_type"])
    size_label, size_kind, size_pen, size_note = size_rule(position_pct)

    el = prof["emotional_limit"]
    try:
        ci = confidence_options().index(d["confidence"])
    except ValueError:
        ci = 2
    base_cap = min(confidence_caps()[ci], portfolio_caps(bankroll)[ci], el)
    rec_cap = base_cap * p_mult * m_mult
    if d["fomo_count"] >= 1:
        rec_cap *= 0.5

    sys_amt, warn_amt = el * 4, el * 2
    if stake >= sys_amt: cap_label, cap_kind, cap_pen = t(f"감정 한도 4배 초과 — 시스템 실패", "4× emotional cap — system failure"), "b", -90
    elif stake >= warn_amt: cap_label, cap_kind, cap_pen = t(f"감정 한도 2배 초과 — 강한 경고", "2× emotional cap — strong warning"), "b", -50
    elif stake > rec_cap * 1.2: cap_label, cap_kind, cap_pen = t("추천 상한선 초과", "Above suggested cap"), "b", -32
    elif stake > rec_cap: cap_label, cap_kind, cap_pen = t("상한선 소폭 초과", "Slightly above cap"), "w", -12
    else: cap_label, cap_kind, cap_pen = t("상한선 이내", "Within cap"), "g", 0

    dup_total = d["duplicate_ml"] + d["duplicate_game"] + d["duplicate_side"] + stake
    dup_pct = dup_total / bankroll * 100 if bankroll else 0
    exp_label, exp_kind, exp_pen, exp_note = exposure_rule(dup_pct)

    if d["fomo_count"] >= 3:
        fomo_label, fomo_kind, fomo_pen = t("감정 진입 금지", "Emotional — blocked"), "b", -75
        fomo_note = t("감정 체크 3개 이상입니다. 신규 진입 금지로 봐야 합니다.", "3+ emotion checks. Treat as no-entry.")
    elif d["fomo_count"] >= 1:
        fomo_label, fomo_kind, fomo_pen = t("감정 위험", "Emotional risk"), "w", -20
        fomo_note = t("감정 체크가 있습니다. 추천 금액을 50% 줄였습니다.", "Emotion checks present. Size halved.")
    else:
        fomo_label, fomo_kind, fomo_pen = t("정상", "Normal"), "g", 0
        fomo_note = t("감정 체크가 없습니다.", "No emotion checks.")

    if d["previous_good_price"] > 0:
        gap = current_price - d["previous_good_price"]
        if gap >= 30: chase = (t("FOMO 추격", "FOMO chase"), "b", -25, t("처음 봤던 가격보다 30¢ 이상 올랐습니다.", "Up 30¢+ since first sighting."))
        elif gap >= 15: chase = (t("추격 위험", "Chase risk"), "w", -13, t("처음 봤던 가격보다 많이 올랐습니다.", "Up a lot since first sighting."))
        elif gap >= 5: chase = (t("조금 상승", "Slightly up"), "w", -5, t("처음 봤던 가격보다 조금 올랐습니다.", "Slightly up since first sighting."))
        else: chase = (t("추격 아님", "Not a chase"), "g", 5, t("추격 위험은 크지 않습니다.", "Chase risk is small."))
    else:
        chase = (t("미입력", "Not entered"), "i", 0, t("처음 봤던 저평가 가격을 입력하지 않았습니다.", "First-seen price not provided."))
    chase_label, chase_kind, chase_pen, chase_note = chase

    bk = d["bookmaker_prob"]
    my_vs_poly = fair_price - current_price
    book_vs_poly = bk - current_price if bk > 0 else 0
    my_vs_book = fair_price - bk if bk > 0 else 0
    if bk <= 0: book = (t("북메이커 미입력", "No bookmaker input"), "i", 0, t("북메이커 승률을 입력하면 공식 배당과의 괴리를 볼 수 있습니다.", "Enter a bookmaker probability to compare."))
    elif my_vs_book >= 10: book = (t("과신 재검토", "Re-check overconfidence"), "b", -12, t("내 적정가가 북메이커보다 10%p 이상 높습니다.", "Your fair price is 10pp+ above the book."))
    elif book_vs_poly >= 5: book = (t("외부배당도 저평가", "Cheap vs books too"), "g", 6, t("북메이커 기준으로도 가격이 싸 보입니다.", "Cheap even vs bookmakers."))
    elif book_vs_poly <= -5: book = (t("외부배당 기준 비쌈", "Expensive vs books"), "w", -8, t("북메이커 기준으로는 비싼 편입니다.", "Expensive vs bookmakers."))
    else: book = (t("큰 차이 없음", "No big gap"), "i", 0, t("북메이커와 큰 차이가 없습니다.", "No large gap vs books."))
    book_label, book_kind, book_pen, book_note = book

    value_score = clamp(50 + edge * 2.2 + zone_pen + p_pen + m_pen + chase_pen + book_pen)
    final_score = clamp(value_score + size_pen + exp_pen + fomo_pen + cap_pen)

    g, c1, c2, blk = size_thresholds()
    hard_stop = None
    if position_pct >= 50: hard_stop = t("시스템 실패 — 계좌 생존 리스크", "System failure — survival risk")
    elif stake >= sys_amt: hard_stop = t("시스템 실패 — 감정 한도 4배", "System failure — 4× emotional cap")
    elif position_pct >= blk: hard_stop = t(f"진입 금지 — 내 한도 {blk:.0f}% 초과", f"Entry blocked — over your {blk:.0f}% line")
    elif dup_pct >= blk: hard_stop = t(f"진입 금지 — 중복 노출 {blk:.0f}% 초과", f"Entry blocked — stacked over {blk:.0f}%")
    elif d["fomo_count"] >= 3: hard_stop = t("진입 금지 — 감정 배팅 위험", "Entry blocked — emotional betting")

    if hard_stop: decision, level = hard_stop, "bad"
    elif final_score >= 75: decision, level = t("진입 적절", "Good entry"), "good"
    elif final_score >= 60: decision, level = t("소액 진입 가능", "Small entry OK"), "warn"
    elif final_score >= 45: decision, level = t("관망 우선", "Wait and watch"), "warn"
    else: decision, level = t("진입 부적절", "Poor entry"), "bad"

    shares = stake / (current_price / 100)
    win_profit = shares - stake
    target_profit = shares * (d["target_price"] / 100) - stake
    stop_loss_amt = stake - shares * (d["stop_price"] / 100)
    rr = target_profit / stop_loss_amt if stop_loss_amt > 0 else 0

    if target_profit > 0 and stop_loss_amt > 0:
        if stop_loss_amt > target_profit: rr_text, rr_kind = t(f"손절 손실이 목표 수익보다 약 {stop_loss_amt/target_profit:.1f}배 큽니다.", f"Stop-loss ≈ {stop_loss_amt/target_profit:.1f}× the target."), "b"
        elif target_profit >= stop_loss_amt * 1.5: rr_text, rr_kind = t(f"목표 수익이 손절 손실보다 약 {target_profit/stop_loss_amt:.1f}배 큽니다.", f"Target ≈ {target_profit/stop_loss_amt:.1f}× the stop."), "g"
        else: rr_text, rr_kind = t(f"손익비 {rr:.2f}:1 — 큰 우위는 아닙니다.", f"R:R {rr:.2f}:1 — not a big edge."), "w"
    else:
        rr_text, rr_kind = t("목표가 또는 손절가를 다시 확인하세요.", "Re-check target or stop."), "w"

    current_value = shares * (current_price / 100)
    additional_to_100 = shares - current_value
    high_warn = ""
    if current_price >= 90:
        high_warn = t(f"현재부터 100¢까지 추가수익은 {money(additional_to_100)}뿐입니다. 틀리면 {money(current_value)}를 잃을 수 있습니다.",
                      f"Only {money(additional_to_100)} left to 100¢, but a miss costs {money(current_value)}.")
    if current_price >= 97:
        high_warn += t(" 97~99¢ 고액 매수는 작은 수익을 위해 큰 금액을 위험에 노출합니다.", " Large buys at 97–99¢ risk a lot for little.")

    if edge >= 10: edge_reason = ("g", t(f"가격 메리트 좋음 — 적정가가 현재가보다 {edge:.1f}¢ 높습니다.", f"Good value — fair price {edge:.1f}¢ above market."))
    elif edge >= 5: edge_reason = ("w", t(f"가격 메리트 약간 — edge {edge:.1f}¢.", f"Some value — edge {edge:.1f}¢."))
    elif edge < 0: edge_reason = ("b", t(f"가격 메리트 없음 — 현재가가 {abs(edge):.1f}¢ 더 비쌉니다.", f"No value — market {abs(edge):.1f}¢ above fair."))
    else: edge_reason = ("w", t(f"가격 메리트 작음 — edge {edge:.1f}¢.", f"Thin value — edge {edge:.1f}¢."))

    reasons = [edge_reason,
               (size_kind, t(f"포지션 크기 — 총자산의 {position_pct:.1f}% · {size_label}", f"Size — {position_pct:.1f}% of portfolio · {size_label}")),
               (cap_kind, t(f"추천 상한선 {money(rec_cap)} · 투자금 {money(stake)} — {cap_label}", f"Cap {money(rec_cap)} · stake {money(stake)} — {cap_label}")),
               (zone_kind, t(f"가격 구간 — {zone_label}. {zone_note}", f"Price zone — {zone_label}. {zone_note}"))]

    return {**d, "edge": edge, "position_pct": position_pct,
            "duplicate_total": dup_total, "duplicate_pct": dup_pct, "rec_cap": rec_cap,
            "value_score": round(value_score, 1), "final_score": round(final_score, 1),
            "decision": decision, "level": level, "shares": shares,
            "win_profit": win_profit, "target_profit": target_profit,
            "stop_loss_amt": stop_loss_amt, "rr": rr, "rr_text": rr_text, "rr_kind": rr_kind,
            "current_value": current_value, "additional_to_100": additional_to_100,
            "high_warn": high_warn,
            "zone_label": zone_label, "zone_kind": zone_kind, "zone_note": zone_note,
            "purpose_note": p_note, "market_type_note": m_note,
            "size_label": size_label, "size_kind": size_kind, "size_note": size_note,
            "cap_label": cap_label, "cap_kind": cap_kind,
            "exp_label": exp_label, "exp_kind": exp_kind, "exp_note": exp_note,
            "fomo_label": fomo_label, "fomo_kind": fomo_kind, "fomo_note": fomo_note,
            "chase_label": chase_label, "chase_kind": chase_kind, "chase_note": chase_note,
            "book_label": book_label, "book_kind": book_kind, "book_note": book_note,
            "my_vs_poly": my_vs_poly, "book_vs_poly": book_vs_poly, "my_vs_book": my_vs_book,
            "reasons": reasons}


# =====================================================
# Position engine
# =====================================================
def evaluate_position(d):
    cp, shares, inv, bankroll = d["current_price"], d["shares"], d["investment"], d["bankroll"]
    current_value = shares * (cp / 100)
    pnl = current_value - inv
    roi = pnl / inv * 100 if inv else 0
    position_pct = current_value / bankroll * 100 if bankroll else 0
    g, c1, c2, blk = size_thresholds()

    reasons, warnings = [], []
    if cp >= d["target_price"]:
        decision, level = t("목표가 도달 — 매도·부분매도 고려", "Target hit — consider selling"), "warn"
        reasons.append(t("목표가에 도달했습니다. 일부 익절을 검토할 구간입니다.", "Target reached. Consider partial profit."))
    elif cp <= d["stop_price"] and current_value >= inv * 0.3:
        decision, level = t("손절 고려", "Consider stop-loss"), "bad"
        reasons.append(t("손절가 이하이고 회수 가능한 금액이 남아 있습니다.", "Below stop; meaningful value recoverable."))
    elif current_value <= inv * 0.1:
        decision, level = t("손절 효용 낮음 — 추가매수 금지", "Stop has little value — no adding"), "warn"
        reasons.append(t("평가금이 원금의 10% 이하입니다. 옵션처럼 보유, 추가매수 금지.", "Under 10% of cost. Hold like an option; never add."))
    else:
        decision, level = t("홀딩 가능", "Holding is fine"), "good"
        reasons.append(t("목표가와 손절가 사이로 홀딩 조건을 충족합니다.", "Between target and stop; hold conditions met."))

    if roi >= 30:
        warnings.append(t("수익률 +30% 이상 — 원금 회수 또는 부분매도 검토.", "ROI +30%+ — consider recovering principal."))
        if level == "good":
            decision, level = t("홀딩 가능, 단 부분매도 검토", "Hold, but consider partial sell"), "warn"
    if position_pct >= blk:
        warnings.append(t(f"포트폴리오 비중이 내 진입 금지선({blk:.0f}%)을 넘었습니다 — 즉시 축소 고려.", f"Over your no-entry line ({blk:.0f}%) — reduce now."))
        decision, level = t("과대 노출 — 즉시 축소 고려", "Excessive exposure — reduce now"), "bad"
    elif position_pct >= c1:
        warnings.append(t(f"포트폴리오 비중이 적정선({g:.0f}%)을 크게 넘었습니다 — 일부 축소 권장.", f"Well above your comfort ratio ({g:.0f}%) — partial reduction advised."))
        if level != "bad":
            decision, level = t("홀딩 가능, 단 포지션 크기 과대", "Hold, but size too large"), "warn"
    if d["fomo_count"] >= 3:
        warnings.append(t("감정 체크 3개 이상 — 추가매수 금지, 축소 우선.", "3+ emotion checks — no adding; reduce first."))
        decision, level = t("감정 리스크 — 추가매수 금지", "Emotional risk — no adding"), "bad"
    elif d["fomo_count"] >= 1:
        warnings.append(t("감정 체크 있음 — 섣부른 추가매수 주의.", "Emotion present — avoid impulsive adds."))

    zl, zk, _, zn = price_zone(cp)
    if cp >= 80:
        warnings.append(zn)
    if not warnings:
        warnings.append(t("큰 위험 신호는 없지만 목표가·손절가 기준은 유지하세요.", "No major risk, but keep target/stop rules."))

    return {**d, "decision": decision, "level": level, "current_value": current_value,
            "pnl": pnl, "roi": roi, "position_pct": position_pct,
            "additional": shares - current_value, "reasons": reasons, "warnings": warnings}


def partial_rows(shares, price_cent, investment):
    pdec = price_cent / 100
    rows, need = [], None
    if shares > 0 and pdec > 0:
        need = investment / (shares * pdec) * 100
    for ratio in [25, 50, 70, 80, 90, 100]:
        ss = shares * ratio / 100
        rec = ss * pdec
        rem = shares - ss
        rows.append({
            t("매도 비율", "Sell %"): f"{ratio}%",
            t("매도 수량", "Shares sold"): round(ss, 2),
            t("회수금", "Recovered"): money(rec),
            t("원금 대비 확정손익", "Locked P&L"): signed_money(rec - investment),
            t("남은 수량", "Shares left"): round(rem, 2),
            t("남은 평가금", "Remaining value"): money(rem * pdec),
            t("100¢ 추가수익", "Extra at 100¢"): signed_money(rem * (1 - pdec)),
        })
    return rows, need


# =====================================================
# Claude AI
# =====================================================
def get_api_key():
    """Read Anthropic key safely from Streamlit secrets or local env. Never hard-code the key in app.py."""
    candidates = []
    try:
        candidates.append(st.secrets.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        pass
    try:
        candidates.append(st.secrets.get("anthropic", {}).get("api_key", ""))
    except Exception:
        pass
    try:
        candidates.append(st.secrets.get("anthropic", {}).get("ANTHROPIC_API_KEY", ""))
    except Exception:
        pass
    candidates.append(os.getenv("ANTHROPIC_API_KEY", ""))

    for k in candidates:
        k = str(k).strip().strip('"').strip("'")
        if k.startswith("sk-ant-") or k.startswith("sk-"):
            return k
    return None

def build_prompt(market_name, outcome="", current_price=0, category="기타", sub="",
                 ai_context="", bookmaker_memo="", fair_price=None, edge=None,
                 market_class="", bookmaker_prob=None, bookmaker_source_memo="",
                 ai_extra_context="", report_mode="standard", resolution="", **_ignore):
    """Research-focused JSON prompt.

    Memento's deterministic engine already owns price/risk/stake. Claude is asked
    only for the things a language model can actually do well WITHOUT live internet:
    interpret the real Polymarket resolution rules, structure the user's pasted
    research, frame the edge, and produce an honest pre-bet checklist. It must never
    fabricate records, standings, injuries, or odds; unknown facts go to missing_data.
    The schema is flat and stable so the UI always renders clean cards/tables.
    """
    lang = "ko" if st.session_state.lang == "ko" else "en"
    category = str(category or "기타")
    sub = str(sub or "")
    market_name = str(market_name or "")
    outcome = str(outcome or "")
    resolution = str(resolution or "").strip()
    try:
        current_price_f = float(current_price or 0)
    except Exception:
        current_price_f = 0.0
    try:
        fair_price_f = float(fair_price) if fair_price is not None else None
    except Exception:
        fair_price_f = None
    try:
        edge_f = float(edge) if edge is not None else (fair_price_f - current_price_f if fair_price_f is not None else None)
    except Exception:
        edge_f = None

    cat = f"{category} {sub} {market_name}".lower()
    sporty = any(k in cat for k in ("e스포츠", "esport", "스포츠", "sport", "lol", "lck", "lpl", "mlb",
                                    "baseball", "nba", "nfl", "ufc", "tennis", "soccer", "football", "valorant", "cs2", "dota"))
    if sporty:
        focus = ("Sports/esports scouting: structure the user's notes into head-to-head, recent form, "
                 "standing, roster/injuries, and the style/matchup that decides this game.")
    else:
        focus = ("Event/market analysis: settlement criteria, timing risk, official source, the catalyst "
                 "or condition that actually decides YES, and liquidity/uncertainty.")

    memo = str(ai_context or ai_extra_context or "").strip()
    bkm = str(bookmaker_memo or bookmaker_source_memo or "").strip()
    if not bkm and bookmaker_prob not in (None, "", 0, 0.0):
        try:
            bkm = f"bookmaker implied {float(bookmaker_prob):.1f}%"
        except Exception:
            bkm = str(bookmaker_prob)

    evidence_parts = []
    if memo:
        evidence_parts.append(f"USER_NOTES (your only evidence for facts):<<<{memo}>>>")
    if bkm:
        evidence_parts.append(f"BOOKMAKER_INPUT:<<<{bkm}>>>")
    if resolution:
        evidence_parts.append(f"POLYMARKET_RESOLUTION_TEXT:<<<{resolution[:1400]}>>>")
    if memo or bkm:
        basis_rule = ("Base every factual claim ONLY on USER_NOTES / BOOKMAKER_INPUT above. "
                      "Anything not stated there is unknown — write '확인 필요' and add it to missing_data.")
    else:
        basis_rule = ("No research notes were provided. Do NOT invent any records, standings, form, injuries, "
                      "or odds. Set scouting fields to '확인 필요', confidence='low', and use data_basis to tell "
                      "the user plainly that this report is a framework only until they paste research.")
    evidence = ("\n" + "\n".join(evidence_parts)) if evidence_parts else ""

    fair_txt = f"{fair_price_f:.1f}¢" if fair_price_f is not None else "확인 필요"
    edge_txt = f"{edge_f:+.1f}¢" if edge_f is not None else "확인 필요"
    implied_txt = f"{current_price_f:.0f}%" if current_price_f else "확인 필요"
    price_txt = f"{current_price_f:.1f}¢" if current_price_f else "확인 필요"
    bookmaker_txt = bkm if bkm else "확인 필요"
    res_txt = "provided above — interpret it" if resolution else "확인 필요"
    lang_line = "Write every string value in natural Korean." if lang == "ko" else "Write every string value in English."
    mode_instruction = {
        "brief":    "Compact: summary 2 items, swing_factors 2, checklist 3, one short sentence per field.",
        "standard": "Standard: summary 3 items, swing_factors 3, checklist 4, concise sentences.",
        "detailed": "Detailed: summary 3 items, swing_factors 5, checklist 5, 2-3 sentence field values where useful.",
    }.get(str(report_mode or "standard"), "Standard length.")

    market_payload = {
        "name": market_name, "outcome": outcome, "category": category, "sub": sub,
        "market_class": market_class, "polymarket_price_cents": round(current_price_f, 1),
        "polymarket_implied_pct": round(current_price_f, 1),
        "user_fair_price": fair_txt, "user_edge": edge_txt, "bookmaker_view": bookmaker_txt,
    }

    return f"""You are Memento's research analyst for Polymarket bets. You have NO live internet access. Output ONE JSON object only — no markdown, no ``` fences, no text before or after. Every value is a flat string or an array of strings.

YOUR JOB (in priority order):
1. Interpret the resolution rules and name the single biggest settlement risk (this is your most valuable output).
2. Organize the user's pasted notes into a clean scouting picture — never add facts they did not give you.
3. Frame the edge using the known numbers (price, fair, bookmaker). The app already handles stake/risk/cap, so do NOT discuss bet sizing.
4. Tell the user exactly what to verify before entering.

HARD RULES:
- {basis_rule}
- Never fabricate records, standings, recent form, injuries, line-ups, or odds.
- Be calibrated: if evidence is thin, say so and keep confidence low. No false certainty.

MARKET={json.dumps(market_payload, ensure_ascii=False)}
FOCUS: {focus}{evidence}
REPORT_MODE: {report_mode}. {mode_instruction}

Return EXACTLY this JSON shape:
{{
"report_title":"short, specific title",
"stance":"favorable|neutral|risky",
"estimated_probability":"e.g. 58% (only if notes support it, else 확인 필요)",
"confidence":"high|medium|low",
"data_basis":"one honest sentence: what this report is actually based on",
"verdict":"1-2 sentence bottom line in plain language, context-based not math",
"summary":["key point","key point"],
"scouting":{{"head_to_head":"확인 필요","recent_form":"확인 필요","standing":"확인 필요","roster_news":"확인 필요","style_matchup":"확인 필요"}},
"odds":{{"polymarket":"{price_txt}","implied":"{implied_txt}","fair":"{fair_txt}","edge":"{edge_txt}","bookmaker":"{bookmaker_txt}","read":"short read on whether it looks cheap/expensive"}},
"resolution_read":"how this market settles and the main settlement risk ({res_txt})",
"swing_factors":["the variable that most decides the outcome"],
"checklist":["a concrete thing to verify before entering"],
"missing_data":["unknown items only; [] if none"]
}}

{lang_line}
"""

def call_claude(prompt, mode="standard"):
    key = get_api_key()
    if not key:
        return None, "no_key"
    max_tokens = {"brief": 700, "standard": 1500, "detailed": 2200}.get(str(mode or "standard"), 1500)
    try:
        payload = json.dumps({"model": "claude-sonnet-4-6", "max_tokens": max_tokens,
                              "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
                                     headers={"Content-Type": "application/json", "x-api-key": key,
                                              "anthropic-version": "2023-06-01"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data["content"][0]["text"], None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "ignore")[:500]
        except Exception:
            body = ""
        return None, f"http_{e.code}: {body}"
    except Exception as e:
        return None, str(e)

def safe_json_parse(text):
    """Parse Claude JSON robustly. Returns None on failure without raising."""
    if not text:
        return None
    import re as _re
    s = str(text).strip()
    m = _re.search(r"```(?:json)?\s*(\{.*\})\s*```", s, _re.S)
    if m:
        s = m.group(1)
    a, b = s.find("{"), s.rfind("}")
    if a == -1 or b == -1 or b <= a:
        return None
    frag = s[a:b + 1]
    attempts = [
        frag,
        frag.replace("\n", " "),
        _re.sub(r",\s*}", "}", _re.sub(r",\s*]", "]", frag)),
        frag.replace("\\", ""),
    ]
    for attempt in attempts:
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


def _ai_plain_fallback(text):
    """If JSON parsing fails, still show a clean report-like card. Never expose the parse failure."""
    import re as _re
    s = str(text or "")
    s = _re.sub(r"```.*?```", " ", s, flags=_re.S)
    s = s.replace("#", "").replace("---", "").replace("{", " ").replace("}", " ").replace('"', "")
    s = _re.sub(r"\s+", " ", s).strip()
    bullets = [seg.strip() for seg in _re.split(r"(?<=[.!?。])\s+", s) if len(seg.strip()) > 8][:6]
    st.markdown(
        f'<div class="verdict"><div class="eyebrow">{t("AI 리서치", "AI research")}</div>'
        f'<div class="v-title" style="font-size:22px;"><span class="dot i"></span>{t("리서치 요약", "Research summary")}</div></div>',
        unsafe_allow_html=True)
    if bullets:
        st.markdown("".join(line(esc(b), "i") for b in bullets), unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="rc-missing"><div class="rc-h">{t("데이터 부족", "Not enough to report")}</div>'
            f'<div>· {t("리서치 메모를 붙여넣고 다시 생성하면 더 정확한 리포트를 만듭니다.", "Paste research notes and regenerate for a fuller report.")}</div></div>',
            unsafe_allow_html=True)


def _ai_get(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v not in (None, "", [], {}):
            return v
    return default


def render_ai_report_json(text):
    """Render the AI research report as a clean, decision-oriented layout.

    Tolerant of both the current schema and older cached reports. Never shows raw
    JSON or a parser failure to the user.
    """
    d = safe_json_parse(text)
    if not isinstance(d, dict) or not d:
        _ai_plain_fallback(text)
        return

    stance = str(_ai_get(d, "stance", "ai_stance")).lower()
    sk = {"favorable": "g", "neutral": "w", "risky": "b"}.get(stance, "i")
    stance_word = {"g": t("우호적", "Favorable"), "w": t("중립", "Neutral"),
                   "b": t("위험", "Risky"), "i": t("판단 보류", "Undecided")}[sk]
    title = esc(_ai_get(d, "report_title", default=t("AI 리서치", "AI research")))
    verdict = esc(_ai_get(d, "verdict", "ai_opinion"))
    prob = esc(_ai_get(d, "estimated_probability", "ai_estimated_probability"))
    conf = str(_ai_get(d, "confidence")).strip().lower()
    ck = {"high": "g", "medium": "w", "low": "b"}.get(conf, "i")
    conf_word = {"g": t("높음", "High"), "w": t("보통", "Medium"),
                 "b": t("낮음", "Low"), "i": "—"}[ck]

    pills = f'<span class="state {sk}">{stance_word}</span>'
    if prob and prob != "확인 필요":
        pills += f' <span class="state i">{t("AI 예상", "AI est.")} {prob}</span>'
    pills += f' <span class="state {ck}">{t("신뢰도", "Confidence")} {conf_word}</span>'

    st.markdown(
        f'<div class="verdict"><div class="eyebrow">{t("AI 리서치", "AI research")}</div>'
        f'<div class="v-title" style="font-size:24px;"><span class="dot {sk}"></span>{title}</div>'
        + (f'<div class="v-sub">{verdict}</div>' if verdict else "")
        + f'<div style="margin-top:12px;">{pills}</div></div>',
        unsafe_allow_html=True)

    basis = esc(_ai_get(d, "data_basis"))
    if basis:
        st.markdown(
            f'<div class="footnote" style="margin:-6px 0 6px 0;">{t("분석 근거", "Based on")}: {basis}</div>',
            unsafe_allow_html=True)

    summary = [x for x in (_ai_get(d, "summary", "summary_bullets", "research_summary", default=[]) or []) if str(x).strip()][:4]
    if summary:
        st.markdown(f'<div class="eyebrow">{t("핵심 요약", "Summary")}</div>'
                    + "".join(line(esc(x), "i") for x in summary), unsafe_allow_html=True)

    # Odds / edge — the numbers Memento already knows, framed.
    od = _ai_get(d, "odds", "odds_table", default={})
    LBL_OD = {
        "polymarket": "Polymarket", "polymarket_price": "Polymarket",
        "implied": t("시장 implied", "Implied"), "polymarket_implied": t("시장 implied", "Implied"),
        "fair": t("내 적정가", "My fair"), "user_fair_price": t("내 적정가", "My fair"),
        "edge": "Edge", "user_edge": "Edge",
        "bookmaker": t("외부배당", "Bookmaker"), "bookmaker_view": t("외부배당", "Bookmaker"),
        "read": t("코멘트", "Read"), "gap_comment": t("코멘트", "Read"),
    }
    if isinstance(od, dict):
        od_rows = [(LBL_OD.get(k, k), str(v)) for k, v in od.items() if str(v).strip()]
        if od_rows:
            st.markdown(f'<div class="eyebrow">{t("배당 · 엣지", "Odds · edge")}</div>'
                        + '<div class="rc-card">'
                        + "".join(f'<div class="rc-row"><span class="rc-k">{esc(k)}</span><span class="rc-v">{esc(v)}</span></div>' for k, v in od_rows)
                        + '</div>', unsafe_allow_html=True)

    # Resolution read — Claude's main value-add, highlighted.
    res = esc(_ai_get(d, "resolution_read", "resolution_check"))
    if res:
        st.markdown(f'<div class="eyebrow">{t("정산 조건 해석", "Resolution read")}</div>'
                    f'<div class="rc-card"><div class="rc-note">{res}</div></div>', unsafe_allow_html=True)

    # Scouting — only shown when there is real content beyond placeholders.
    sc = _ai_get(d, "scouting", "pre_match_table", "context_table", default={})
    LBL_SC = {
        "head_to_head": t("상대전적", "Head-to-head"), "recent_form": t("최근 폼", "Recent form"),
        "standing": t("순위", "Standing"), "league_standing": t("순위", "Standing"),
        "league_record": t("리그 전적", "League record"),
        "roster_news": t("로스터/뉴스", "Roster / news"), "style_matchup": t("스타일 매치업", "Style matchup"),
    }
    if isinstance(sc, dict):
        sc_rows = [(LBL_SC.get(k, k), str(v)) for k, v in sc.items() if str(v).strip()]
        real = [r for r in sc_rows if str(r[1]).strip() not in ("확인 필요", "Verify", "N/A", "-")]
        if real:
            st.markdown(f'<div class="eyebrow">{t("스카우팅", "Scouting")}</div>'
                        + '<div class="rc-card">'
                        + "".join(f'<div class="rc-row"><span class="rc-k">{esc(k)}</span><span class="rc-v">{esc(v)}</span></div>' for k, v in sc_rows)
                        + '</div>', unsafe_allow_html=True)

    swing = [x for x in (_ai_get(d, "swing_factors", "key_variables", default=[]) or []) if str(x).strip()][:5]
    if swing:
        st.markdown(f'<div class="eyebrow">{t("승부처", "Swing factors")}</div>'
                    + "".join(line(esc(x), "w") for x in swing), unsafe_allow_html=True)

    checklist = [x for x in (_ai_get(d, "checklist", default=[]) or []) if str(x).strip()][:6]
    if checklist:
        st.markdown(
            f'<div class="rc-action"><div class="rc-h">{t("진입 전 체크리스트", "Before you enter")}</div>'
            + "".join(f'<div class="rc-row"><span class="rc-k">☐</span><span class="rc-v" style="text-align:left;">{esc(x)}</span></div>' for x in checklist)
            + '</div>', unsafe_allow_html=True)

    md = [x for x in (_ai_get(d, "missing_data", default=[]) or []) if str(x).strip()]
    if md:
        st.markdown(f'<div class="rc-missing"><div class="rc-h">{t("확인 필요 데이터", "Verify yourself")}</div>'
                    + "".join(f"<div>· {esc(x)}</div>" for x in md) + '</div>', unsafe_allow_html=True)


def render_ai(text):
    render_ai_report_json(text)


# =====================================================
# Polymarket APIs
# =====================================================
def extract_slug(url):
    """Return the last usable path segment. Supports localized Polymarket URLs like /ko/sports/mlb/<slug>."""
    try:
        path = urllib.parse.urlparse(str(url or "").strip()).path.strip("/")
    except Exception:
        return ""
    parts = [p for p in path.split("/") if p]
    return parts[-1] if parts else ""

@st.cache_data(ttl=60, show_spinner=False)
def fetch_gamma(slug):
    api = f"https://gamma-api.polymarket.com/events?slug={urllib.parse.quote(slug)}"
    req = urllib.request.Request(api, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_list(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return []
    return []



GAME_RE = re.compile(r"\b(game|map)\s*[1-5]\b", re.I)
PROP_KW = (
    "first blood", "first tower", "first dragon", "first baron", "kills", "towers",
    "tower", "dragon", "baron", "handicap", "spread", "total", "over/under", "o/u",
    "correct score", "map score", "series score", "exact score", "duration",
    "objectives", "inhibitor", "first to", "player props",
)
MAIN_KW = (
    "moneyline", "match winner", "match-winner", "series winner", "series-winner",
    "overall winner", "event winner", "to win", "will win", "match result", "series result",
)


def classify_market_type(question, outcome="", is_binary=False):
    """Classify markets for URL-loaded Polymarket events.

    MAIN = full match / moneyline / series winner.
    GAME = specific game/map winner.
    PROP = markets the user does not want in the entry flow.
    Important: many Polymarket main moneyline markets are just binary team-vs-team
    questions without the word "moneyline". Those are promoted to MAIN when
    they are not props and not game/map-specific.
    """
    s = f"{question or ''} {outcome or ''}".lower()
    if any(k in s for k in PROP_KW):
        return "prop"
    if GAME_RE.search(s):
        return "p2_game"
    if any(k in s for k in MAIN_KW):
        return "p1_main"
    if is_binary:
        return "p1_main"
    return "other"


def is_prop_market(q, outcome=""):
    return classify_market_type(q, outcome, False) == "prop"


def is_relevant_market(q, outcome="", event_title=""):
    s = f"{event_title or ''} {q or ''}"
    return classify_market_type(s, outcome, False) in ("p1_main", "p2_game")


def _event_resolution(event, market):
    return (market.get("rules") or market.get("description") or market.get("resolutionSource") or
            event.get("rules") or event.get("description") or event.get("resolutionSource") or "")


def _event_volume(event, market):
    return market.get("volume") or market.get("volumeNum") or event.get("volume") or event.get("volumeNum") or ""


def _event_liquidity(event, market):
    return market.get("liquidity") or market.get("liquidityNum") or event.get("liquidity") or event.get("liquidityNum") or ""


def _event_end_date(event, market):
    return market.get("endDate") or market.get("endDateIso") or event.get("endDate") or event.get("endDateIso") or ""


def extract_markets(payload, category=""):
    """Extract MAIN + GAME winner markets.

    Return order:
    1) MAIN full match / moneyline / series winner, including binary non-prop non-game markets
    2) GAME/MAP winner
    Props are excluded. Game markets never replace main markets.
    """
    events = payload if isinstance(payload, list) else payload.get("events", []) if isinstance(payload, dict) else []
    if not isinstance(events, list):
        return []
    p1, p2, binary_other = [], [], []
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            continue
        event_title = event.get("title") or event.get("slug") or ""
        for m in event.get("markets", []) or []:
            if not isinstance(m, dict):
                continue
            q = m.get("question") or m.get("title") or m.get("slug") or event_title or "Unknown"
            outs = parse_list(m.get("outcomes"))
            prices = parse_list(m.get("outcomePrices"))
            tokens = parse_list(m.get("clobTokenIds"))
            if not outs:
                continue
            is_bin = len(outs) == 2
            cls = classify_market_type(f"{event_title} {q}", "", is_bin)
            if cls == "prop":
                continue
            for i, o in enumerate(outs):
                price = None
                if i < len(prices):
                    try:
                        price = round(float(prices[i]) * 100, 2)
                    except Exception:
                        price = None
                row = {
                    t("시장", "Market"): q,
                    t("선택지", "Outcome"): o,
                    t("현재가 (¢)", "Price (¢)"): price,
                    "token_id": tokens[i] if i < len(tokens) else "",
                    "volume": _event_volume(event, m),
                    "liquidity": _event_liquidity(event, m),
                    "endDate": _event_end_date(event, m),
                    "resolution": _event_resolution(event, m),
                    "event_title": event_title,
                    "market_class": cls,
                    "_binary": is_bin,
                }
                key = (row[t("시장", "Market")], row[t("선택지", "Outcome")], row.get("token_id"))
                if key in seen:
                    continue
                seen.add(key)
                if cls == "p1_main":
                    p1.append(row)
                elif cls == "p2_game":
                    p2.append(row)
                elif is_bin:
                    binary_other.append(row)
    if not p1 and binary_other:
        for r in binary_other:
            r["market_class"] = "p1_main"
        p1 = binary_other
    return p1 + p2

def infer_market_category(url="", name=""):
    s = f"{url or ''} {name or ''}".lower()
    if any(x in s for x in ["/sports/", "mlb", "nba", "nfl", "nhl", "soccer", "ufc", "tennis", "baseball", "basketball"]):
        return t("일반 스포츠", "Sports")
    if any(x in s for x in ["lol", "lck", "lpl", "valorant", "cs2", "dota", "esports"]):
        return t("e스포츠", "Esports")
    if any(x in s for x in ["election", "politic", "president", "mayor", "선거"]):
        return t("정치", "Politics")
    if any(x in s for x in ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana", "sol"]):
        return t("크립토", "Crypto")
    if any(x in s for x in ["news", "event"]):
        return t("뉴스·이벤트", "News / events")
    return t("기타", "Other")


def infer_market_subcategory(url="", name=""):
    s = f"{url or ''} {name or ''}".lower()
    if "mlb" in s or "baseball" in s:
        return t("야구", "Baseball")
    if "nba" in s or "basketball" in s:
        return t("농구", "Basketball")
    if "nfl" in s or "football" in s:
        return t("미식축구", "Football")
    if "soccer" in s:
        return t("축구", "Soccer")
    if "tennis" in s:
        return t("테니스", "Tennis")
    if "ufc" in s or "mma" in s:
        return "UFC/MMA"
    if "lol" in s or "lck" in s or "lpl" in s:
        return "LoL"
    return t("기타", "Other")

def _escape(v):
    return html.escape(str(v or ""))


def _as_cents(v):
    try:
        f = float(v)
        return f * 100 if 0 <= f <= 1 else f
    except Exception:
        return None


@st.cache_data(ttl=45, show_spinner=False)
def fetch_clob_price(token_id):
    """Read-only CLOB quote. Public endpoint; no trading/auth."""
    token_id = str(token_id or "").strip()
    if not token_id:
        return {"bid": None, "ask": None, "spread": None, "raw": {}}

    out = {"bid": None, "ask": None, "spread": None, "raw": {}}

    def _get(path, params):
        url = "https://clob.polymarket.com" + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))

    try:
        bid_raw = _get("/price", {"token_id": token_id, "side": "BUY"})
        out["raw"]["bid"] = bid_raw
        out["bid"] = _as_cents(bid_raw.get("price") if isinstance(bid_raw, dict) else None)
    except Exception as e:
        out["raw"]["bid_error"] = str(e)

    try:
        ask_raw = _get("/price", {"token_id": token_id, "side": "SELL"})
        out["raw"]["ask"] = ask_raw
        out["ask"] = _as_cents(ask_raw.get("price") if isinstance(ask_raw, dict) else None)
    except Exception as e:
        out["raw"]["ask_error"] = str(e)

    try:
        sp_raw = _get("/spread", {"token_id": token_id})
        out["raw"]["spread"] = sp_raw
        out["spread"] = _as_cents(sp_raw.get("spread") if isinstance(sp_raw, dict) else None)
    except Exception as e:
        out["raw"]["spread_error"] = str(e)

    if out["spread"] is None and out["bid"] is not None and out["ask"] is not None:
        out["spread"] = out["ask"] - out["bid"]
    return out




@st.cache_data(ttl=45, show_spinner=False)
def fetch_clob_book(token_id):
    """Read-only CLOB orderbook. Fails soft."""
    token_id = str(token_id or "").strip()
    if not token_id:
        return {}
    try:
        url = "https://clob.polymarket.com/book?" + urllib.parse.urlencode({"token_id": token_id})
        req = urllib.request.Request(url, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=15, show_spinner=False)
def fetch_live_token_price(token_id):
    """Return live bid/ask/mid/spread in cents. Fails soft and never calls Claude."""
    token_id = str(token_id or "").strip()
    if not token_id:
        return None
    # First try the existing quote endpoints. They are more stable than raw book shape.
    try:
        q = fetch_clob_price(token_id)
        bid, ask, spread = q.get("bid"), q.get("ask"), q.get("spread")
        mid = round((float(bid) + float(ask)) / 2, 2) if bid is not None and ask is not None else (bid if bid is not None else ask)
        if mid is not None:
            return {"bid": bid, "ask": ask, "mid": mid, "spread": spread, "source": "price"}
    except Exception:
        pass
    # Fallback to book. The JSON shape can differ, so parse defensively.
    try:
        book = fetch_clob_book(token_id)
        bids = book.get("bids") or [] if isinstance(book, dict) else []
        asks = book.get("asks") or [] if isinstance(book, dict) else []
        def _price(x):
            if isinstance(x, dict):
                return _as_cents(x.get("price"))
            if isinstance(x, (list, tuple)) and x:
                return _as_cents(x[0])
            return None
        bid_prices = [p for p in (_price(x) for x in bids) if p is not None]
        ask_prices = [p for p in (_price(x) for x in asks) if p is not None]
        bid = max(bid_prices) if bid_prices else None
        ask = min(ask_prices) if ask_prices else None
        mid = round((bid + ask) / 2, 2) if bid is not None and ask is not None else (bid if bid is not None else ask)
        spread = round(ask - bid, 2) if bid is not None and ask is not None else None
        return {"bid": bid, "ask": ask, "mid": mid, "spread": spread, "source": "book"} if mid is not None else None
    except Exception:
        return None


_PMHIST_RANGES = {
    "1H": ("1h", 1),
    "6H": ("6h", 5),
    "1D": ("1d", 15),
    "1W": ("1w", 60),
    "1M": ("1m", 180),
    "MAX": ("max", 720),
}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_price_history(token_id, rng="1D"):
    """Polymarket CLOB price history -> list[{t,p}] (t=unix sec, p=cents). Fails soft."""
    token_id = str(token_id or "").strip()
    if not token_id:
        return []
    interval, fidelity = _PMHIST_RANGES.get(str(rng).upper(), ("1d", 15))
    attempts = [
        ("https://clob.polymarket.com/prices-history", {"market": token_id, "interval": interval, "fidelity": fidelity}),
        ("https://clob.polymarket.com/prices-history", {"market": token_id, "fidelity": fidelity}),
    ]
    for base, params in attempts:
        try:
            url = base + "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                d = json.loads(r.read().decode("utf-8"))
            hist = d.get("history") if isinstance(d, dict) else d
            if not isinstance(hist, list):
                hist = []
            out = []
            for p in hist:
                if not isinstance(p, dict):
                    continue
                pc = _as_cents(p.get("p", p.get("price", p.get("value"))))
                if pc is None:
                    continue
                out.append({"t": p.get("t", p.get("timestamp", len(out))), "p": round(pc, 2)})
            if out:
                return out
        except Exception:
            continue
    return []

def evaluate_live_price(entry_result, live_price):
    """Deterministic live re-evaluation. Does not call Claude."""
    entry_result = entry_result if isinstance(entry_result, dict) else {}
    fair = float(entry_result.get("fair_price") or st.session_state.get("watching_market", {}).get("fair_price") or 0)
    entry_p = float(entry_result.get("current_price") or st.session_state.get("watching_market", {}).get("entry_price") or 0)
    target = float(entry_result.get("target_price") or 999)
    edge = fair - float(live_price)
    move = float(live_price) - entry_p
    if live_price >= target:
        status, kind = t("익절 구간", "Take-profit zone"), "w"
    elif fair and live_price >= fair:
        status, kind = t("비쌈 — 진입 불리", "Expensive — worse entry"), "b"
    elif edge >= 8:
        status, kind = t("저평가 — 진입 유리", "Cheap — better entry"), "g"
    elif edge >= 3:
        status, kind = t("약간 저평가", "Slightly cheap"), "w"
    else:
        status, kind = t("적정", "Fair"), "i"
    return {"edge": edge, "move": move, "status": status, "kind": kind, "implied": live_price, "fair": fair}


def render_live_price_panel(wm):
    """Live mid + edge update + real Polymarket price-history chart. Auto-refreshes; read-only."""
    wm = wm if isinstance(wm, dict) else {}
    tok = str(wm.get("token_id", "") or "")
    if not tok:
        st.markdown(line(t("실시간 추적 token_id가 없습니다.", "No token_id for live tracking."), "w"), unsafe_allow_html=True)
        return

    ranges = ["1H", "6H", "1D", "1W", "1M", "MAX"]
    cc1, cc2 = st.columns([3, 1])
    with cc1:
        rng = st.radio(
            t("기간", "Range"),
            ranges,
            index=2,
            horizontal=True,
            key=f"live_rng_{tok}",
            label_visibility="collapsed",
        )
    with cc2:
        if st.button(t("새로고침", "Refresh"), key=f"live_refresh_{tok}", use_container_width=True):
            try:
                fetch_live_token_price.clear()
                fetch_price_history.clear()
            except Exception:
                pass
            st.rerun()
    auto = st.checkbox(t("자동 갱신 (15초)", "Auto-refresh (15s)"), value=True, key=f"live_auto_{tok}")

    def _body():
        lp = fetch_live_token_price(tok)
        if not lp or lp.get("mid") is None:
            st.markdown(line(t("실시간 호가 없음 — Polymarket에서 직접 확인 필요.", "No live book — verify on Polymarket."), "w"), unsafe_allow_html=True)
            return
        live = float(lp["mid"])
        r = st.session_state.get("last_entry", {})
        r = r if isinstance(r, dict) else {}
        ev = evaluate_live_price(r, live)
        st.markdown(
            '<div class="stats">'
            + stat(t("실시간 중간가", "Live mid"), cents(live), t(f"분석시 {cents(wm.get('entry_price', 0))}", f"at analysis {cents(wm.get('entry_price', 0))}"))
            + stat("Bid / Ask", f"{cents(float(lp['bid'])) if lp.get('bid') is not None else '—'} / {cents(float(lp['ask'])) if lp.get('ask') is not None else '—'}", f"{t('스프레드','spread')} {cents(float(lp['spread'])) if lp.get('spread') is not None else '—'}")
            + stat(t("실시간 Edge", "Live edge"), f"{ev['edge']:+.1f}¢", t("적정가 대비", "vs fair"), "pos" if ev['edge'] >= 3 else "neg" if ev['edge'] < 0 else "")
            + stat(t("분석 후 변동", "Move since"), f"{ev['move']:+.1f}¢", t("시장 가격 변화", "market move"), "pos" if ev['move'] >= 0 else "neg")
            + "</div>", unsafe_allow_html=True)
        st.markdown(meter(t("시장 판단 vs 내 판단", "Market view vs my view"), live, ev["kind"], ev["status"], unit="¢"), unsafe_allow_html=True)

        hist = fetch_price_history(tok, rng)
        if not hist:
            st.markdown(f'<div class="footnote">{t("이 기간의 가격 히스토리가 아직 없습니다.", "No price history for this range yet.")}</div>', unsafe_allow_html=True)
            return
        dfh = pd.DataFrame(hist)
        try:
            # Polymarket usually returns unix seconds. Guard ms timestamps too.
            t_numeric = pd.to_numeric(dfh["t"], errors="coerce")
            unit = "ms" if t_numeric.dropna().max() and t_numeric.dropna().max() > 10**11 else "s"
            dfh["ts"] = pd.to_datetime(t_numeric, unit=unit, errors="coerce")
            dfh = dfh.dropna(subset=["ts", "p"])
        except Exception:
            dfh["ts"] = pd.to_datetime(dfh.index, unit="s", errors="coerce")
        if dfh.empty:
            st.markdown(f'<div class="footnote">{t("차트로 표시할 수 있는 가격 데이터가 없습니다.", "No chartable price data.")}</div>', unsafe_allow_html=True)
            return
        try:
            import altair as alt
            lo, hi = float(dfh["p"].min()), float(dfh["p"].max())
            pad = max(1.5, (hi - lo) * 0.2)
            dom = [max(0.0, lo - pad), min(100.0, hi + pad)]
            base = alt.Chart(dfh).encode(
                x=alt.X(
                    "ts:T",
                    title=None,
                    axis=alt.Axis(grid=False, labelColor="#a2a5af", tickColor="#e9eaee", domainColor="#e9eaee"),
                )
            )
            area = base.mark_area(
                line={"color": "#3b4ef0", "strokeWidth": 2},
                color=alt.Gradient(
                    gradient="linear",
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                    stops=[
                        alt.GradientStop(color="#ffffff", offset=0),
                        alt.GradientStop(color="#e9ecfe", offset=1),
                    ],
                ),
            ).encode(
                y=alt.Y(
                    "p:Q",
                    title=None,
                    scale=alt.Scale(domain=dom),
                    axis=alt.Axis(grid=True, gridColor="#f0f1f4", labelColor="#a2a5af", tickColor="#e9eaee", domainColor="#e9eaee"),
                ),
                tooltip=[alt.Tooltip("ts:T", title="time"), alt.Tooltip("p:Q", title="¢", format=".1f")],
            )
            layers = [area]
            try:
                fairf = float(wm.get("fair_price") or 0)
            except Exception:
                fairf = 0.0
            if fairf:
                layers.append(
                    alt.Chart(pd.DataFrame({"y": [fairf]}))
                    .mark_rule(strokeDash=[4, 4], color="#a2a5af")
                    .encode(y="y:Q")
                )
            st.altair_chart(alt.layer(*layers).properties(height=210).configure_view(strokeWidth=0), use_container_width=True)
        except Exception:
            st.line_chart(dfh.set_index("ts")["p"], height=210)

    frag = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None)
    if auto and frag:
        try:
            frag(run_every=15)(_body)()
            return
        except Exception:
            pass
    _body()
    if auto and not frag:
        st.markdown(f'<div class="footnote">{t("자동 갱신은 Streamlit 1.37+에서 지원됩니다. 새로고침 버튼을 눌러 갱신하세요.", "Auto-refresh needs Streamlit 1.37+. Use the Refresh button.")}</div>', unsafe_allow_html=True)


def _first_present(obj, keys, default=""):
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj.get(k) not in (None, ""):
                return obj.get(k)
        for v in obj.values():
            got = _first_present(v, keys, None)
            if got not in (None, ""):
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _first_present(v, keys, None)
            if got not in (None, ""):
                return got
    return default


def _history_points(raw):
    if isinstance(raw, dict):
        for key in ("history", "prices", "data"):
            val = raw.get(key)
            if isinstance(val, list):
                return val
    return raw if isinstance(raw, list) else []


def history_summary(raw):
    pts = _history_points(raw)
    vals = []
    for p in pts:
        if isinstance(p, dict):
            val = p.get("p", p.get("price", p.get("value")))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            val = p[1]
        else:
            val = p
        cv = _as_cents(val)
        if cv is not None:
            vals.append(cv)
    if len(vals) >= 2:
        return {"start": vals[0], "last": vals[-1], "change": vals[-1] - vals[0], "points": len(vals)}
    return {"start": None, "last": None, "change": None, "points": len(vals)}


def book_summary(raw):
    bids = raw.get("bids", []) if isinstance(raw, dict) else []
    asks = raw.get("asks", []) if isinstance(raw, dict) else []
    def _level_value(level):
        if isinstance(level, dict):
            price = _as_cents(level.get("price")) or 0
            size = _safe_float(level.get("size"), 0)
            return price, size
        if isinstance(level, (list, tuple)) and len(level) >= 2:
            return _as_cents(level[0]) or 0, _safe_float(level[1], 0)
        return 0, 0
    bid_depth = sum(_level_value(x)[1] for x in bids[:5])
    ask_depth = sum(_level_value(x)[1] for x in asks[:5])
    return {"bids": len(bids), "asks": len(asks), "bid_depth5": bid_depth, "ask_depth5": ask_depth}


def build_order_candidate(row, clob=None, bankroll=None):
    clob = clob or {}
    bankroll = bankroll or effective_bankroll()
    price = row_get(row, "현재가 (¢)", "Price (¢)", 52.0)
    try:
        price = float(price)
    except Exception:
        price = 52.0
    bid = clob.get("bid")
    spread = clob.get("spread")
    limit_price = bid if isinstance(bid, (int, float)) and bid > 0 else price
    max_amt = min(bankroll * profile().get("max_pct", 3) / 100, profile().get("emotional_limit", 50))
    shares = max_amt / (limit_price / 100) if limit_price > 0 else 0
    kind = "g"
    note = t("후보 생성 가능", "Candidate ready")
    if isinstance(spread, (int, float)) and spread >= 5:
        kind, note = "w", t("스프레드 넓음 — 원본 호가 확인", "Wide spread — confirm orderbook")
    if price >= 85:
        kind, note = "w", t("고가 구간 — 신규 주문 후보는 보수적으로", "High-price zone — conservative sizing")
    if price >= 95:
        kind, note = "b", t("상환 스캘핑 구간 — 자동 주문 금지", "Redemption-scap zone — no automation")
    return {"limit_price": limit_price, "max_amount": max_amt, "shares": shares, "kind": kind, "note": note}

def row_get(row, ko, en=None, default=""):
    if not isinstance(row, dict):
        return default
    if ko in row:
        return row.get(ko, default)
    if en and en in row:
        return row.get(en, default)
    lookup = ("시장", "Market") if ko == "시장" else ("선택지", "Outcome") if ko == "선택지" else ("현재가 (¢)", "Price (¢)")
    for k in lookup:
        if k in row:
            return row.get(k, default)
    return row.get(ko, default)


def market_card_html(row, clob=None, book=None, hist=None, cand=None):
    name = row_get(row, "시장", "Market", "Unknown")
    outcome = row_get(row, "선택지", "Outcome", "")
    price = row_get(row, "현재가 (¢)", "Price (¢)", None)
    token = row.get("token_id", "") if isinstance(row, dict) else ""
    clob = clob or {}
    book = book or {}
    hist = hist or {}
    cand = cand or {}
    bid = clob.get("bid")
    ask = clob.get("ask")
    spread = clob.get("spread")
    hs = history_summary(hist)
    bs = book_summary(book)
    price_text = cents(float(price)) if isinstance(price, (int, float)) else "—"
    bid_text = cents(float(bid)) if isinstance(bid, (int, float)) else "—"
    ask_text = cents(float(ask)) if isinstance(ask, (int, float)) else "—"
    spread_text = cents(float(spread)) if isinstance(spread, (int, float)) else "—"
    ch = hs.get("change")
    hist_text = signed_pct(ch) if isinstance(ch, (int, float)) else "—"
    token_short = str(token)[:8] + "…" if token else "—"
    vol = row.get("volume", "") if isinstance(row, dict) else ""
    liq = row.get("liquidity", "") if isinstance(row, dict) else ""
    end_date = row.get("endDate", "") if isinstance(row, dict) else ""
    resolution = str(row.get("resolution", "") or "")[:180]
    cand_note = cand.get("note", "")
    cand_kind = cand.get("kind", "i")
    return f"""<div class=\"market-card\">
  <div class=\"market-head\">
    <div>
      <div class=\"market-title\">{_escape(name)}</div>
      <div class=\"market-sub\">{t('선택지', 'Outcome')} · <b>{_escape(outcome)}</b></div>
    </div>
    <div class=\"market-price\">{price_text}</div>
  </div>
  <div class=\"market-metrics\">
    <div class=\"market-metric\"><div class=\"k\">Best bid</div><div class=\"v\">{bid_text}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Best ask</div><div class=\"v\">{ask_text}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Spread</div><div class=\"v\">{spread_text}</div></div>
    <div class=\"market-metric\"><div class=\"k\">History</div><div class=\"v\">{hist_text}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Volume</div><div class=\"v\">{_escape(vol or '—')}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Liquidity</div><div class=\"v\">{_escape(liq or '—')}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Book</div><div class=\"v\">B{bs.get('bids',0)} / A{bs.get('asks',0)}</div></div>
    <div class=\"market-metric\"><div class=\"k\">Token</div><div class=\"v\">{_escape(token_short)}</div></div>
  </div>
  <div class=\"market-note\"><b>{t('주문 후보', 'Order candidate')}</b> · <span class=\"state {cand_kind}\">{_escape(cand_note)}</span> · {t('실제 주문은 원본 Polymarket에서 확인하세요.', 'Confirm actual orders on Polymarket.')}</div>
  <div class=\"market-note\"><b>{t('만기/해결 기준', 'End / resolution')}</b> · {_escape(end_date or '—')} · {_escape(resolution or t('데이터 없음/직접 확인 필요', 'No data / verify manually'))}</div>
</div>"""

@st.cache_data(ttl=30, show_spinner=False)
def fetch_wallet_positions(addr):
    """Public Polymarket data API — read-only, no login required."""
    api = f"https://data-api.polymarket.com/positions?user={urllib.parse.quote(addr)}&sizeThreshold=0.5&limit=100"
    req = urllib.request.Request(api, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))



@st.cache_data(ttl=60, show_spinner=False)
def fetch_wallet_value(addr):
    api = f"https://data-api.polymarket.com/value?user={urllib.parse.quote(addr)}"
    req = urllib.request.Request(api, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


def _find_first_number(obj, keys):
    if isinstance(obj, dict):
        lower = {str(k).lower(): v for k, v in obj.items()}
        for k in keys:
            if k.lower() in lower:
                val = _safe_float(lower[k.lower()], None)
                if val is not None:
                    return val
        for v in obj.values():
            got = _find_first_number(v, keys)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find_first_number(v, keys)
            if got is not None:
                return got
    return None


def calc_profile_pnl(portfolio, cash, raw_positions=None, raw_value=None):
    raw_positions = raw_positions if isinstance(raw_positions, list) else []
    pos_value_local = sum(_safe_float(p.get("shares"), 0) * (_safe_float(p.get("cur"), 0) / 100) for p in portfolio)
    pos_cost_local = sum(_safe_float(p.get("inv"), 0) for p in portfolio)
    value_api = _find_first_number(raw_value, ["value", "positionValue", "positionsValue", "totalValue", "currentValue"])
    pos_value = value_api if value_api is not None and value_api >= 0 else pos_value_local
    raw_initial = sum(_safe_float(it.get("initialValue"), 0) for it in raw_positions)
    raw_current = sum(_safe_float(it.get("currentValue"), 0) for it in raw_positions)
    raw_realized = sum(_safe_float(it.get("realizedPnl"), 0) for it in raw_positions)
    raw_cash = sum(0 for it in raw_positions)
    raw_percent = _find_first_number(raw_positions, ["percentPnl", "percentRealizedPnl", "percentCashPnl"])
    cost = raw_initial if raw_initial > 0 else pos_cost_local
    if raw_current > 0 and value_api is None:
        pos_value = raw_current
    unrealized = pos_value - cost if cost else pos_value - pos_cost_local
    unrealized_pct = unrealized / cost * 100 if cost else 0
    wallet_assets = cash + pos_value
    deposits = _safe_float(st.session_state.deposits, 0)
    withdrawals = _safe_float(st.session_state.withdrawals, 0)
    # Manual cash/deposit/withdrawal inputs are the source of truth for profile-like P&L.
    # Deposit and withdrawal are both entered as positive total amounts.
    net_profit = wallet_assets + withdrawals - deposits
    adjusted_roi = net_profit / deposits * 100 if deposits else None
    _, month_pnl, year_pnl = period_pnl()
    status_kind = "g" if net_profit >= 0 else "b"
    status_text = t("누적 이익 중", "Net profitable") if net_profit >= 0 else t("누적 손실 중", "Net loss")
    return {"position_value": pos_value, "position_cost": cost, "cash": cash, "wallet_assets": wallet_assets,
            "unrealized": unrealized, "unrealized_pct": unrealized_pct,
            "realized_pnl": raw_realized, "percent_pnl": raw_percent if raw_percent is not None else unrealized_pct,
            "deposits": deposits, "withdrawals": withdrawals,
            "adjusted_profit": net_profit, "net_profit": net_profit, "adjusted_roi": adjusted_roi,
            "month_pnl": month_pnl, "year_pnl": year_pnl, "status_kind": status_kind, "status_text": status_text,
            "source_note": t("수동 현금·입금·출금 + 공개 포지션 API 기준", "Manual cash/deposit/withdrawal + public position API")}


def render_profile_pnl_dashboard(pnl):
    kind = pnl.get("status_kind", "i")
    prof_line = st.session_state.wallet_addr[:6] + "…" + st.session_state.wallet_addr[-4:] if st.session_state.wallet_addr else t("지갑 미연결", "No wallet")
    adj_tone = "pos" if pnl.get("adjusted_profit", 0) >= 0 else "neg"
    un_tone = "pos" if pnl.get("unrealized", 0) >= 0 else "neg"
    yr_tone = "pos" if pnl.get("year_pnl", 0) >= 0 else "neg"
    roi_val = pnl.get("adjusted_roi")
    roi_text = signed_pct(roi_val) if roi_val is not None else "—"
    html = f"""<div class='profile-hero'>
  <div class='profile-hero-head'>
    <div><div class='title'><span class='dot {kind}'></span>{esc(pnl.get('status_text', ''))}</div>
    <div class='sub'>{t('Polymarket 프로필 손익 요약', 'Polymarket profile P&L summary')} · {esc(prof_line)} · {esc(pnl.get('source_note', ''))}</div></div>
    <span class='state {kind}'>{esc(pnl.get('status_text', ''))}</span>
  </div>
  <div class='profile-grid'>
    <div class='profile-cell'><div class='k'>{t('현재 포지션 가치', 'Position value')}</div><div class='v'>{money(pnl.get('position_value', 0))}</div></div>
    <div class='profile-cell'><div class='k'>{t('지갑 총자산', 'Wallet assets')}</div><div class='v'>{money(pnl.get('wallet_assets', 0))}</div></div>
    <div class='profile-cell'><div class='k'>{t('출금보정 누적손익', 'Cashflow-adjusted P&L')}</div><div class='v {adj_tone}'>{signed_money(pnl.get('adjusted_profit', 0))}</div></div>
    <div class='profile-cell'><div class='k'>{t('보정 수익률', 'Adjusted ROI')}</div><div class='v {adj_tone}'>{roi_text}</div></div>
    <div class='profile-cell'><div class='k'>{t('올해 손익', 'Year P&L')}</div><div class='v {yr_tone}'>{signed_money(pnl.get('year_pnl', 0))}</div></div>
    <div class='profile-cell'><div class='k'>realizedPnl</div><div class='v'>{signed_money(pnl.get('realized_pnl', 0))}</div></div>
  </div>
  <div class='sub' style='margin-top:14px;'>{t('Polymarket 프로필 화면과 소액 차이가 날 수 있습니다. 출금·입금·정산·dust 포지션은 보정값과 API 필드에 따라 달라집니다.', 'This can differ slightly from the Polymarket profile due to withdrawals, deposits, settlements and dust positions.')}</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


@st.cache_data(ttl=60, show_spinner=False)
def fetch_wallet_activity(addr, limit=100, offset=0):
    """Read-only Polymarket activity feed for a wallet. Used for automatic trade history import."""
    qs = urllib.parse.urlencode({
        "user": addr,
        "limit": int(limit),
        "offset": int(offset),
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC",
    })
    api = f"https://data-api.polymarket.com/activity?{qs}"
    req = urllib.request.Request(api, headers={"User-Agent": "Memento/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def _safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _activity_dt(v):
    ts = _safe_float(v, 0)
    if ts <= 0:
        return datetime.now().isoformat()
    if ts > 10_000_000_000:  # milliseconds
        ts = ts / 1000
    # Polymarket timestamps are UTC; display in Korea time for journal grouping.
    return (datetime.utcfromtimestamp(ts) + timedelta(hours=9)).isoformat()


def normalize_activity(raw):
    """Convert raw Polymarket activity rows into a simple journal-like table."""
    rows = []
    if not isinstance(raw, list):
        return rows
    for it in raw:
        if not isinstance(it, dict):
            continue
        typ = str(it.get("type", "TRADE")).upper()
        side = str(it.get("side", "")).upper()
        # Keep trade-like rows first. Other activity can stay in raw debug.
        if typ and typ != "TRADE" and side not in ("BUY", "SELL"):
            continue
        price_raw = _safe_float(it.get("price"), 0)
        price_c = price_raw * 100 if 0 < price_raw <= 1 else price_raw
        size = _safe_float(it.get("size"), 0)
        usdc = _safe_float(it.get("usdcSize"), 0)
        amount = usdc if usdc > 0 else size * (price_c / 100 if price_c else 0)
        tx_base = it.get("transactionHash") or it.get("transaction_hash") or it.get("hash") or ""
        asset = it.get("asset") or it.get("conditionId") or it.get("slug") or ""
        tx_id = "|".join([str(tx_base), str(asset), str(it.get("timestamp", "")), side, str(size), str(price_raw)])
        rows.append({
            "tx_id": tx_id,
            "d": _activity_dt(it.get("timestamp")),
            "name": it.get("title") or it.get("slug") or it.get("eventSlug") or "Polymarket trade",
            "outcome": it.get("outcome", ""),
            "side": side or typ,
            "price": round(price_c, 2),
            "shares": round(size, 4),
            "amount": round(amount, 2),
            "asset": str(asset),
            "token_id": str(asset),
        })
    return rows


def merge_activity_into_log(items):
    """Merge API trades into auto_trades without duplicating existing rows."""
    if not isinstance(st.session_state.imported_tx_ids, list):
        st.session_state.imported_tx_ids = []
    seen = set(st.session_state.imported_tx_ids)
    added = 0
    for it in items:
        tx = it.get("tx_id") or ""
        if not tx or tx in seen:
            continue
        st.session_state.auto_trades.append(it)
        st.session_state.imported_tx_ids.append(tx)
        seen.add(tx)
        added += 1
    return added


def summarize_activity(items):
    # Summarize imported activity for pattern review. Does not calculate realized P&L.
    now = datetime.now()
    today = now.date().isoformat()
    week_start = (now - timedelta(days=now.weekday())).date()
    month_key = now.strftime("%Y-%m")
    out = {
        "count": 0, "buy_count": 0, "sell_count": 0, "today_count": 0,
        "week_count": 0, "month_count": 0, "total_amount": 0.0,
        "top_market": "-", "top_market_count": 0, "market_count": 0,
        "repeat_markets": [], "heavy_markets": [], "insights": []
    }
    if not items:
        out["insights"].append(("i", t("불러온 거래내역이 없습니다.", "No imported activity yet.")))
        return out

    market_stats = {}
    for tr in items:
        name = str(tr.get("name") or "Unknown")
        side = str(tr.get("side") or "").upper()
        amount = _safe_float(tr.get("amount"), 0)
        out["count"] += 1
        out["total_amount"] += amount
        if side == "BUY":
            out["buy_count"] += 1
        elif side == "SELL":
            out["sell_count"] += 1
        d = str(tr.get("d") or "")[:10]
        if d == today:
            out["today_count"] += 1
        try:
            dd = datetime.fromisoformat(str(tr.get("d"))).date()
            if dd >= week_start:
                out["week_count"] += 1
            if str(tr.get("d"))[:7] == month_key:
                out["month_count"] += 1
        except Exception:
            pass
        stt = market_stats.setdefault(name, {"count": 0, "buy": 0, "sell": 0, "amount": 0.0})
        stt["count"] += 1
        stt["amount"] += amount
        if side == "BUY": stt["buy"] += 1
        if side == "SELL": stt["sell"] += 1

    out["market_count"] = len(market_stats)
    ranked = sorted(market_stats.items(), key=lambda x: (x[1]["count"], x[1]["amount"]), reverse=True)
    if ranked:
        out["top_market"], top = ranked[0]
        out["top_market_count"] = top["count"]
    out["repeat_markets"] = [(n, v) for n, v in ranked if v["count"] >= 3]
    out["heavy_markets"] = [(n, v) for n, v in ranked if v["amount"] >= max(out["total_amount"] * 0.35, 50)]

    buy_ratio = out["buy_count"] / out["count"] * 100 if out["count"] else 0
    if out["today_count"] >= 10:
        out["insights"].append(("b", t(f"오늘 거래 {out['today_count']}건 — 거래 빈도가 높습니다. 감정적 재진입 여부를 점검하세요.",
                                        f"{out['today_count']} trades today — high frequency. Check for emotional re-entry.")))
    elif out["today_count"] >= 5:
        out["insights"].append(("w", t(f"오늘 거래 {out['today_count']}건 — 잦은 진입 구간입니다.",
                                        f"{out['today_count']} trades today — frequent trading zone.")))
    else:
        out["insights"].append(("g", t(f"오늘 거래 {out['today_count']}건 — 빈도는 과하지 않습니다.",
                                        f"{out['today_count']} trades today — frequency is not excessive.")))
    if buy_ratio >= 75 and out["count"] >= 5:
        out["insights"].append(("w", t(f"BUY 비율 {buy_ratio:.0f}% — 매수 중심입니다. 익절/축소 계획이 있는지 확인하세요.",
                                        f"BUY ratio {buy_ratio:.0f}% — buy-heavy. Check whether you have exit/reduction rules.")))
    if out["repeat_markets"]:
        names = ", ".join(n[:34] + ("…" if len(n) > 34 else "") for n, _ in out["repeat_markets"][:3])
        out["insights"].append(("w", t(f"같은 시장 반복 거래 감지: {names}. 물타기/추격매수인지 복기하세요.",
                                        f"Repeated market activity: {names}. Review whether it was averaging down or chasing.")))
    if out["heavy_markets"]:
        n, v = out["heavy_markets"][0]
        out["insights"].append(("w", t(f"거래금액 집중: {n[:48]} · {money(v['amount'])}. 한 시장에 노출이 몰렸는지 확인하세요.",
                                        f"Concentrated turnover: {n[:48]} · {money(v['amount'])}. Check if exposure is clustered.")))
    return out


def activity_market_table(items):
    # Market-level activity summary table, intentionally no realized P&L pairing.
    agg = {}
    for tr in items:
        name = str(tr.get("name") or "Unknown")
        side = str(tr.get("side") or "").upper()
        a = agg.setdefault(name, {"market": name, "count": 0, "buy": 0, "sell": 0, "amount": 0.0, "last": ""})
        a["count"] += 1
        a["amount"] += _safe_float(tr.get("amount"), 0)
        if side == "BUY": a["buy"] += 1
        if side == "SELL": a["sell"] += 1
        d = str(tr.get("d") or "")[:16]
        if d > a["last"]:
            a["last"] = d
    return sorted(agg.values(), key=lambda x: (x["count"], x["amount"]), reverse=True)


# =====================================================
# Imported trade P&L review — date filter + grouped estimates
# =====================================================
KST = timezone(timedelta(hours=9))


def safe_trade_float(x, default=0.0):
    try:
        if x is None or x == "":
            return float(default)
        return float(x)
    except Exception:
        return float(default)


def _norm_price_cent(p):
    p = safe_trade_float(p)
    return round(p * 100, 2) if 0 < p <= 1 else round(p, 2)



def parse_pasted_activity(text):
    """Parse copied Polymarket activity text into auto_trades-shaped rows.

    Blocks are split on markdown links [Title](URL). Each block must yield an
    outcome+price line (¢), a shares line (주/shares), and a side word
    (매수/매도/Buy/Sell/Bought/Sold). The +$/−$ figure Polymarket shows is kept
    for display only and never used in P&L — cost is recomputed as shares×price.
    Blocks missing a required field are returned as 'unparsed' so nothing is
    silently invented. Relative times (e.g. '19분 전') are approximated for
    date grouping only.
    """
    rows, unparsed = [], []
    src = str(text or "")
    if not src.strip():
        return rows, {"ok": 0, "buy": 0, "sell": 0, "unparsed": unparsed}

    link_re = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
    links = list(link_re.finditer(src))
    if not links:
        return rows, {
            "ok": 0,
            "buy": 0,
            "sell": 0,
            "unparsed": [t("[제목](주소) 형식 링크를 찾지 못했습니다.", "No [title](url) links found.")],
        }

    now_kst = datetime.now(KST)
    price_re = re.compile(r"([^\n]*?)(\d+(?:\.\d+)?)\s*(?:¢|cents?|c)(?![a-zA-Z])")
    shares_re = re.compile(r"(\d+(?:\.\d+)?)\s*(?:주|shares?)\b", re.IGNORECASE)
    money_re = re.compile(r"([+\-]?)\s*\$\s*([\d,]+(?:\.\d+)?)")
    rel_re = re.compile(
        r"(\d+)\s*(분|시간|시|일|주|개월|달|min|minute|minutes|hour|hours|day|days|week|weeks|month|months)",
        re.IGNORECASE,
    )

    for i, m in enumerate(links):
        title = m.group(1).strip()
        url = m.group(2).strip()
        slug = extract_slug(url)
        block = src[m.end() : (links[i + 1].start() if i + 1 < len(links) else len(src))]
        low = block.lower()

        outcome, price = "", None
        pm = price_re.search(block)
        if pm:
            outcome = re.sub(r"[·•|,\-–—:\s]+$", "", pm.group(1))
            outcome = re.sub(r"^[·•|,\-–—:\s]+", "", outcome).strip()
            try:
                price = float(pm.group(2))
            except ValueError:
                price = None

        shares = None
        sm = shares_re.search(block)
        if sm:
            try:
                shares = float(sm.group(1))
            except ValueError:
                shares = None

        if ("매도" in block) or ("sold" in low) or re.search(r"\bsell\b", low):
            side = "SELL"
        elif ("매수" in block) or ("bought" in low) or re.search(r"\bbuy\b", low):
            side = "BUY"
        else:
            side = None

        shown = ""
        mm = money_re.search(block)
        if mm:
            shown = ("-" if mm.group(1) == "-" else "+") + "$" + mm.group(2)

        d_iso = now_kst.replace(tzinfo=None).isoformat()
        if ("어제" in block) or ("yesterday" in low):
            d_iso = (now_kst - timedelta(days=1)).replace(tzinfo=None).isoformat()
        else:
            rm = rel_re.search(block)
            if rm:
                n, unit = int(rm.group(1)), rm.group(2).lower()
                if unit in ("분", "min", "minute", "minutes"):
                    delta = timedelta(minutes=n)
                elif unit in ("시간", "시", "hour", "hours"):
                    delta = timedelta(hours=n)
                elif unit in ("일", "day", "days"):
                    delta = timedelta(days=n)
                elif unit in ("주", "week", "weeks"):
                    delta = timedelta(weeks=n)
                else:
                    delta = timedelta(days=30 * n)
                d_iso = (now_kst - delta).replace(tzinfo=None).isoformat()

        if price is None or shares is None or shares <= 0 or not outcome or side is None:
            unparsed.append(title or url)
            continue

        key = f"{slug}::{outcome}" if slug else f"{title}|{outcome}"
        rows.append(
            {
                "tx_id": f"paste|{slug}|{outcome}|{side}|{price}|{shares}",
                "d": d_iso,
                "name": title or slug or "Polymarket trade",
                "outcome": outcome,
                "side": side,
                "price": round(price, 2),
                "shares": round(shares, 4),
                "amount": round(shares * price / 100.0, 2),
                "asset": key,
                "token_id": key,
                "src": "paste",
                "shown_pnl": shown,
            }
        )

    buy = sum(1 for r in rows if r["side"] == "BUY")
    sell = sum(1 for r in rows if r["side"] == "SELL")
    return rows, {"ok": len(rows), "buy": buy, "sell": sell, "unparsed": unparsed}


def parse_trade_datetime(tr):
    """Return a KST datetime from normalized auto_trades or raw-like activity rows."""
    if not isinstance(tr, dict):
        return None
    raw = tr.get("d") or tr.get("timestamp") or tr.get("createdAt") or tr.get("created_at") or tr.get("date")
    if raw is None:
        return None
    try:
        n = float(raw)
        if n > 1e12:  # milliseconds
            n /= 1000.0
        if n > 1e9:   # seconds epoch
            return datetime.fromtimestamp(n, tz=timezone.utc).astimezone(KST)
    except (TypeError, ValueError):
        pass
    try:
        s0 = str(raw).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(s0)
        if dt.tzinfo is None:
            # normalize_activity already stores KST-like ISO without tz; treat it as KST.
            dt = dt.replace(tzinfo=KST)
        return dt.astimezone(KST)
    except Exception:
        return None


def filter_trades_by_date(auto_trades, start_date, end_date):
    """Filter imported activity by KST date range. Missing dates are excluded and counted."""
    keep, unknown = [], 0
    for tr in auto_trades or []:
        dt = parse_trade_datetime(tr)
        if dt is None:
            unknown += 1
            continue
        d0 = dt.date()
        if start_date and d0 < start_date:
            continue
        if end_date and d0 > end_date:
            continue
        keep.append(tr)
    return keep, unknown


QF_DEF = [("today", "오늘", "Today"), ("yday", "어제", "Yesterday"),
          ("d7", "최근 7일", "Last 7d"), ("month", "이번 달", "This month"),
          ("all", "전체", "All"), ("custom", "직접 선택", "Custom")]
QF_LABEL = {code: (ko, en) for code, ko, en in QF_DEF}


def _trade_preset(qf, today):
    if qf == "today":
        return today, today
    if qf == "yday":
        yday = today - timedelta(days=1)
        return yday, yday
    if qf == "d7":
        return today - timedelta(days=6), today
    if qf == "month":
        return today.replace(day=1), today
    return None, None


def _on_trade_qf_change():
    # Radio uses internal code values, not translated labels.
    code = st.session_state.get("trade_qf_select", "all")
    st.session_state.trade_qf = code
    start_date, end_date = _trade_preset(code, datetime.now(KST).date())
    if start_date is not None:
        # Callback runs before the next script rerun, so updating widget-backed
        # date state here is safe and prevents stale date_input values.
        st.session_state.trade_start_date = start_date
        st.session_state.trade_end_date = end_date


def _on_trade_date_change():
    # Manual date edits must override any quick-filter preset. Keep the radio
    # widget state in sync so it visibly moves to Custom on the next rerun.
    st.session_state.trade_qf = "custom"
    st.session_state.trade_qf_select = "custom"


def render_trade_date_controls():
    today = datetime.now(KST).date()

    # Defaults and safety checks happen before widget rendering.
    if not isinstance(st.session_state.get("trade_start_date"), date):
        st.session_state.trade_start_date = today - timedelta(days=30)
    if not isinstance(st.session_state.get("trade_end_date"), date):
        st.session_state.trade_end_date = today

    codes = [code for code, _, _ in QF_DEF]
    if st.session_state.get("trade_qf") not in codes:
        st.session_state.trade_qf = "all"
    if st.session_state.get("trade_qf_select") not in codes:
        st.session_state.trade_qf_select = st.session_state.get("trade_qf", "all")

    # If a quick preset is already selected when the page reruns, make sure the
    # displayed date widgets and the actual filter stay aligned.
    if st.session_state.trade_qf_select != st.session_state.trade_qf:
        st.session_state.trade_qf_select = st.session_state.trade_qf
    preset_start, preset_end = _trade_preset(st.session_state.trade_qf, today)
    if preset_start is not None:
        st.session_state.trade_start_date = preset_start
        st.session_state.trade_end_date = preset_end

    st.markdown(f'<div class="eyebrow">{t("기간 선택", "Date range")}</div>', unsafe_allow_html=True)
    st.radio(
        "qf",
        codes,
        format_func=lambda code: t(QF_LABEL[code][0], QF_LABEL[code][1]),
        horizontal=True,
        label_visibility="collapsed",
        key="trade_qf_select",
        on_change=_on_trade_qf_change,
    )

    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input(t("시작일", "Start"), key="trade_start_date", on_change=_on_trade_date_change)
    with c2:
        end_date = st.date_input(t("종료일", "End"), key="trade_end_date", on_change=_on_trade_date_change)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if st.session_state.get("trade_qf", "all") == "all":
        return None, None, t("전체 기간", "All time")
    return start_date, end_date, f"{start_date.isoformat()} ~ {end_date.isoformat()}"

def group_auto_trades_for_pnl(auto_trades):
    """Group fill-level auto trades by market/outcome/token and estimate weighted average P&L."""
    groups = {}
    for tr in auto_trades or []:
        if not isinstance(tr, dict):
            continue
        title = tr.get("title") or tr.get("market") or tr.get("name") or tr.get("slug") or "Unknown"
        outcome = tr.get("outcome") or tr.get("side_outcome") or ""
        tok = tr.get("token_id") or tr.get("asset") or tr.get("assetId") or ""
        key = str(tok).strip() if tok else f"{title}|{outcome}"
        side = str(tr.get("side") or tr.get("type") or "").upper()
        price = _norm_price_cent(tr.get("price"))
        size = safe_trade_float(tr.get("size") or tr.get("shares"))
        usdc = tr.get("usdcSize", tr.get("usdValue", tr.get("amount", None)))
        cash = safe_trade_float(usdc) if usdc is not None else size * (price / 100)
        if size <= 0 and cash <= 0:
            continue
        g = groups.setdefault(key, {
            "market": title, "outcome": outcome, "token_id": tok,
            "bought_shares": 0.0, "sold_shares": 0.0,
            "buy_cost": 0.0, "sell_proceeds": 0.0, "fills": 0,
        })
        g["fills"] += 1
        if side.startswith("B"):
            g["bought_shares"] += size
            g["buy_cost"] += cash
        elif side.startswith("S"):
            g["sold_shares"] += size
            g["sell_proceeds"] += cash
    rows = []
    for key, g in groups.items():
        bs, ss = g["bought_shares"], g["sold_shares"]
        avg_buy = (g["buy_cost"] / bs) if bs > 0 else 0.0
        avg_sell = (g["sell_proceeds"] / ss) if ss > 0 else 0.0
        oversold = ss > bs + 1e-6
        matched_buy_cost = avg_buy * min(ss, bs)
        realized = g["sell_proceeds"] - matched_buy_cost
        remaining = max(bs - ss, 0.0)
        remaining_cost = avg_buy * remaining
        if oversold:
            status = t("확인 필요(매도>매수)", "Verify (sold>bought)")
        elif remaining > 1e-6 and ss > 0:
            status = t("일부 청산", "Partly closed")
        elif remaining > 1e-6:
            status = t("보유 중", "Open")
        else:
            status = t("청산 완료", "Closed")
        rows.append({
            "key": key, "market": g["market"], "outcome": g["outcome"], "token_id": g["token_id"],
            "avg_buy_price": round(avg_buy * 100, 2) if avg_buy <= 1 and avg_buy > 0 else round(avg_buy, 2),
            "avg_sell_price": round(avg_sell * 100, 2) if avg_sell <= 1 and avg_sell > 0 else round(avg_sell, 2),
            "bought_shares": round(bs, 2), "sold_shares": round(ss, 2),
            "buy_cost": round(g["buy_cost"], 2), "sell_proceeds": round(g["sell_proceeds"], 2),
            "realized_pnl": None if oversold else round(realized, 2),
            "remaining_shares": round(remaining, 2), "remaining_cost": round(remaining_cost, 2),
            "status": status, "fills": g["fills"],
        })
    return sorted(rows, key=lambda r: (r["remaining_shares"] > 0, abs(r["realized_pnl"] or 0), r["buy_cost"]), reverse=True)


def summarize_selected_trade_groups(rows, selected_keys):
    sel = [r for r in rows if r["key"] in selected_keys] or rows
    buy_cost = sum(safe_trade_float(r.get("buy_cost"), 0) for r in sel)
    proceeds = sum(safe_trade_float(r.get("sell_proceeds"), 0) for r in sel)
    realized = sum(safe_trade_float(r.get("realized_pnl"), 0) for r in sel if r.get("realized_pnl") is not None)
    remaining = sum(safe_trade_float(r.get("remaining_shares"), 0) for r in sel)
    remaining_cost = sum(safe_trade_float(r.get("remaining_cost"), 0) for r in sel)
    any_unverified = any(r.get("realized_pnl") is None for r in sel)
    return {"buy_cost": buy_cost, "sell_proceeds": proceeds, "realized_pnl": realized,
            "remaining_shares": remaining, "remaining_cost": remaining_cost, "unverified": any_unverified}


def render_trade_pnl_summary(auto_trades, date_label=""):
    rows = group_auto_trades_for_pnl(auto_trades)
    if not rows:
        st.markdown(f'<div class="footnote">{t("해당 기간 자동 거래내역이 없습니다.", "No auto-trades in this range.")}</div>', unsafe_allow_html=True)
        return
    sel_col = t("선택", "Sel")
    df = pd.DataFrame([{
        sel_col: False,
        t("시장", "Market"): r["market"],
        t("선택지", "Outcome"): r["outcome"],
        t("평균 매수", "Avg buy"): cents(r["avg_buy_price"]),
        t("평균 매도", "Avg sell"): cents(r["avg_sell_price"]) if r["sold_shares"] > 0 else "—",
        t("매수 수량", "Bought"): r["bought_shares"],
        t("매도 수량", "Sold"): r["sold_shares"],
        t("매수금", "Buy cost"): money(r["buy_cost"]),
        t("매도금", "Proceeds"): money(r["sell_proceeds"]),
        t("실현손익", "Realized"): t("확인 필요", "Verify") if r["realized_pnl"] is None else signed_money(r["realized_pnl"]),
        t("잔여 수량", "Remaining"): r["remaining_shares"],
        t("상태", "Status"): r["status"],
    } for r in rows])
    disabled_cols = [c for c in df.columns if c != sel_col]
    edited = st.data_editor(df, hide_index=True, use_container_width=True, key="pnl_editor", disabled=disabled_cols)
    selected_keys = [rows[i]["key"] for i, v in enumerate(edited[sel_col].tolist()) if v]
    s0 = summarize_selected_trade_groups(rows, selected_keys)
    label = t("선택 합계", "Selected total") if selected_keys else t("전체 합계", "All total")
    range_label = f" · {date_label}" if date_label else ""
    st.markdown(f'<div class="eyebrow" style="margin-top:16px;">{t("거래내역 기준 추정손익", "Estimated P&L from trade history")} · {label}{range_label}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stats">'
        + stat(t("총 매수금", "Buy cost"), money(s0["buy_cost"]), "")
        + stat(t("총 매도금", "Proceeds"), money(s0["sell_proceeds"]), "")
        + stat(t("실현손익(추정)", "Realized (est)"), signed_money(s0["realized_pnl"]), t("매도금−대응매수원가", "proceeds−matched cost"), "pos" if s0["realized_pnl"] >= 0 else "neg")
        + stat(t("잔여 수량", "Remaining"), f'{s0["remaining_shares"]:.2f}', t(f"원가 {money(s0['remaining_cost'])}", f"cost {money(s0['remaining_cost'])}"))
        + "</div>", unsafe_allow_html=True)
    if s0["unverified"]:
        st.markdown(line(t("일부 항목은 매도 수량이 매수보다 많아 손익이 부정확할 수 있습니다.", "Some rows have sold>bought; P&L may be off."), "w"), unsafe_allow_html=True)
    st.markdown(f'<div class="footnote">{t("추정치입니다. 공식 포트폴리오 손익과 별개이며 아직 합산하지 않습니다.", "Estimate only. Separate from official portfolio P&L; not merged yet.")}</div>', unsafe_allow_html=True)
    with st.expander(t("원본 체결(fill) 보기", "Raw fills")):
        st.markdown(f'<div class="footnote" style="margin:0 0 8px 0;">{t("체결 수는 성과 지표가 아닙니다. 지정가 주문은 여러 fill로 쪼개질 수 있습니다.", "Fill count is not a performance metric. Limit orders may split.")}</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            t("시장", "Market"): r["market"], t("선택지", "Outcome"): r["outcome"],
            t("체결 수", "Fills"): r["fills"], t("상태", "Status"): r["status"],
        } for r in rows]), use_container_width=True, hide_index=True)



def _norm_key(v):
    return "".join(ch.lower() for ch in str(v or "") if ch.isalnum())


def _trade_ts(tr):
    try:
        return datetime.fromisoformat(str(tr.get("d")))
    except Exception:
        return datetime.min


def link_position_to_trades(p, trades):
    """Connect one open position to imported activity using token/asset first, then market+outcome fallback."""
    if not trades:
        return {"matched_trades": 0, "buy_trades": 0, "sell_trades": 0, "buy_amount": 0.0,
                "sell_amount": 0.0, "last_trade": "", "last_buy": "", "recent_add": False,
                "repeat_entry": False, "avg_activity_price": 0.0, "match_note": t("거래내역 없음", "No imported activity")}

    pos_asset = str(p.get("asset") or p.get("token_id") or p.get("conditionId") or "").strip()
    pos_name = _norm_key(p.get("name"))
    pos_out = _norm_key(p.get("outcome"))
    matched = []
    for tr in trades:
        tr_asset = str(tr.get("asset") or tr.get("token_id") or "").strip()
        asset_match = pos_asset and tr_asset and pos_asset == tr_asset
        text_match = pos_name and pos_name in _norm_key(tr.get("name")) and (not pos_out or pos_out in _norm_key(tr.get("outcome")))
        if asset_match or text_match:
            matched.append(tr)

    matched = sorted(matched, key=_trade_ts)
    buys = [x for x in matched if str(x.get("side", "")).upper() == "BUY"]
    sells = [x for x in matched if str(x.get("side", "")).upper() == "SELL"]
    buy_amount = sum(_safe_float(x.get("amount"), 0) for x in buys)
    sell_amount = sum(_safe_float(x.get("amount"), 0) for x in sells)
    buy_shares = sum(_safe_float(x.get("shares"), 0) for x in buys)
    avg_px = (buy_amount / buy_shares * 100) if buy_shares else 0
    last_trade = matched[-1]["d"][:16] if matched else ""
    last_buy_dt = _trade_ts(buys[-1]) if buys else None
    recent_add = bool(last_buy_dt and (datetime.now() - last_buy_dt).total_seconds() <= 60 * 60 * 24)
    repeat_entry = len(buys) >= 3
    note = t(f"연결 거래 {len(matched)}건 · 매수 {len(buys)}회 / 매도 {len(sells)}회",
             f"Linked {len(matched)} fills · {len(buys)} buys / {len(sells)} sells")
    if recent_add:
        note += t(" · 최근 24시간 추가매수", " · added in last 24h")
    if repeat_entry:
        note += t(" · 반복 진입 주의", " · repeated entry")
    return {"matched_trades": len(matched), "buy_trades": len(buys), "sell_trades": len(sells),
            "buy_amount": buy_amount, "sell_amount": sell_amount, "last_trade": last_trade,
            "last_buy": last_buy_dt.isoformat()[:16] if last_buy_dt else "", "recent_add": recent_add,
            "repeat_entry": repeat_entry, "avg_activity_price": avg_px, "match_note": note}


def habit_report(trades):
    """Higher-level trading habit report from imported activity. It does not calculate realized P&L."""
    sm = summarize_activity(trades)
    insights = list(sm.get("insights", []))
    if not trades:
        return {**sm, "habit_level": "i", "habit_title": t("거래 습관 데이터 없음", "No habit data"), "habit_insights": insights}

    by_day = {}
    last_by_market = {}
    fast_reentries = 0
    chase_like = 0
    for tr in sorted(trades, key=_trade_ts):
        dkey = str(tr.get("d") or "")[:10]
        by_day[dkey] = by_day.get(dkey, 0) + 1
        name = str(tr.get("name") or "Unknown")
        side = str(tr.get("side") or "").upper()
        dt = _trade_ts(tr)
        px = _safe_float(tr.get("price"), 0)
        if side == "BUY" and px >= 80:
            chase_like += 1
        prev = last_by_market.get(name)
        if prev and side == "BUY" and prev.get("side") == "BUY":
            gap_min = (dt - prev.get("dt", dt)).total_seconds() / 60
            if 0 <= gap_min <= 180:
                fast_reentries += 1
        last_by_market[name] = {"dt": dt, "side": side}

    max_day = max(by_day.values()) if by_day else 0
    if max_day >= 15 or fast_reentries >= 3:
        level, title = "b", t("과열 거래 가능성 높음", "High chance of overtrading")
    elif max_day >= 8 or fast_reentries >= 1 or chase_like >= 2:
        level, title = "w", t("거래 습관 주의", "Trading habit caution")
    else:
        level, title = "g", t("거래 빈도 관리 가능", "Trading frequency manageable")

    insights.append((level, t(f"최대 하루 거래 {max_day}건 · 빠른 재진입 {fast_reentries}회 · 80¢ 이상 매수 {chase_like}회",
                              f"Max daily trades {max_day} · fast re-entries {fast_reentries} · buys above 80¢ {chase_like}")))
    if fast_reentries:
        insights.append(("w", t("짧은 시간 안의 같은 시장 재매수가 감지됐습니다. 손실 복구/추격매수인지 복기하세요.",
                                "Repeated buys in the same market within a short time were detected. Review whether it was chasing or loss recovery.")))
    if chase_like:
        insights.append(("w", t("80¢ 이상 고가 매수가 있습니다. 작은 추가수익을 위해 큰 금액을 위험에 둔 거래인지 확인하세요.",
                                "Some buys were above 80¢. Check whether you risked too much for limited upside.")))
    return {**sm, "habit_level": level, "habit_title": title, "habit_insights": insights}


def portfolio_card_html(ar):
    pnl_cls = "pos" if ar.get("pnl", 0) >= 0 else "neg"
    return f'''<div class="pf-card">
  <div class="pf-card-head">
    <div>
      <div class="pf-title">{esc(ar.get("name"))}</div>
      <div class="pf-sub">{esc(ar.get("outcome"))}</div>
    </div>
    <span class="state {ar.get("kind", "i")}">{esc(ar.get("title"))}</span>
  </div>
  <div class="pf-big {pnl_cls}">{signed_money(ar.get("pnl", 0))}</div>
  <div class="pf-sub">{t("포지션 손익", "Position P&L")} · {signed_pct(ar.get("roi", 0))}</div>
  <div class="pf-metrics">
    <div class="pf-metric"><div class="k">{t("평가금", "Value")}</div><div class="v">{money(ar.get("value", 0))}</div></div>
    <div class="pf-metric"><div class="k">{t("비중", "Weight")}</div><div class="v">{ar.get("pct", 0):.1f}%</div></div>
    <div class="pf-metric"><div class="k">{t("현재가", "Now")}</div><div class="v">{ar.get("cur", 0):.1f}¢</div></div>
    <div class="pf-metric"><div class="k">{t("평균가", "Avg")}</div><div class="v">{ar.get("buy", 0):.1f}¢</div></div>
    <div class="pf-metric"><div class="k">{t("연결 거래", "Linked")}</div><div class="v">{int(ar.get("matched_trades", 0))}건</div></div>
    <div class="pf-metric"><div class="k">{t("매수 횟수", "Buys")}</div><div class="v">{int(ar.get("buy_trades", 0))}회</div></div>
  </div>
  <div class="pf-note">{esc(ar.get("summary"))}<br><b>{t("거래 연결", "Trade link")}:</b> {esc(ar.get("match_note", t("자동 거래내역 없음", "No imported activity")))}</div>
</div>'''


MIN_SHARES = 1.0   # 이 미만 수량은 dust로 간주
MIN_VALUE = 1.0    # 평가금 $1 미만은 숨김

def is_open_position(it):
    """현재 실제 보유 중인 포지션인지 판단"""
    try:
        size = float(it.get("size", 0))
        cur = float(it.get("curPrice", 0))
        val = float(it.get("currentValue", size * cur))
    except Exception:
        return False
    if it.get("redeemable") is True:
        return False
    if size < MIN_SHARES or val < MIN_VALUE:
        return False
    if cur <= 0.001 or cur >= 0.999:
        return False
    return True


# =====================================================
# Period P&L
# =====================================================
def period_pnl():
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    w = m = y = 0.0
    for tr in st.session_state.trade_log:
        try:
            dt = datetime.fromisoformat(tr["d"])
        except Exception:
            continue
        p = tr.get("profit", 0.0)
        if dt >= week_start: w += p
        if dt.year == now.year and dt.month == now.month: m += p
        if dt.year == now.year: y += p
    return w, m + st.session_state.adj_month, y + st.session_state.adj_year


def portfolio_health(portfolio, cash):
    """Analyze current holdings using only existing portfolio rows. No extra manual inputs."""
    g, c1, c2, blk = size_thresholds()
    pos_value = sum((p.get("shares", 0) or 0) * ((p.get("cur", 0) or 0) / 100) for p in portfolio)
    pos_cost = sum((p.get("inv", 0) or 0) for p in portfolio)
    total_assets = cash + pos_value
    unrealized = pos_value - pos_cost
    unrealized_pct = unrealized / pos_cost * 100 if pos_cost else 0
    exposure_pct = pos_value / total_assets * 100 if total_assets else 0
    cash_pct = cash / total_assets * 100 if total_assets else 0

    rows, values = [], []
    for p in portfolio:
        sh = p.get("shares", 0) or 0
        cur = p.get("cur", 0) or 0
        inv = p.get("inv", 0) or 0
        val = sh * cur / 100
        pnl = val - inv
        roi = pnl / inv * 100 if inv else 0
        pct = val / total_assets * 100 if total_assets else 0
        values.append({"name": p.get("name", ""), "val": val, "pct": pct, "cur": cur, "roi": roi, "pnl": pnl})

    if not portfolio:
        return {"title": t("분석할 보유 포지션이 없습니다", "No holdings to analyze"), "kind": "i",
                "summary": t("지갑에서 포지션을 불러오거나 직접 추가하면 자동 분석이 표시됩니다.", "Import or add positions to see analysis."),
                "lines": [], "exposure_pct": 0, "cash_pct": 100, "unrealized": 0, "unrealized_pct": 0}

    biggest = max(values, key=lambda x: x["val"]) if values else {"name": "", "pct": 0, "val": 0, "cur": 0, "roi": 0}
    losers = [x for x in values if x["roi"] <= -8]
    high_price = [x for x in values if x["cur"] >= 85]
    lottery = [x for x in values if x["cur"] <= 5]

    kind = "g"
    title = t("보유 상황 양호", "Holdings look controlled")
    summary = t("현재 포지션 규모가 개인 리스크 기준 안에서 관리 가능한 편입니다.", "Current position sizes look manageable within your risk profile.")

    if biggest["pct"] >= blk:
        kind, title = "b", t("단일 포지션 과대", "Single position too large")
        summary = t(f"가장 큰 포지션이 총자산의 {biggest['pct']:.1f}%입니다. 내 진입 금지선 {blk:.0f}%를 넘었습니다.",
                    f"Largest position is {biggest['pct']:.1f}% of assets, above your no-entry line {blk:.0f}%.")
    elif exposure_pct >= min(blk * 2, 50):
        kind, title = "b", t("전체 노출 과대", "Total exposure too high")
        summary = t(f"보유 포지션 평가금이 총자산의 {exposure_pct:.1f}%입니다. 신규 진입보다 축소·관망이 우선입니다.",
                    f"Open positions are {exposure_pct:.1f}% of assets. Reduce/watch before adding.")
    elif biggest["pct"] >= c1 or len(losers) >= 2 or high_price:
        kind, title = "w", t("주의 필요", "Needs caution")
        summary = t("일부 포지션의 크기·가격대·손실률을 점검해야 합니다.", "Review size, price zone, or loss rate on some positions.")

    rows.append((kind, summary))
    rows.append(("w" if biggest["pct"] >= c1 else "g",
                 t(f"최대 포지션: {biggest['name']} · {money(biggest['val'])} · 총자산의 {biggest['pct']:.1f}%",
                   f"Largest: {biggest['name']} · {money(biggest['val'])} · {biggest['pct']:.1f}% of assets")))
    rows.append(("g" if unrealized >= 0 else "b",
                 t(f"보유 포지션 손익: {signed_money(unrealized)} ({signed_pct(unrealized_pct)})",
                   f"Unrealized P&L: {signed_money(unrealized)} ({signed_pct(unrealized_pct)})")))
    rows.append(("w" if high_price else "g",
                 t(f"85¢ 이상 고가 포지션: {len(high_price)}개 — 고가 구간은 신규매수보다 익절/축소 판단이 우선입니다.",
                   f"High-price positions 85¢+: {len(high_price)} — prefer take-profit/reduce checks over new buys.")))
    rows.append(("w" if lottery else "g",
                 t(f"5¢ 이하 복권형 포지션: {len(lottery)}개 — 추가매수 금지 원칙이 좋습니다.",
                   f"Lottery-like positions ≤5¢: {len(lottery)} — no-add rule is safer.")))

    return {"title": title, "kind": kind, "summary": summary, "lines": rows,
            "exposure_pct": exposure_pct, "cash_pct": cash_pct,
            "unrealized": unrealized, "unrealized_pct": unrealized_pct}




def analyze_portfolio_position(p, bankroll):
    """Analyze one open holding using current portfolio data only."""
    name = p.get("name", "") or "Polymarket position"
    outcome = p.get("outcome", "") or ""
    sh = _safe_float(p.get("shares"), 0)
    buy = _safe_float(p.get("buy"), 0)
    cur = _safe_float(p.get("cur"), 0)
    inv = _safe_float(p.get("inv"), 0)
    val = sh * cur / 100 if cur else 0
    pnl = val - inv
    roi = pnl / inv * 100 if inv else 0
    pct = val / bankroll * 100 if bankroll else 0

    zone_label, zone_kind, _, zone_note = price_zone(cur)
    size_label, size_kind, _, size_note = size_rule(pct)
    g, c1, c2, blk = size_thresholds()

    if pct >= blk:
        title, kind = t("과대 노출 — 축소 우선", "Oversized — reduce first"), "b"
        summary = t("이 포지션은 내 진입 금지선보다 큽니다. 추가매수보다 일부 축소가 우선입니다.",
                    "This holding is above your no-entry line. Reducing comes before adding.")
    elif roi >= 30 and cur >= 80:
        title, kind = t("수익 구간 — 부분매도 검토", "Profit zone — consider partial sell"), "w"
        summary = t("수익률이 크고 가격도 높은 편입니다. 원금 회수 또는 일부 익절을 검토할 만합니다.",
                    "Profit is strong and price is high. Consider recovering principal or taking partial profit.")
    elif roi <= -35:
        title, kind = t("손실 확대 — 추가매수 금지", "Large loss — no adding"), "b"
        summary = t("손실률이 큽니다. 복구 배팅보다 손절·홀딩 기준을 다시 확인하세요.",
                    "Loss is large. Re-check stop/hold rules instead of chasing.")
    elif cur >= 90:
        title, kind = t("고가 구간 — 신규매수 비추천", "High price — new buys discouraged"), "w"
        summary = t("현재가는 고가 구간입니다. 홀딩은 가능해도 추가 진입은 보수적으로 봐야 합니다.",
                    "Price is high. Holding may be fine, but adding should be conservative.")
    elif cur <= 5:
        title, kind = t("복권형 구간 — 소액 원칙", "Lottery zone — small only"), "w"
        summary = t("초저가 포지션입니다. 추가매수보다 최대 손실을 제한하는 게 중요합니다.",
                    "Very low-price holding. Limit max loss rather than adding.")
    elif pct >= c1:
        title, kind = t("크기 주의 — 비중 점검", "Size caution — review exposure"), "w"
        summary = t("가격 자체보다 포지션 크기가 커지고 있습니다. 다음 진입 전에 전체 노출을 확인하세요.",
                    "Size is becoming the issue. Check total exposure before the next entry.")
    else:
        title, kind = t("관리 가능", "Manageable"), "g"
        summary = t("현재 데이터 기준으로는 과도한 위험 신호가 크지 않습니다.",
                    "Based on current data, no major risk signal stands out.")

    lines_ = [
        ("g" if pnl >= 0 else "b", t(f"현재 손익: {signed_money(pnl)} ({signed_pct(roi)}) · 평가금 {money(val)}",
                                      f"Current P&L: {signed_money(pnl)} ({signed_pct(roi)}) · value {money(val)}")),
        (size_kind, t(f"포지션 크기: 총자산의 {pct:.1f}% · {size_label}",
                      f"Position size: {pct:.1f}% of assets · {size_label}")),
        (zone_kind, t(f"가격 구간: {cur:.1f}¢ · {zone_label}. {zone_note}",
                      f"Price zone: {cur:.1f}¢ · {zone_label}. {zone_note}")),
        ("i", t(f"평균 매수가 {buy:.1f}¢ · 보유 수량 {sh:.2f} · 선택 {outcome}",
                 f"Avg buy {buy:.1f}¢ · shares {sh:.2f} · side {outcome}")),
    ]
    return {"name": name, "outcome": outcome, "title": title, "kind": kind, "summary": summary,
            "value": val, "pnl": pnl, "roi": roi, "pct": pct,
            "cur": cur, "buy": buy, "shares": sh, "investment": inv, "lines": lines_}


# =====================================================
# Masthead + language
# =====================================================
mh_l, mh_r = st.columns([4, 1])
with mh_l:
    st.markdown(
        f"""<div class="masthead">
<div class="name">Memento</div>
<div class="tag">{t("폴리마켓 진입 판단 터미널", "Polymarket entry-decision terminal")}</div>
</div>""", unsafe_allow_html=True)
with mh_r:
    lang_choice = st.radio("lang", ["한국어", "English"],
                           index=0 if st.session_state.lang == "ko" else 1,
                           horizontal=True, label_visibility="collapsed")
    new_lang = "ko" if lang_choice == "한국어" else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

# The app opens directly with a safe default risk profile; no onboarding gate.
# Users can adjust bankroll/risk settings later in Settings · tools.
if st.session_state.profile is None:
    st.session_state.profile = dict(DEFAULT_PROFILE)

# Slim risk chip under the masthead — only the numbers that drive a decision.
prof = profile()
g_, c1_, c2_, blk_ = size_thresholds()
eb_ = effective_bankroll()
exp_limit_ = min(blk_ * 2, 50)
st.markdown(
    f'<div class="mh-chip">'
    f'{t("총자산", "Bankroll")} <b>{money(eb_)}</b>'
    f' · {t("적정", "comfort")} {g_:.0f}% ({money(eb_*g_/100)})'
    f' · {t("진입 금지", "block")} {blk_:.0f}% ({money(eb_*blk_/100)})'
    f' · {t("감정 한도", "emotion cap")} {money(prof["emotional_limit"])}</div>',
    unsafe_allow_html=True)

tab1, tab_ai, tab_pf, tab2, tab3, tab4, tab_set = st.tabs([
    t("진입 판독", "Entry check"),
    t("AI 리서치", "AI research"),
    t("포트폴리오", "Portfolio"),
    t("포지션 관리", "Positions"),
    t("부분매도", "Partial sell"),
    t("거래일지", "Journal"),
    t("설정 · 도구", "Settings · tools"),
])


# =====================================================
# Render: entry result
# =====================================================
def render_entry_result(r):
    if not r:
        st.markdown(
            f"""<div class="quiet">
<div class="q-title">{t("판독 결과가 여기에 표시됩니다", "Your verdict appears here")}</div>
<div class="q-body">{t("오른쪽에서 시장 정보와 투자금을 입력하고<br>판독하기를 누르세요.", "Enter the market details on the right<br>and press Evaluate.")}</div>
</div>""", unsafe_allow_html=True)
        return

    k = verdict_dot(r["level"])
    score_word = t("적절성", "Suitability") if r["level"] != "bad" else t("부적절도", "Unsuitability")
    score_val = r["final_score"] if r["level"] != "bad" else 100 - r["final_score"]

    st.markdown(
        f"""<div class="verdict">
<div class="eyebrow">{t("판정", "Verdict")}</div>
<div class="v-title"><span class="dot {k}"></span>{r["decision"]}</div>
<div class="v-sub">{r["market_name"]} · {score_word} {score_val:.0f}% · {t("규모 제외 순수 가치", "Pure value")} {r["value_score"]:.0f}%</div>
</div>""", unsafe_allow_html=True)

    edge_tone = "pos" if r["edge"] >= 5 else "neg" if r["edge"] < 0 else ""
    pos_tone = "neg" if r["size_kind"] == "b" else ""
    st.markdown(
        '<div class="stats">'
        + stat(t("현재가", "Price"), cents(r["current_price"]), t("시장 implied probability", "Implied probability"))
        + stat("Edge", f"{r['edge']:+.1f}¢", t("내 적정가 대비", "vs fair price"), edge_tone)
        + stat(t("포트폴리오 비중", "Portfolio %"), f"{r['position_pct']:.1f}%", r["size_label"], pos_tone)
        + stat(t("추천 상한선", "Suggested cap"), money(r["rec_cap"]), t(f"투자금 {money(r['stake'])}", f"Stake {money(r['stake'])}"))
        + "</div>",
        unsafe_allow_html=True)

    # ---- meters with explicit verdicts ----
    fs = r["final_score"]
    fs_kind = "g" if fs >= 70 else "w" if fs >= 50 else "b"
    vs = r["value_score"]
    vs_kind = "g" if vs >= 70 else "w" if vs >= 50 else "b"
    pp = min(r["position_pct"], 100)
    pp_kind = r["size_kind"]
    pz_kind = r["zone_kind"]

    st.markdown(
        meter(t("리스크 포함 최종 적절성", "Final suitability incl. risk"), fs, fs_kind, grade_word(fs_kind), unit="%")
        + meter(t("배팅 규모 제외 순수 가치", "Pure value ex-size"), vs, vs_kind, grade_word(vs_kind), unit="%")
        + meter(t("포트폴리오 사용 비중", "Portfolio usage"), pp, pp_kind, r["size_label"], unit="%")
        + meter(t("현재가 위치", "Price position"), r["current_price"], pz_kind, r["zone_label"], unit="¢"),
        unsafe_allow_html=True)

    st.markdown(f'<div class="eyebrow" style="margin-top:22px;">{t("핵심 판단 근거", "Key reasoning")}</div>', unsafe_allow_html=True)
    notes = "".join(line(txt, kk) for kk, txt in r["reasons"])
    if r["fomo_count"] > 0: notes += line(r["fomo_note"], r["fomo_kind"])
    if r["duplicate_pct"] >= size_thresholds()[1]: notes += line(r["exp_note"], r["exp_kind"])
    if r["high_warn"]: notes += line(r["high_warn"], "b")
    st.markdown(notes, unsafe_allow_html=True)

    with st.expander(t("상세 리포트", "Detailed report")):
        st.markdown(
            '<div class="spec">'
            + spec_row(t("진입가격 구간", "Price zone"), f"{t('현재가','Price')} <b>{cents(r['current_price'])}</b> — {r['zone_note']}", r["zone_label"], r["zone_kind"])
            + spec_row(t("배팅금액 · 계좌 생존", "Stake · survival"), f"{t('투자금','Stake')} <b>{money(r['stake'])}</b> / {t('총자산','Portfolio')} <b>{money(r['bankroll'])}</b> · <b>{r['position_pct']:.1f}%</b><br>{r['size_note']}", r["size_label"], r["size_kind"])
            + spec_row(t("북메이커 비교", "Bookmaker check"), f"{t('내 적정가−현재가','Fair−mkt')} <b>{r['my_vs_poly']:+.1f}%p</b> · {t('북메이커−현재가','Book−mkt')} <b>{r['book_vs_poly']:+.1f}%p</b><br>{r['book_note']}", r["book_label"], r["book_kind"])
            + spec_row(t("추천 상한선", "Suggested cap"), f"<b>{money(r['rec_cap'])}</b> · {t('투자금','Stake')} <b>{money(r['stake'])}</b> · {r['confidence']}", r["cap_label"], r["cap_kind"])
            + spec_row(t("손익비", "Risk : reward"), f"{t('목표 도달','At target')} <b>{money(r['target_profit'])}</b> · {t('손절','At stop')} <b>{money(r['stop_loss_amt'])}</b><br>{r['rr_text']}", f"{r['rr']:.2f} : 1", r["rr_kind"])
            + spec_row(t("감정 · FOMO", "Emotion · FOMO"), f"{t('체크','Checks')} <b>{r['fomo_count']}</b> — {r['fomo_note']}", r["fomo_label"], r["fomo_kind"])
            + spec_row(t("중복 노출", "Stacked exposure"), f"<b>{money(r['duplicate_total'])}</b> · <b>{r['duplicate_pct']:.1f}%</b><br>{r['exp_note']}", r["exp_label"], r["exp_kind"])
            + spec_row(t("추격매수 점검", "Chase check"), r["chase_note"], r["chase_label"], r["chase_kind"])
            + spec_row(t("목적 · 시장 유형", "Purpose · type"), f"<b>{r['purpose']}</b> — {r['purpose_note']}<br><b>{r['market_type']}</b> — {r['market_type_note']}", t("구조", "Structure"), "i")
            + "</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="eyebrow" style="margin-top:24px;">{t("수익 · 손실 시나리오", "P&L scenarios")}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="stats">'
            + stat(t("보유 수량", "Shares"), f"{r['shares']:.2f}", t("투자금 ÷ 현재가", "Stake ÷ price"))
            + stat(t("승리 시 순이익", "Profit if win"), money(r["win_profit"]), t("100¢ 상환 기준", "At 100¢"), "pos")
            + stat(t("패배 시 손실", "Loss if lose"), money(-r["stake"]), t("전액 손실 가정", "Total loss"), "neg")
            + stat(t("100¢까지 추가수익", "Left to 100¢"), money(r["additional_to_100"]), t("남은 업사이드", "Upside left"))
            + "</div>", unsafe_allow_html=True)

        summary = (f"{r['market_name']} | {cents(r['current_price'])} → fair {cents(r['fair_price'])} · edge {r['edge']:+.0f}¢ | "
                   f"{money(r['stake'])} · {r['position_pct']:.1f}% | {r['decision']} | {r['final_score']:.0f}% / {r['value_score']:.0f}%")
        st.markdown(f'<div class="eyebrow" style="margin-top:20px;">{t("기록용 한 줄 요약", "One-line summary")}</div>', unsafe_allow_html=True)
        st.code(summary)


def render_position_result(r):
    if not r:
        st.markdown(
            f"""<div class="quiet">
<div class="q-title">{t("포지션 결과가 여기에 표시됩니다", "Position verdict appears here")}</div>
<div class="q-body">{t("오른쪽에서 현재가와 보유 수량을 입력하세요.", "Enter price and shares on the right.")}</div>
</div>""", unsafe_allow_html=True)
        return

    k = verdict_dot(r["level"])
    st.markdown(
        f"""<div class="verdict">
<div class="eyebrow">{t("포지션 판정", "Position verdict")}</div>
<div class="v-title"><span class="dot {k}"></span>{r["decision"]}</div>
<div class="v-sub">{r["name"]} · {t("현재가", "Price")} {cents(r["current_price"])}</div>
</div>""", unsafe_allow_html=True)

    pnl_tone = "pos" if r["pnl"] >= 0 else "neg"
    st.markdown(
        '<div class="stats">'
        + stat(t("현재 평가금", "Current value"), money(r["current_value"]), t("현재가 × 수량", "Price × shares"))
        + stat(t("즉시 매도 손익", "P&L if sold"), signed_money(r["pnl"]), f"{t('수익률','ROI')} {signed_pct(r['roi'])}", pnl_tone)
        + stat(t("100¢ 상환 총액", "Value at 100¢"), money(r["shares"]), t("승리 시", "If it wins"))
        + stat(t("실패 시 손실", "Loss if fails"), money(-r["current_value"]), t("평가금 전액", "Full value"), "neg")
        + "</div>", unsafe_allow_html=True)

    roi_kind = "g" if r["roi"] >= 0 else "b"
    g_, c1_, c2_, blk_ = size_thresholds()
    pp_kind = "b" if r["position_pct"] >= blk_ else "w" if r["position_pct"] >= c1_ else "g"
    zl, zk, _, _ = price_zone(r["current_price"])
    st.markdown(
        meter(t("현재 수익률", "Current ROI"), max(r["roi"], -100), roi_kind, signed_pct(r["roi"]), max_v=100, unit="%")
        + meter(t("포트폴리오 비중", "Portfolio share"), min(r["position_pct"], 100), pp_kind,
                grade_word(pp_kind), unit="%")
        + meter(t("현재가 위치", "Price position"), r["current_price"], zk, zl, unit="¢"),
        unsafe_allow_html=True)

    st.markdown(f'<div class="eyebrow" style="margin-top:20px;">{t("판단 근거", "Reasoning")}</div>', unsafe_allow_html=True)
    notes = "".join(line(x, "g") for x in r["reasons"])
    for w in r["warnings"]:
        kind = "b" if (("금지" in w or "손절" in w or "축소" in w) or any(s in w.lower() for s in ["block", "reduce now"])) else "w"
        notes += line(w, kind)
    st.markdown(notes, unsafe_allow_html=True)

    rows, need = partial_rows(r["shares"], r["current_price"], r["investment"])
    st.markdown(f'<div class="eyebrow" style="margin-top:22px;">{t("부분매도 시나리오", "Partial-sell scenarios")}</div>', unsafe_allow_html=True)
    if need is not None:
        if need <= 100:
            st.markdown(line(t(f"원금 회수 최소 매도 비율: <b>{need:.1f}%</b>", f"Min sell ratio to recover cost: <b>{need:.1f}%</b>"), "g"), unsafe_allow_html=True)
        else:
            st.markdown(line(t(f"100% 팔아도 원금 회수가 어렵습니다 (필요 {need:.1f}%).", f"Even 100% can't recover cost (needs {need:.1f}%)."), "w"), unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# =====================================================
# Tab 1 — Entry
# =====================================================
def _safe_price(v, default=50.0):
    try:
        if v is None or v == "":
            return float(default)
        out = float(v)
        return max(1.0, min(99.0, out))
    except Exception:
        return float(default)


def analyze_entry_row(row, stake, fair_price, confidence, purpose, category=None, subcategory=None, ai_context="", adv=None):
    """Build deterministic entry judgment only. Claude is called only from the AI research tab."""
    mk = t("시장", "Market")
    oc = t("선택지", "Outcome")
    pc = t("현재가 (¢)", "Price (¢)")
    q = row.get(mk, "") or row.get("Market", "") or "Unknown"
    o = row.get(oc, "") or row.get("Outcome", "") or "Yes"
    tok = str(row.get("token_id", "") or "")
    price = _safe_price(row.get(pc, row.get("Price (¢)", None)), 50.0)
    bankroll = effective_bankroll() or profile().get("assets", 1000.0) or 1000.0
    adv = adv or {}
    if category is None:
        category = infer_market_category(st.session_state.get("entry_url", "") or st.session_state.get("explore_url", ""), q)
    if subcategory is None:
        subcategory = infer_market_subcategory(st.session_state.get("entry_url", "") or st.session_state.get("explore_url", ""), q)
    market_type = adv.get("market_type") or "Match Moneyline"

    data = dict(
        market_name=f"{q} — {o}",
        team_a=o,
        team_b="",
        league=str(subcategory or ""),
        category=category,
        subcategory=subcategory,
        current_price=price,
        fair_price=float(fair_price),
        stake=float(stake),
        purpose=purpose,
        market_type=market_type,
        bankroll=bankroll,
        confidence=confidence,
        target_price=float(adv.get("target_price", min(price + 10, 99.0))),
        stop_price=float(adv.get("stop_price", max(price - 10, 1.0))),
        bookmaker_prob=float(adv.get("bookmaker_prob", 0.0)),
        previous_good_price=float(adv.get("previous_good_price", 0.0)),
        duplicate_ml=float(adv.get("duplicate_ml", 0.0)),
        duplicate_game=float(adv.get("duplicate_game", 0.0)),
        duplicate_side=float(adv.get("duplicate_side", 0.0)),
        fomo_count=int(adv.get("fomo_count", 0)),
    )
    result = calculate_entry(data)
    st.session_state.last_entry = result
    st.session_state.prefill_entry = {
        "market_name": f"{q} — {o}",
        "current_price": price,
        "fair_price": float(fair_price),
        "category": category,
        "subcategory": subcategory,
        "market_type": market_type,
        "token_id": tok,
        "outcome": o,
        "note": str(subcategory or ""),
        "stake": float(stake),
    }
    st.session_state.watching_market = {
        "market": f"{q} — {o}",
        "outcome": o,
        "token_id": tok,
        "entry_price": price,
        "fair_price": float(fair_price),
        "stake": float(stake),
        "category": category,
        "subcategory": subcategory,
        "analyzed_at": datetime.now().isoformat(timespec="seconds"),
    }
    return result


def _market_table(rows, section_key):
    """Compact market table. Select one row, then use a single detailed form below.

    Live quotes are intentionally NOT fetched per row — that made one blocking HTTP
    call per outcome on every render. Gamma's last price is shown instantly here, and
    the live bid/ask/spread is fetched only for the market you select (in the result
    panel below). Much faster, especially for events with many outcomes.
    """
    if not rows:
        return
    mk = t("시장", "Market")
    oc = t("선택지", "Outcome")
    pc = t("현재가 (¢)", "Price (¢)")
    st.markdown(
        '<div class="spec-row" style="box-shadow:none;background:transparent;border-color:transparent;padding-bottom:4px;">'
        f'<div class="spec-key">{t("결과 · 시장","Outcome · market")}</div>'
        f'<div class="spec-val" style="color:var(--gray);">{t("현재가 · 시장 implied","Price · implied")}</div>'
        '<div></div></div>', unsafe_allow_html=True)
    for i, m in enumerate(rows):
        q = m.get(mk, "")
        o = m.get(oc, "")
        tok = str(m.get("token_id", "") or "")
        price = m.get(pc, None)
        disp = 50.0 if price is None else float(price)
        cinfo, cprice, cbtn = st.columns([3, 2.2, 1.1])
        cinfo.markdown(
            f'<div class="spec-val" style="padding-top:8px;"><b>{esc(o)}</b>'
            f'<br><span style="color:var(--gray2);font-size:11px;">{esc(q[:72])}</span></div>',
            unsafe_allow_html=True)
        cprice.markdown(
            f'<div class="spec-val" style="padding-top:8px;font-weight:650;">{cents(disp)}'
            f' <span style="color:var(--gray2);font-size:12px;font-weight:500;">· {disp:.0f}%</span></div>',
            unsafe_allow_html=True)
        with cbtn:
            keytok = tok if tok else f"idx_{section_key}_{i}"
            if st.button(t("선택", "Select"), key=f"sel_{section_key}_{i}_{keytok}", use_container_width=True):
                st.session_state._entry_sel = {**m, "_disp_price": disp, "_sel_key": keytok}
                st.session_state._entry_active = None
                st.rerun()


def _selected_entry_form(entry_category, entry_subcategory):
    """Selected market detailed inputs. Important fields are visible, not hidden."""
    sel = st.session_state.get("_entry_sel")
    if not sel:
        st.markdown(f'<div class="footnote">{t("위에서 시장을 선택하면 입력 폼이 열립니다.", "Select a market above to open inputs.")}</div>', unsafe_allow_html=True)
        return
    mk = t("시장", "Market")
    oc = t("선택지", "Outcome")
    q = sel.get(mk, "")
    o = sel.get(oc, "")
    tok = str(sel.get("token_id", "") or "")
    keytok = tok if tok else str(sel.get("_sel_key", "selected"))
    disp = float(sel.get("_disp_price", 50.0) or 50.0)
    st.markdown(f'<div class="eyebrow" style="margin-top:16px;">{t("선택한 시장", "Selected")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="spec-row"><div class="spec-key">{esc(q)}</div><div class="spec-val"><b>{esc(o)}</b> · {cents(disp)}</div><div></div></div>', unsafe_allow_html=True)

    with st.form("sel_entry_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            stake = st.number_input(t("투자금($)", "Stake($)"), min_value=1.0, value=float(min(50.0, (effective_bankroll() or 1000.0) * 0.03) or 50.0), key="sel_stake")
        with c2:
            fair = st.number_input(t("적정가(¢)", "Fair(¢)"), min_value=1.0, max_value=99.0, value=float(min(disp + 5, 99.0)), key="sel_fair")
        with c3:
            conf = st.selectbox(t("확신", "Conviction"), confidence_options(), index=2, key="sel_conf")
        with c4:
            purp = st.selectbox(t("목적", "Purpose"), purpose_options(), key="sel_purpose")
        c5, c6 = st.columns(2)
        with c5:
            target = st.number_input(t("목표가(¢)", "Target(¢)"), min_value=1.0, max_value=100.0, value=float(min(disp + 10, 99.0)), key="sel_target")
        with c6:
            stop = st.number_input(t("손절가(¢)", "Stop(¢)"), min_value=0.0, max_value=99.0, value=float(max(disp - 10, 1.0)), key="sel_stop")
        bk = st.number_input(t("외부배당/북메이커 승률(%)", "Bookmaker prob(%)"), min_value=0.0, max_value=99.0, value=0.0, key="sel_book")
        bk_memo = st.text_input(t("외부배당 출처 메모", "Bookmaker/source memo"), key="sel_bm", placeholder=t("예: Pinnacle T1 -180, Bet365 Gen.G 1.55", "e.g. Pinnacle T1 -180, Bet365 Gen.G 1.55"))
        ai_memo = st.text_area(t("AI 리서치 메모 / 외부정보", "AI research memo / external info"), key="sel_ai_memo", height=84,
                               placeholder=t("최근 10경기·상대전적·순위·라인업·부상·뉴스 링크 붙여넣기", "recent 10, h2h, standings, lineup, injuries, news links"))
        with st.expander(t("고급 (감정·중복노출)", "Advanced (emotion·stacking)")):
            fomo = st.slider(t("감정 체크", "Emotion"), 0, 7, 0, key="sel_fomo")
        go = st.form_submit_button(t("분석", "Analyze"), use_container_width=True)

    if go:
        analyze_entry_row(sel, stake, fair, conf, purp, category=entry_category, subcategory=entry_subcategory, ai_context=ai_memo,
                          adv={"target_price": target, "stop_price": stop, "bookmaker_prob": bk,
                               "bookmaker_source_memo": bk_memo, "ai_extra_context": ai_memo,
                               "fomo_count": fomo, "market_type": "Match Moneyline"})
        st.session_state._entry_active = keytok
        st.rerun()

    if st.session_state.get("_entry_active") == keytok and st.session_state.get("last_entry"):
        render_entry_result(st.session_state.last_entry)
        if st.session_state.get("watching_market", {}).get("token_id"):
            st.markdown(f'<div class="eyebrow" style="margin-top:16px;">{t("실시간 가격 추적", "Live price watch")}</div>', unsafe_allow_html=True)
            render_live_price_panel(st.session_state.watching_market)
        if st.button(t("AI 분석 탭으로 보내기", "Send to AI tab"), key=f"toai_{keytok}", use_container_width=True):
            r = st.session_state.last_entry
            memo_for_ai = str(st.session_state.get("sel_ai_memo", "") or "")
            bk_for_ai = str(st.session_state.get("sel_bm", "") or "")
            st.session_state.ai_pending = {
                "market": sel.get(mk, ""),
                "outcome": sel.get(oc, ""),
                "token_id": tok,
                "market_class": sel.get("market_class", ""),
                "current_price": r.get("current_price", disp),
                "fair_price": r.get("fair_price", disp),
                "edge": r.get("edge", 0.0),
                "category": entry_category,
                "subcategory": entry_subcategory,
                "bookmaker_prob": float(st.session_state.get("sel_book", 0.0) or 0.0),
                "bookmaker_memo": bk_for_ai,
                "ai_memo": memo_for_ai,
                "resolution": str(sel.get("resolution", "") or ""),
                "end_date": str(sel.get("endDate", "") or ""),
                "source_url": st.session_state.get("entry_url", ""),
            }
            st.session_state._ai_memo_cache = memo_for_ai
            st.session_state._ai_bk_cache = bk_for_ai
            st.session_state.ai_text = ""
            st.session_state.ai_error = ""
            st.session_state.ai_last_market_key = ""
            st.success(t("AI 리서치 탭에서 리포트를 생성하세요", "Generate the report in the AI research tab"))


with tab1:
    st.markdown(f'<div class="headline">{t("진입 판독", "Entry check")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="subline">{t("Polymarket URL을 불러와 선택지를 고르고, 필요한 정보를 입력한 뒤 분석하세요.", "Load a Polymarket URL, select an outcome, enter context, then analyze.")}</div>',
        unsafe_allow_html=True,
    )

    u1, u2 = st.columns([4, 1])
    with u1:
        entry_url_value = st.text_input(
            "Polymarket URL",
            value=st.session_state.get("entry_url", ""),
            key="entry_url_input",
            label_visibility="collapsed",
            placeholder="https://polymarket.com/...",
        )
    with u2:
        load_market = st.button(t("시장 불러오기", "Load market"), use_container_width=True, key="entry_load_market")

    if load_market:
        st.session_state.entry_url = entry_url_value
        st.session_state.explore_url = entry_url_value
        slug = extract_slug(entry_url_value)
        if not slug:
            st.markdown(line(t("URL에서 slug를 찾지 못했습니다.", "No slug found in URL."), "b"), unsafe_allow_html=True)
        else:
            try:
                with st.spinner(t("시장 정보를 불러오는 중", "Fetching market data")):
                    payload = fetch_gamma(slug)
                    rows = extract_markets(payload, infer_market_category(entry_url_value, ""))
                st.session_state.entry_raw = payload
                st.session_state.entry_markets = rows
                st.session_state.explore_raw = payload
                st.session_state.explore_markets = rows
                st.session_state._entry_active = None
                st.session_state._entry_sel = None
                if rows:
                    st.markdown(line(t(f"{len(rows)}개 선택지를 불러왔습니다.", f"Loaded {len(rows)} outcomes."), "g"), unsafe_allow_html=True)
                else:
                    st.markdown(line(t("분석 가능한 선택지를 찾지 못했습니다.", "No analyzable outcomes found."), "w"), unsafe_allow_html=True)
            except Exception as e:
                st.session_state.entry_raw = {"error": str(e)}
                st.session_state.entry_markets = []
                st.markdown(line(t(f"불러오기 실패 — {e}", f"Fetch failed — {e}"), "b"), unsafe_allow_html=True)

    rows = st.session_state.get("entry_markets", []) or []
    if not rows:
        st.markdown(
            f"""<div class="quiet">
<div class="q-title">{t('URL을 먼저 불러오세요', 'Load a URL first')}</div>
<div class="q-body">{t('시장 URL을 붙여넣으면 전체 경기/머니라인과 단일경기 선택지를 표로 보여줍니다.', 'Paste a market URL to show full-match moneyline and game outcomes as tables.')}</div>
</div>""",
            unsafe_allow_html=True,
        )
    else:
        default_cat = infer_market_category(st.session_state.get("entry_url", ""), row_get(rows[0], "시장", "Market", ""))
        default_sub = infer_market_subcategory(st.session_state.get("entry_url", ""), row_get(rows[0], "시장", "Market", ""))
        ccat, csub = st.columns([1, 1])
        with ccat:
            cat_options = [t("e스포츠", "Esports"), t("일반 스포츠", "Sports"), t("정치", "Politics"), t("뉴스·이벤트", "News / events"), t("크립토", "Crypto"), t("기타", "Other")]
            if default_cat not in cat_options:
                default_cat = cat_options[-1]
            entry_category = st.selectbox(t("시장 카테고리", "Market category"), cat_options, index=cat_options.index(default_cat), key="entry_url_category")
        with csub:
            entry_subcategory = st.text_input(t("세부종목/분류", "Subcategory"), value=default_sub, key="entry_url_subcategory")

        main_rows = [x for x in rows if x.get("market_class") == "p1_main"]
        game_rows = [x for x in rows if x.get("market_class") == "p2_game"]
        fallback_rows = [x for x in rows if x.get("market_class") == "fallback_binary"]

        if main_rows or fallback_rows:
            st.markdown(f'<div class="eyebrow" style="margin-top:14px;">{t("전체 경기 / 머니라인", "Full match / moneyline")}</div>', unsafe_allow_html=True)
            _market_table(main_rows or fallback_rows, "main")
        else:
            st.markdown(line(t("메인 머니라인을 못 찾았습니다. 단일경기만 표시됩니다.", "No moneyline found; game markets only."), "w"), unsafe_allow_html=True)
        if game_rows:
            with st.expander(t("단일경기 / 맵 승리 (고변동)", "Single game / map (volatile)")):
                _market_table(game_rows, "game")
        _selected_entry_form(entry_category, entry_subcategory)

# =====================================================
# Tab 2 — Position
# =====================================================
with tab2:
    left, right = st.columns([1.05, 0.95], gap="large")

    with right:
        st.markdown(f'<div class="eyebrow" style="margin-top:8px;">{t("입력", "Input")}</div>', unsafe_allow_html=True)
        with st.form("position_form"):
            name = st.text_input(t("거래 이름", "Trade name"), "KT Rolster vs Dplus KIA — Match Winner")
            p1, p2 = st.columns(2)
            with p1:
                avg_buy = st.number_input(t("평균 매수가 (¢)", "Avg buy (¢)"), 1.0, 99.0, 52.4)
                shares_in = st.number_input(t("보유 수량", "Shares"), 0.01, value=1164.12)
                target_price = st.number_input(t("목표가 (¢)", "Target (¢)"), 1.0, 100.0, 60.0)
            with p2:
                current_price_p = st.number_input(t("현재가 (¢)", "Price (¢)"), 1.0, 100.0, 58.0)
                investment = st.number_input(t("투자금 ($)", "Cost ($)"), 1.0, value=610.0)
                stop_price_p = st.number_input(t("손절가 (¢)", "Stop (¢)"), 0.0, 99.0, 45.0)
            fomo_p = st.slider(t("감정 위험 체크 수", "Emotion checks"), 0, 7, 0)
            pos_submit = st.form_submit_button(t("포지션 판독하기", "Evaluate position"), use_container_width=True)

        if pos_submit:
            st.session_state.last_position = evaluate_position(dict(
                name=name, avg_buy=avg_buy, current_price=current_price_p,
                shares=shares_in, investment=investment,
                target_price=target_price, stop_price=stop_price_p,
                bankroll=effective_bankroll(), fomo_count=fomo_p))
            st.rerun()

        if st.session_state.last_position:
            if st.button(t("이 포지션을 포트폴리오에 추가", "Add to Portfolio"), use_container_width=True):
                r = st.session_state.last_position
                st.session_state.portfolio.append(dict(
                    name=r["name"], outcome="", buy=r["avg_buy"],
                    shares=round(r["shares"], 2), inv=round(r["investment"], 2),
                    cur=r["current_price"]))
                st.toast(t("포트폴리오에 추가했습니다", "Added"))

    with left:
        render_position_result(st.session_state.last_position)


# =====================================================
# Tab 3 — Partial sell
# =====================================================
with tab3:
    st.markdown(f'<div class="headline">{t("부분매도 계산기", "Partial-sell calculator")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subline">{t("원금 회수 최소 비율과 비율별 회수금·확정손익을 계산합니다.", "Min sell ratio to recover cost, plus per-ratio recovery and locked P&L.")}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: buy_price = st.number_input(t("매수가 (¢)", "Buy (¢)"), 1.0, 99.0, 16.0, key="pb")
    with c2: cur_price = st.number_input(t("현재가 (¢)", "Price (¢)"), 1.0, 100.0, 73.0, key="pc")
    with c3: inv = st.number_input(t("투자금 ($)", "Cost ($)"), 0.0, value=16.08, key="pi")

    manual = st.checkbox(t("보유 수량 직접 입력", "Enter shares manually"))
    shares_ps = st.number_input(t("보유 수량", "Shares"), 0.0, value=100.0, key="psh") if manual else (inv / (buy_price / 100) if buy_price > 0 else 0)

    if st.button(t("계산하기", "Calculate"), use_container_width=True):
        rows, need = partial_rows(shares_ps, cur_price, inv)
        cur_val = shares_ps * (cur_price / 100)
        add = shares_ps - cur_val
        st.markdown(
            '<div class="stats" style="margin-top:22px;">'
            + stat(t("보유 수량", "Shares"), f"{shares_ps:.2f}", "")
            + stat(t("현재 평가금", "Current value"), money(cur_val), "")
            + stat(t("100¢까지 추가수익", "Left to 100¢"), money(add), "", "pos")
            + stat(t("실패 시 손실", "Loss if fails"), money(-cur_val), "", "neg")
            + "</div>", unsafe_allow_html=True)
        if need is not None:
            if need <= 100:
                st.markdown(line(t(f"원금 회수 최소 매도 비율: <b>{need:.1f}%</b>", f"Min sell ratio: <b>{need:.1f}%</b>"), "g"), unsafe_allow_html=True)
            else:
                st.markdown(line(t(f"100% 팔아도 원금 회수 불가 (필요 {need:.1f}%).", f"Even 100% can't recover cost ({need:.1f}% needed)."), "w"), unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# =====================================================
# Tab 4 — Journal
# =====================================================
with tab4:
    st.markdown(f'<div class="headline">{t("거래일지", "Journal")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subline">{t("직접 기록은 실현손익 계산에 쓰고, API 불러오기는 배팅내역 확인용으로 분리해서 관리합니다.", "Manual entries feed realized P&L; API imports are kept separately for trade-history review.")}</div>', unsafe_allow_html=True)

    with st.expander(t("Polymarket 배팅내역 자동 불러오기", "Import Polymarket trade history"), expanded=False):
        st.markdown(f'<div class="footnote" style="margin:0 0 10px 0;">{t("지갑 주소 기준으로 최근 체결내역을 불러옵니다. 매수/매도 짝짓기는 복잡하므로, 우선 자동 거래내역은 직접 거래일지와 분리해서 보여줍니다.", "Import recent wallet activity. Because pairing buys and sells is complex, auto trades are shown separately from manual journal entries first.")}</div>', unsafe_allow_html=True)
        ac1, ac2 = st.columns([3, 1])
        with ac1:
            st.session_state.wallet_addr = st.text_input(t("지갑 주소", "Wallet address"), value=st.session_state.wallet_addr, placeholder="0x...", key="activity_wallet_addr")
        with ac2:
            act_limit = st.number_input(t("불러올 개수", "Limit"), 10, 300, 100, step=10)
        if st.button(t("거래내역 불러오기", "Import trades"), use_container_width=True):
            a = st.session_state.wallet_addr.strip()
            if not (a.startswith("0x") and len(a) == 42):
                st.markdown(line(t("주소 형식 오류 — 0x로 시작하는 42자 주소인지 확인하세요.", "Bad address — must be 42 chars starting with 0x."), "b"), unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(t("거래내역 불러오는 중", "Fetching activity")):
                        raw = fetch_wallet_activity(a, limit=act_limit)
                    st.session_state.activity_raw = raw
                    items = normalize_activity(raw)
                    added = merge_activity_into_log(items)
                    st.markdown(line(t(f"자동 거래내역 {len(items)}건 확인 · 새로 추가 {added}건", f"Found {len(items)} auto trades · added {added}"), "g"), unsafe_allow_html=True)
                except urllib.error.HTTPError as e:
                    st.markdown(line(t(f"거래내역 불러오기 실패 (HTTP {e.code})", f"Activity import failed (HTTP {e.code})"), "b"), unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(line(t(f"거래내역 불러오기 실패 — {e}", f"Activity import failed — {e}"), "b"), unsafe_allow_html=True)


        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f'<div class="eyebrow">{t("텍스트로 거래내역 붙여넣기", "Paste trade history as text")}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="footnote" style="margin:0 0 8px 0;">'
            f'{t("Polymarket 활동 화면을 그대로 복사해 붙여넣으세요. 매수·매도가 섞여 있어도 시장·선택지별로 평균가와 추정 실현손익을 계산합니다. 화면에 보이는 +$/−$ 숫자는 의미가 확정되지 않아 무시하고, 손익은 가격×수량으로 다시 계산합니다.", "Paste the Polymarket activity screen as-is. Buys and sells can be mixed; we group by market/outcome and estimate average price and realized P&L. The +$/−$ figure shown is ignored (meaning unconfirmed); P&L is recomputed from price × shares.")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        paste_text = st.text_area(
            t("거래내역 텍스트", "Trade history text"),
            value="",
            height=150,
            key="paste_activity_text",
            placeholder="[Will England vs. Croatia end in a draw?](https://polymarket.com/event/.../...-draw)\nYes 30¢\n40.0 주\n+$12.14\n19분 전매수",
            label_visibility="collapsed",
        )
        if st.button(
            t("붙여넣기 분석 · 거래내역에 추가", "Parse paste · add to trade history"),
            use_container_width=True,
            key="paste_activity_btn",
        ):
            parsed_rows, pstat = parse_pasted_activity(paste_text)
            if not parsed_rows and not pstat["unparsed"]:
                st.markdown(line(t("붙여넣은 내용에서 거래를 찾지 못했습니다.", "No trades found in the pasted text."), "w"), unsafe_allow_html=True)
            else:
                st.session_state.auto_trades = [
                    r for r in st.session_state.get("auto_trades", []) if r.get("src") != "paste"
                ]
                st.session_state.auto_trades.extend(parsed_rows)
                if parsed_rows:
                    st.markdown(
                        line(
                            t(
                                f"거래 {pstat['ok']}건 인식 · 매수 {pstat['buy']} / 매도 {pstat['sell']} (다시 붙여넣으면 이전 붙여넣기 내역은 교체됩니다)",
                                f"Parsed {pstat['ok']} trades · buy {pstat['buy']} / sell {pstat['sell']} (re-pasting replaces the previous paste)",
                            ),
                            "g",
                        ),
                        unsafe_allow_html=True,
                    )
                if pstat["unparsed"]:
                    st.markdown(
                        line(
                            t(
                                f"인식 실패 {len(pstat['unparsed'])}건 — 선택지·가격(¢)·수량(주)·매수/매도 표시가 모두 있는지 확인하세요.",
                                f"{len(pstat['unparsed'])} blocks not parsed — each needs outcome, price(¢), shares, and buy/sell.",
                            ),
                            "w",
                        ),
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="footnote">' + " · ".join(esc(x) for x in pstat["unparsed"][:8]) + "</div>",
                        unsafe_allow_html=True,
                    )
        st.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state.auto_trades:
            sd, ed, date_label = render_trade_date_controls()
            filtered_trades, unknown_dates = filter_trades_by_date(st.session_state.get("auto_trades", []), sd, ed)
            if unknown_dates:
                st.markdown(line(t(f"날짜 확인 필요 {unknown_dates}건은 제외되었습니다.", f"{unknown_dates} rows excluded (date unknown)."), "w"), unsafe_allow_html=True)

            render_trade_pnl_summary(filtered_trades, date_label)

            sm = habit_report(filtered_trades)
            if filtered_trades:
                st.markdown(f'<div class="eyebrow" style="margin-top:18px;">{t("거래습관 리포트", "Trading habit report")}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="verdict" style="padding:12px 0 10px 0;border-top:none;">'
                    f'<div class="v-title" style="font-size:26px;"><span class="dot {sm.get("habit_level", "i")}"></span>{esc(sm.get("habit_title", ""))}</div>'
                    f'<div class="v-sub">{t("선택한 기간의 자동 거래내역 기준 행동 패턴입니다. 실현손익에는 합산하지 않습니다.", "Behavior pattern for the selected imported-trade period. Not merged into official P&L.")}</div></div>',
                    unsafe_allow_html=True)
                st.markdown(''.join(f'<div class="trade-insight"><span class="dot {kk}"></span>{esc(txt)}</div>' for kk, txt in sm.get("habit_insights", [])), unsafe_allow_html=True)

            with st.expander(t("기간 내 원본 자동 거래내역", "Raw imported trades in selected range"), expanded=False):
                auto_view = pd.DataFrame([{
                    t("날짜", "Date"): str(tr.get("d") or "")[:16],
                    t("시장", "Market"): tr.get("name") or tr.get("title") or tr.get("market") or "",
                    t("선택", "Outcome"): tr.get("outcome", ""),
                    t("매수/매도", "Side"): tr.get("side", ""),
                    t("가격", "Price"): cents(_norm_price_cent(tr.get("price"))),
                    t("수량", "Shares"): tr.get("shares") or tr.get("size") or 0,
                    t("금액", "Amount"): money(safe_trade_float(tr.get("amount", tr.get("usdcSize", 0)))),
                } for tr in filtered_trades])
                if not auto_view.empty:
                    st.dataframe(auto_view, use_container_width=True, hide_index=True)
                    csv_auto = auto_view.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(t("선택 기간 CSV", "Download selected range CSV"), data=csv_auto, file_name="memento_auto_trades_filtered.csv", mime="text/csv", use_container_width=True)
                else:
                    st.markdown(f'<div class="footnote">{t("선택한 기간의 원본 거래내역이 없습니다.", "No raw trades in the selected range.")}</div>', unsafe_allow_html=True)
                if st.button(t("자동 거래내역 전체 비우기", "Clear all auto trades"), use_container_width=True):
                    st.session_state.auto_trades = []
                    st.session_state.imported_tx_ids = []
                    st.rerun()
        else:
            st.markdown(f'<div class="footnote">{t("거래내역을 불러오면 기간별 추정손익과 거래습관 분석이 여기에 표시됩니다.", "Import activity to see date-based estimated P&L and habit analysis here.")}</div>', unsafe_allow_html=True)

        if st.session_state.get("dev_mode", False):
            with st.expander(t("디버그 — activity raw 응답", "Debug — raw activity response")):
                st.json(st.session_state.activity_raw)

    with st.form("trade_form"):
        t1c, t2c, t3c = st.columns(3)
        with t1c:
            tname = st.text_input(t("거래 이름", "Trade name"), "T1 vs HLE — Match Winner")
            tbuy = st.number_input(t("매수가 (¢)", "Buy (¢)"), 1.0, 99.0, 52.0, key="jb")
        with t2c:
            tsell = st.number_input(t("매도가 (¢)", "Sell (¢)"), 0.0, 100.0, 78.0, key="js")
            tstake = st.number_input(t("투자금 ($)", "Stake ($)"), 1.0, value=50.0, key="jst")
        with t3c:
            tdate = st.date_input(t("거래일", "Date"), value=date.today())
            tmemo = st.text_input(t("메모", "Memo"), "")
        add = st.form_submit_button(t("기록 추가", "Add"), use_container_width=True)

    if add:
        tsh = tstake / (tbuy / 100)
        tp = tsh * (tsell / 100) - tstake
        tr_ = tp / tstake * 100
        st.session_state.trade_log.append({
            "d": datetime.combine(tdate, datetime.min.time()).isoformat(),
            "name": tname, "buy": tbuy, "sell": tsell, "stake": tstake,
            "profit": round(tp, 2), "roi": round(tr_, 1), "memo": tmemo})
        st.toast(f"{signed_money(tp)} ({signed_pct(tr_)})")
        st.rerun()

    if st.session_state.trade_log:
        view = pd.DataFrame([{
            t("날짜", "Date"): tr["d"][:10], t("거래", "Trade"): tr["name"],
            t("매수가", "Buy"): cents(tr["buy"]), t("매도가", "Sell"): cents(tr["sell"]),
            t("투자금", "Stake"): money(tr["stake"]), t("손익", "P&L"): signed_money(tr["profit"]),
            t("수익률", "ROI"): signed_pct(tr["roi"]), t("메모", "Memo"): tr["memo"],
        } for tr in st.session_state.trade_log])
        st.dataframe(view, use_container_width=True, hide_index=True)

        total_realized = sum(tr["profit"] for tr in st.session_state.trade_log)
        k = "g" if total_realized >= 0 else "b"
        st.markdown(line(t(f"거래 {len(st.session_state.trade_log)}건 · 총 실현손익 <b>{signed_money(total_realized)}</b>",
                           f"{len(st.session_state.trade_log)} trades · total <b>{signed_money(total_realized)}</b>"), k), unsafe_allow_html=True)

        csv = view.to_csv(index=False).encode("utf-8-sig")
        cdl, crs = st.columns(2)
        with cdl:
            st.download_button(t("CSV 내려받기", "Download CSV"), data=csv, file_name="memento_trades.csv",
                               mime="text/csv", use_container_width=True)
        with crs:
            if st.button(t("거래일지 비우기", "Clear journal"), use_container_width=True):
                st.session_state.trade_log = []
                st.rerun()
    else:
        st.markdown(f'<div class="footnote">{t("아직 기록된 거래가 없습니다.", "No trades yet.")}</div>', unsafe_allow_html=True)

    with st.expander(t("거래 복기", "Trade review")):
        with st.form("review_form"):
            rv_name = st.text_input(t("어떤 거래?", "Which trade?"),
                st.session_state.trade_log[-1]["name"] if st.session_state.trade_log else "")
            r1, r2 = st.columns(2)
            with r1:
                rv_plan = st.radio(t("계획대로 진입했는가?", "Entered as planned?"), ["Yes", "No"], horizontal=True)
                rv_stop = st.radio(t("손절 기준을 지켰는가?", "Followed stop rule?"), ["Yes", "No"], horizontal=True)
            with r2:
                rv_emo = st.radio(t("감정적으로 진입했는가?", "Entered emotionally?"), ["No", "Yes"], horizontal=True)
                rv_tp = st.radio(t("익절 기준을 지켰는가?", "Followed TP rule?"), ["Yes", "No"], horizontal=True)
            rv_reason = st.text_area(t("진입 이유", "Why did you enter?"), height=70)
            rv_one = st.text_input(t("결과 한 줄 복기", "One-line review"))
            rv_fix = st.text_input(t("다음 거래에서 고칠 점", "Fix for next trade"))
            rv_save = st.form_submit_button(t("복기 저장", "Save review"), use_container_width=True)

        if rv_save:
            st.session_state.reviews.append({
                t("날짜", "Date"): date.today().isoformat(),
                t("거래", "Trade"): rv_name,
                t("계획 진입", "Planned"): rv_plan,
                t("감정 진입", "Emotional"): rv_emo,
                t("손절 준수", "Stop kept"): rv_stop,
                t("익절 준수", "TP kept"): rv_tp,
                t("진입 이유", "Reason"): rv_reason,
                t("복기", "Review"): rv_one,
                t("개선점", "Fix"): rv_fix})
            st.toast(t("저장했습니다", "Saved"))

        if st.session_state.reviews:
            st.dataframe(pd.DataFrame(st.session_state.reviews), use_container_width=True, hide_index=True)


# =====================================================
# Tab — AI research (optional, manual-trigger only)
# =====================================================
with tab_ai:
    st.markdown(f'<div class="headline">{t("AI 리서치", "AI research")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="subline">{t("Claude는 실시간 인터넷이 없어 최근 전적·부상·배당을 직접 가져오지 못합니다. 대신 정산 규칙 해석, 붙여넣은 리서치 정리, 엣지 판단, 진입 전 체크리스트에 집중합니다. 버튼을 눌렀을 때만 호출되어 토큰을 아낍니다.", "Claude has no live internet, so it can’t pull recent form, injuries, or odds itself. It focuses on reading the resolution rules, organizing the notes you paste, framing the edge, and a pre-bet checklist. It runs only when you press the button.")}</div>',
        unsafe_allow_html=True)

    has_key = bool(get_api_key())
    if not has_key:
        st.markdown(line(t("Claude API 키가 없습니다 — 설정 · 도구 탭에서 ANTHROPIC_API_KEY를 등록하세요.", "No Claude API key — add ANTHROPIC_API_KEY in Settings · tools."), "w"), unsafe_allow_html=True)

    pend = st.session_state.get("ai_pending", {}) or {}
    has_pend = bool(pend.get("market"))

    # ---- choose the subject: pending market from Entry, or a manual quick entry ----
    if has_pend:
        src_choice = st.radio(
            t("리서치 대상", "Research subject"),
            ["pending", "manual"],
            format_func=lambda c: t("진입 판독에서 보낸 시장", "Market sent from Entry") if c == "pending" else t("직접 입력", "Enter manually"),
            horizontal=True, key="ai_src_choice", label_visibility="collapsed",
        )
    else:
        src_choice = "manual"
        st.markdown(f'<div class="footnote" style="margin:0 0 8px 0;">{t("진입 판독에서 ‘AI 분석 탭으로 보내기’를 누르면 시장이 자동으로 채워집니다. 또는 아래에 직접 입력하세요.", "Press ‘Send to AI tab’ in Entry to auto-fill a market, or enter one below.")}</div>', unsafe_allow_html=True)

    if src_choice == "pending" and has_pend:
        subj = {
            "market": pend.get("market", ""), "outcome": pend.get("outcome", ""),
            "current_price": float(pend.get("current_price", 0.0) or 0.0),
            "fair_price": float(pend.get("fair_price", 0.0) or 0.0),
            "edge": float(pend.get("edge", 0.0) or 0.0),
            "category": pend.get("category", "기타"), "subcategory": pend.get("subcategory", ""),
            "market_class": pend.get("market_class", ""), "token_id": pend.get("token_id", ""),
            "bookmaker_prob": float(pend.get("bookmaker_prob", 0.0) or 0.0),
            "resolution": str(pend.get("resolution", "") or ""),
            "default_memo": st.session_state.get("_ai_memo_cache", pend.get("ai_memo", "")),
            "default_bk": st.session_state.get("_ai_bk_cache", pend.get("bookmaker_memo", "")),
        }
    else:
        mc1, mc2 = st.columns([3, 1])
        with mc1:
            m_name = st.text_input(t("시장 / 매치", "Market / match"), value=st.session_state.get("ai_manual_name", ""), key="ai_manual_name", placeholder=t("예: T1 vs Gen.G — Match Winner", "e.g. T1 vs Gen.G — Match Winner"))
        with mc2:
            m_out = st.text_input(t("선택 결과", "Outcome"), value=st.session_state.get("ai_manual_out", ""), key="ai_manual_out", placeholder="T1")
        mc3, mc4, mc5 = st.columns(3)
        with mc3:
            m_price = st.number_input(t("현재가 (¢)", "Price (¢)"), 0.0, 100.0, float(st.session_state.get("ai_manual_price", 50.0)), key="ai_manual_price")
        with mc4:
            m_fair = st.number_input(t("내 적정가 (¢)", "My fair (¢)"), 0.0, 100.0, float(st.session_state.get("ai_manual_fair", 50.0)), key="ai_manual_fair")
        with mc5:
            cat_opts = [t("e스포츠", "Esports"), t("일반 스포츠", "Sports"), t("정치", "Politics"), t("뉴스·이벤트", "News / events"), t("크립토", "Crypto"), t("기타", "Other")]
            m_cat = st.selectbox(t("카테고리", "Category"), cat_opts, key="ai_manual_cat")
        m_res = st.text_area(t("정산 규칙 (Polymarket resolution 텍스트 붙여넣기)", "Resolution rules (paste Polymarket resolution text)"), value=st.session_state.get("ai_manual_res", ""), height=70, key="ai_manual_res", placeholder=t("이 시장이 어떻게 정산되는지에 대한 공식 설명", "the official description of how this market resolves"))
        subj = {
            "market": m_name, "outcome": m_out, "current_price": float(m_price),
            "fair_price": float(m_fair), "edge": float(m_fair) - float(m_price),
            "category": m_cat, "subcategory": "", "market_class": "", "token_id": "",
            "bookmaker_prob": 0.0, "resolution": str(m_res or ""),
            "default_memo": st.session_state.get("_ai_memo_cache", ""), "default_bk": st.session_state.get("_ai_bk_cache", ""),
        }

    # ---- subject summary line ----
    if subj["market"]:
        edge_txt = f"Edge {subj['edge']:+.1f}¢" if subj["fair_price"] else t("적정가 미입력", "no fair yet")
        st.markdown(
            f'<div class="spec-row"><div class="spec-key">{esc(subj["market"])}</div>'
            f'<div class="spec-val"><b>{esc(subj["outcome"]) or "—"}</b> · {cents(subj["current_price"])} · {edge_txt} · {esc(str(subj["category"]))}'
            + (f' · {t("정산 규칙 있음", "has resolution text")}' if subj["resolution"] else f' · {t("정산 규칙 없음", "no resolution text")}')
            + '</div><div></div></div>',
            unsafe_allow_html=True)

    # ---- depth + research notes ----
    mode_label = st.selectbox(
        t("리포트 상세도", "Report depth"),
        [t("요약", "Brief"), t("표준", "Standard"), t("상세", "Detailed")],
        index={"brief": 0, "standard": 1, "detailed": 2}.get(st.session_state.get("ai_report_mode", "standard"), 1),
        key="ai_report_mode_label",
    )
    mode = {"요약": "brief", "Brief": "brief", "표준": "standard", "Standard": "standard", "상세": "detailed", "Detailed": "detailed"}.get(mode_label, "standard")
    st.session_state.ai_report_mode = mode

    ai_memo = st.text_area(
        t("리서치 메모 (전적·순위·라인업·부상·뉴스)", "Research notes (form, standings, lineup, injuries, news)"),
        value=subj["default_memo"],
        placeholder=t("여기에 붙여넣은 내용만 근거로 사용합니다. 비우면 정산 규칙 해석과 분석 틀만 제공합니다.", "Only what you paste here is used as evidence. Leave empty for a resolution read and framework only."),
        height=110, key="ai_tab_memo",
    )
    bk_memo = st.text_input(
        t("외부배당 메모", "Bookmaker memo"),
        value=subj["default_bk"],
        placeholder=t("예: Pinnacle T1 -180, Bet365 Gen.G 1.55", "e.g. Pinnacle T1 -180, Bet365 Gen.G 1.55"),
        key="ai_tab_bk_memo",
    )

    subj_id = subj["token_id"] or f'{subj["market"]}|{subj["outcome"]}'
    mkey = f"{subj_id}|{mode}|{ai_memo.strip()}|{bk_memo.strip()}|{subj['fair_price']}|{subj['edge']}|{subj['resolution'][:60]}"
    c1, c2 = st.columns([1, 1])
    gen = c1.button(t("AI 리포트 생성", "Generate report"), use_container_width=True, key="ai_generate_report", disabled=not subj["market"])
    force = c2.button(t("새로 생성", "Force refresh"), use_container_width=True, key="ai_force_report", disabled=not subj["market"])

    if (gen or force) and subj["market"]:
        st.session_state._ai_memo_cache = ai_memo
        st.session_state._ai_bk_cache = bk_memo
        cache = st.session_state.ai_report_cache
        if (not force) and mkey in cache:
            st.session_state.ai_text = cache[mkey]
            st.session_state.ai_error = ""
        else:
            prompt = build_prompt(
                market_name=subj["market"], outcome=subj["outcome"], current_price=subj["current_price"],
                category=subj["category"], sub=subj["subcategory"], ai_context=ai_memo,
                bookmaker_memo=bk_memo, bookmaker_prob=subj["bookmaker_prob"],
                fair_price=subj["fair_price"], edge=subj["edge"], market_class=subj["market_class"],
                resolution=subj["resolution"], report_mode=mode,
            )
            try:
                with st.spinner(t("AI 분석 중", "Analyzing")):
                    txt, err = call_claude(prompt, mode=mode)
            except Exception as e:
                txt, err = None, str(e)
            st.session_state.ai_text = txt or ""
            st.session_state.ai_error = err or ""
            if txt:
                cache[mkey] = txt
        st.session_state.ai_last_market_key = mkey

    if st.session_state.get("ai_text"):
        render_ai_report_json(st.session_state.ai_text)
    elif st.session_state.get("ai_error"):
        err = str(st.session_state.get("ai_error"))
        if err == "no_key":
            st.markdown(line(t("Claude API 키가 없어 생성하지 못했습니다 — 설정 · 도구에서 등록하세요.", "Couldn’t generate — add your Claude API key in Settings · tools."), "w"), unsafe_allow_html=True)
        else:
            st.markdown(line(t("AI 호출에 실패했습니다 — 새로 생성을 눌러 다시 시도하세요.", "The AI call failed — press Force refresh to retry."), "w"), unsafe_allow_html=True)


with tab_pf:
    st.markdown(f'<div class="headline">{t("포트폴리오", "Portfolio")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subline">{t("현재 보유 포지션을 먼저 보고, 그다음 전체 자산 요약과 손익을 확인합니다.", "Open holdings first, then the wallet summary, then P&L.")}</div>', unsafe_allow_html=True)

    # ---- import wallet (read-only) ----
    with st.expander(t("폴리마켓 지갑으로 포지션 불러오기", "Import positions from a Polymarket wallet")):
        st.markdown(f'<div class="footnote" style="margin:0 0 10px 0;">{t("폴리마켓 프로필 주소(0x로 시작)를 붙여넣으면 공개 데이터 API로 현재 보유 포지션을 읽어옵니다. 로그인·서명 없이 조회만 합니다.", "Paste your Polymarket wallet address. We read open positions via the public data API — read-only, no login or signing.")}</div>', unsafe_allow_html=True)
        st.session_state.wallet_addr = st.text_input(t("지갑 주소", "Wallet address"), value=st.session_state.wallet_addr, placeholder="0x...", key="portfolio_wallet_addr")
        if st.button(t("보유 포지션 불러오기", "Import open positions"), use_container_width=True):
            a = st.session_state.wallet_addr.strip()
            if not (a.startswith("0x") and len(a) == 42):
                st.markdown(line(t("주소 형식 오류 — 0x로 시작하는 42자 주소인지 확인하세요.", "Bad address — must be 42 chars starting with 0x."), "b"), unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(t("폴리마켓에서 불러오는 중", "Fetching")):
                        items = fetch_wallet_positions(a)
                    st.session_state.wallet_raw = items
                    try:
                        st.session_state.pnl_raw = fetch_wallet_value(a)
                    except Exception as _pnl_err:
                        st.session_state.pnl_raw = {"error": str(_pnl_err)}
                    open_items = [it for it in items if is_open_position(it)] if isinstance(items, list) else []
                    st.session_state.portfolio = [dict(
                        name=it.get("title") or "Polymarket position",
                        outcome=it.get("outcome", ""),
                        buy=round(_safe_float(it.get("avgPrice"), 0) * 100, 1),
                        shares=round(_safe_float(it.get("size"), 0), 2),
                        inv=round(_safe_float(it.get("initialValue"), 0), 2),
                        cur=round(_safe_float(it.get("curPrice"), 0) * 100, 1),
                        asset=str(it.get("asset") or it.get("tokenId") or it.get("clobTokenId") or it.get("conditionId") or ""),
                    ) for it in open_items]
                    st.toast(t(f"현재 보유 포지션 {len(open_items)}개", f"{len(open_items)} open positions"))
                    st.rerun()
                except urllib.error.HTTPError as e:
                    st.markdown(line(t(f"연결 실패 (HTTP {e.code}) — 주소 확인 필요", f"Failed (HTTP {e.code}) — check address"), "b"), unsafe_allow_html=True)
                except urllib.error.URLError:
                    st.markdown(line(t("응답 없음 — 잠시 후 다시 시도하세요.", "No response — try again later."), "b"), unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(line(t(f"불러오기 실패 — {e}", f"Import failed — {e}"), "b"), unsafe_allow_html=True)

    if st.session_state.get("dev_mode", False):
        with st.expander(t("디버그 — positions raw 응답", "Debug — raw positions response")):
            st.json(st.session_state.wallet_raw)
        with st.expander(t("디버그 — profile/value raw 응답", "Debug — profile/value raw response")):
            st.json(st.session_state.pnl_raw)

    # ---- capital inputs (drive every calculation; manual cash is source of truth) ----
    with st.expander(t("내 자금 입력 (현금 · 입금 · 출금)", "My capital (cash · deposits · withdrawals)"), expanded=not bool(st.session_state.portfolio)):
        pf_i1, pf_i2, pf_i3 = st.columns(3)
        with pf_i1:
            st.session_state.cash = st.number_input(t("현금 보유량 (USDC, $)", "Cash balance (USDC, $)"), 0.0, value=float(st.session_state.cash), key="cash_input")
        with pf_i2:
            st.session_state.deposits = st.number_input(t("총 입금액 ($)", "Total deposits ($)"), 0.0, value=float(st.session_state.deposits), key="deposit_input")
        with pf_i3:
            st.session_state.withdrawals = st.number_input(t("총 출금액 ($)", "Total withdrawals ($)"), 0.0, value=float(st.session_state.withdrawals), key="withdrawal_input")
        st.markdown(f'<div class="footnote" style="margin-top:4px;">{t("현금은 수동 입력값이 기준입니다. 입금·출금 모두 양수로 입력하세요.", "Manual cash is the source of truth. Enter both deposits and withdrawals as positive values.")}</div>', unsafe_allow_html=True)

    # ---- shared figures ----
    cash = float(st.session_state.cash)
    pos_value = sum((p.get("shares", 0) or 0) * ((p.get("cur", 0) or 0) / 100) for p in st.session_state.portfolio)
    pos_cost = sum((p.get("inv", 0) or 0) for p in st.session_state.portfolio)
    total_assets = cash + pos_value
    bankroll_for_positions = total_assets if total_assets > 0 else prof["assets"]

    # ================= 1) OPEN POSITIONS FIRST =================
    st.markdown(f'<div class="eyebrow">{t("현재 보유 포지션", "Open positions")}</div>', unsafe_allow_html=True)
    if st.session_state.portfolio:
        cards = []
        for p in st.session_state.portfolio:
            ar = analyze_portfolio_position(p, bankroll_for_positions)
            ar.update(link_position_to_trades(p, st.session_state.auto_trades))
            cards.append(portfolio_card_html(ar))
        st.markdown('<div class="pf-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="footnote">{t("카드는 현재가·평균가·수량·투자금만으로 자동 판단합니다. 아래 편집표에서 값을 고치면 즉시 다시 계산됩니다.", "Cards use price, average, shares and cost only. Edit the table below to recalculate instantly.")}</div>', unsafe_allow_html=True)

        with st.expander(t("보유 포지션 편집표", "Edit open positions table"), expanded=False):
            df = pd.DataFrame(st.session_state.portfolio)
            col_cfg = {
                "name": st.column_config.TextColumn(t("시장", "Market")),
                "outcome": st.column_config.TextColumn(t("선택", "Side")),
                "buy": st.column_config.NumberColumn(t("평균 매수가 (¢)", "Avg buy (¢)"), format="%.1f"),
                "shares": st.column_config.NumberColumn(t("수량", "Shares"), format="%.2f"),
                "inv": st.column_config.NumberColumn(t("투자금 ($)", "Cost ($)"), format="%.2f"),
                "cur": st.column_config.NumberColumn(t("현재가 (¢)", "Now (¢)"), format="%.1f"),
                "asset": st.column_config.TextColumn(t("토큰/자산 ID", "Token/asset ID")),
            }
            edited = st.data_editor(df, column_config=col_cfg, use_container_width=True,
                                    hide_index=True, num_rows="dynamic", key="pf_editor")
            st.session_state.portfolio = edited.to_dict("records")

        with st.expander(t("포지션별 핵심 판단", "Per-position verdicts"), expanded=False):
            for p in st.session_state.portfolio:
                ar = analyze_portfolio_position(p, bankroll_for_positions)
                ar.update(link_position_to_trades(p, st.session_state.auto_trades))
                st.markdown(line(f'<b>{esc(ar["name"])}</b> — {esc(ar["title"])} · {esc(ar["summary"])} · {esc(ar.get("match_note", ""))}', ar["kind"]), unsafe_allow_html=True)
    else:
        st.markdown(
            f"""<div class="quiet" style="padding:36px 20px;">
<div class="q-title">{t("등록된 포지션이 없습니다", "No positions yet")}</div>
<div class="q-body">{t("위에서 지갑으로 불러오거나, 아래에서 직접 추가하세요.", "Import via wallet above, or add one manually below.")}</div>
</div>""", unsafe_allow_html=True)

    with st.expander(t("수동으로 포지션 추가", "Add a position manually"), expanded=False):
        with st.form("add_pos"):
            a1, a2, a3 = st.columns(3)
            with a1:
                np_name = st.text_input(t("시장 이름", "Market name"), "")
                np_out = st.text_input(t("선택한 결과", "Outcome"), "")
            with a2:
                np_buy = st.number_input(t("평균 매수가 (¢)", "Avg buy (¢)"), 0.1, 99.9, 50.0)
                np_cur = st.number_input(t("현재가 (¢)", "Now (¢)"), 0.1, 100.0, 50.0)
            with a3:
                np_shares = st.number_input(t("보유 수량", "Shares"), 0.0, value=0.0)
                np_inv = st.number_input(t("투자금 ($)", "Cost ($)"), 0.0, value=0.0)
            add_pos = st.form_submit_button(t("포지션 추가", "Add position"), use_container_width=True)

        if add_pos:
            if not np_name.strip():
                st.markdown(line(t("시장 이름을 입력해주세요.", "Please enter a market name."), "w"), unsafe_allow_html=True)
            else:
                shares_v = np_shares if np_shares > 0 else (np_inv / (np_buy / 100) if np_buy > 0 else 0)
                inv_v = np_inv if np_inv > 0 else shares_v * (np_buy / 100)
                st.session_state.portfolio.append(dict(name=np_name, outcome=np_out, buy=np_buy,
                                                       shares=round(shares_v, 2), inv=round(inv_v, 2), cur=np_cur, asset=""))
                st.rerun()

    # ================= 2) PORTFOLIO SUMMARY =================
    pos_value = sum((p.get("shares", 0) or 0) * ((p.get("cur", 0) or 0) / 100) for p in st.session_state.portfolio)
    pos_cost = sum((p.get("inv", 0) or 0) for p in st.session_state.portfolio)
    wallet_value = cash + pos_value
    deposits = st.session_state.deposits
    withdrawals = st.session_state.withdrawals
    net_profit = cash + pos_value + withdrawals - deposits
    roi = net_profit / deposits * 100 if deposits else None
    wallet_gap = withdrawals - deposits

    ph = portfolio_health(st.session_state.portfolio, cash)
    st.markdown(f'<div class="eyebrow" style="margin-top:8px;">{t("전체 포트폴리오 판단", "Overall portfolio verdict")}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="verdict" style="padding-top:18px;">'
        f'<div class="v-title" style="font-size:28px;"><span class="dot {ph["kind"]}"></span>{ph["title"]}</div>'
        f'<div class="v-sub">{ph["summary"]}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eyebrow">{t("자산 요약", "Wallet summary")}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stats">'
        + stat(t("현금", "Cash"), money(cash), "USDC")
        + stat(t("포지션 평가금", "Position value"), money(pos_value), t(f"원금 {money(pos_cost)}", f"cost {money(pos_cost)}"))
        + stat(t("총 지갑가치", "Wallet value"), money(wallet_value), t("현금+포지션", "cash+pos"))
        + stat(t("실제 누적손익", "Net profit"), signed_money(net_profit), (signed_pct(roi) if roi is not None else "—"), "pos" if net_profit >= 0 else "neg")
        + "</div>"
        + '<div class="stats three">'
        + stat(t("전체 포지션 노출", "Total exposure"), f"{ph['exposure_pct']:.1f}%", t("평가금 / 총자산", "Value / assets"), "neg" if ph['exposure_pct'] >= blk_ else "")
        + stat(t("현금 비중", "Cash ratio"), f"{ph['cash_pct']:.1f}%", t("현금 / 총자산", "Cash / assets"))
        + stat(t("지갑-성과 차이", "Wallet-performance gap"), signed_money(wallet_gap), t("출금/추가입금 영향", "Deposits/withdrawals effect"), "pos" if wallet_gap >= 0 else "neg")
        + "</div>", unsafe_allow_html=True)
    if ph["lines"]:
        st.markdown("".join(line(txt, kk) for kk, txt in ph["lines"]), unsafe_allow_html=True)

    # ================= 3) P&L =================
    st.markdown(f'<div class="eyebrow" style="margin-top:22px;">{t("손익 요약", "P&L summary")}</div>', unsafe_allow_html=True)
    st.session_state.profile_pnl = calc_profile_pnl(st.session_state.portfolio, st.session_state.cash, st.session_state.wallet_raw, st.session_state.pnl_raw)
    render_profile_pnl_dashboard(st.session_state.profile_pnl)

    st.markdown(f'<div class="eyebrow">{t("기간별 실현손익", "Realized P&L by period")}</div>', unsafe_allow_html=True)
    with st.expander(t("앱 사용 전 손익 보정 (이미 번 돈 반영)", "Pre-app P&L adjustment (count earlier gains)")):
        st.markdown(f'<div class="footnote" style="margin:0 0 10px 0;">{t("앱을 쓰기 전에 이미 번(잃은) 금액을 더해 이번 달·올해 손익에 반영합니다.", "Add gains/losses made before using this app, so monthly/yearly totals are accurate.")}</div>', unsafe_allow_html=True)
        j1, j2 = st.columns(2)
        with j1:
            st.session_state.adj_month = st.number_input(t("이번 달 보정 ($)", "This-month adjustment ($)"), value=float(st.session_state.adj_month))
        with j2:
            st.session_state.adj_year = st.number_input(t("올해 보정 ($)", "This-year adjustment ($)"), value=float(st.session_state.adj_year))

    w, m, y = period_pnl()
    def pct_of_start(v):
        sc = (profile().get("start_capital", 0) or profile().get("assets", 0) or 0)
        return signed_pct(v / sc * 100) if sc else "—"
    st.markdown(
        '<div class="stats three">'
        + stat(t("이번 주", "This week"), signed_money(w), pct_of_start(w), "pos" if w >= 0 else "neg")
        + stat(t("이번 달", "This month"), signed_money(m), pct_of_start(m), "pos" if m >= 0 else "neg")
        + stat(t("올해", "This year"), signed_money(y), pct_of_start(y), "pos" if y >= 0 else "neg")
        + "</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="footnote">{t("퍼센트는 시작 자금 기준입니다. 자동 거래내역은 아직 손익 집계에 합산하지 않고, 직접 거래일지와 보정값만 합산합니다.", "Percentages are vs starting capital. Auto-imported activity is not yet paired into realized P&L; only manual journal entries and adjustments are counted.")}</div>', unsafe_allow_html=True)


# =====================================================
# Tab — Settings · tools
# =====================================================
with tab_set:
    st.markdown(f'<div class="headline">{t("설정 · 도구", "Settings · tools")}</div>', unsafe_allow_html=True)

    # ---- Claude API test ----
    st.markdown(f'<div class="eyebrow">{t("Claude API 상태", "Claude API status")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="footnote" style="margin:0 0 10px 0;">{t("API 키는 코드에 직접 넣지 말고 Streamlit Secrets의 ANTHROPIC_API_KEY에 저장하세요.", "Do not hard-code keys. Save it as ANTHROPIC_API_KEY in Streamlit Secrets.")}</div>', unsafe_allow_html=True)
    if st.button(t("Claude API 연결 테스트", "Test Claude API"), use_container_width=True):
        test_text, test_err = call_claude(t("한 문장으로 '연결 성공'이라고 답해.", "Reply with one sentence: connection successful."))
        if test_err:
            st.markdown(line(t(f"Claude API 실패 — {test_err}", f"Claude API failed — {test_err}"), "b"), unsafe_allow_html=True)
        else:
            st.markdown(line(t("Claude API 연결 성공", "Claude API connection successful"), "g"), unsafe_allow_html=True)
            st.caption(test_text)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- developer mode ----
    st.markdown(f'<div class="eyebrow">{t("개발자 모드", "Developer mode")}</div>', unsafe_allow_html=True)
    st.session_state.dev_mode = st.checkbox(
        t("디버그/Raw API 응답 보기", "Show debug / raw API responses"),
        value=bool(st.session_state.get("dev_mode", False)),
        help=t("일반 사용 시 꺼두면 포트폴리오와 거래내역 화면이 더 깔끔해집니다.", "Keep this off for a cleaner portfolio and journal UI."),
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- risk profile ----
    st.markdown(f'<div class="eyebrow">{t("내 리스크 프로필", "My risk profile")}</div>', unsafe_allow_html=True)
    with st.form("profile_form"):
        s1, s2 = st.columns(2)
        with s1:
            pf_assets = st.number_input(t("총자산 ($) — 포트폴리오 미사용 시 기준값", "Total assets ($) — fallback when portfolio empty"), 1.0, value=float(prof["assets"]))
            pf_start = st.number_input(t("시작 자금 ($)", "Starting capital ($)"), 1.0, value=float(prof["start_capital"]))
            pf_emotional = st.number_input(t("감정 한도 ($)", "Emotional cap ($)"), 1.0, value=float(prof["emotional_limit"]))
        with s2:
            pf_max = st.slider(t("적정 배팅 비율 (%)", "Comfort bet ratio (%)"), 1, 30, int(prof["max_pct"]))
            pf_block = st.slider(t("진입 금지선 (%)", "No-entry line (%)"), 5, 40, int(prof["block_pct"]))
        save_prof = st.form_submit_button(t("저장", "Save"), use_container_width=True)

    if save_prof:
        p = dict(prof)
        p.update(assets=pf_assets, start_capital=pf_start, emotional_limit=pf_emotional,
                 max_pct=float(pf_max), block_pct=float(max(pf_block, pf_max + 2)))
        st.session_state.profile = p
        st.toast(t("저장했습니다", "Saved"))
        st.rerun()

    if st.button(t("리스크 기준 기본값으로 초기화", "Reset risk defaults"), use_container_width=True):
        st.session_state.profile = dict(DEFAULT_PROFILE)
        st.rerun()

    st.markdown(
        f'<div class="footnote">{t(f"현재 적용 — 적정 {g_:.0f}% · 주의 {c1_:.0f}% · 위험 {c2_:.0f}% · 진입 금지 {blk_:.0f}% · 시스템 실패 50% / 감정 한도 {money(prof['emotional_limit'])} · 강한 경고 {money(prof['emotional_limit']*2)} · 시스템 실패 {money(prof['emotional_limit']*4)}", f"Active — comfort {g_:.0f}% · caution {c1_:.0f}% · risk {c2_:.0f}% · block {blk_:.0f}% · failure 50% / cap {money(prof['emotional_limit'])} · strong warning {money(prof['emotional_limit']*2)} · failure {money(prof['emotional_limit']*4)}")}</div>',
        unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- URL helper ----
    st.markdown(f'<div class="eyebrow">{t("Polymarket URL 도우미", "Polymarket URL helper")}</div>', unsafe_allow_html=True)
    url = st.text_input("Polymarket URL", "https://polymarket.com/event/")
    if st.button(t("시장 정보 불러오기", "Fetch market info"), use_container_width=True):
        slug = extract_slug(url)
        if not slug:
            st.markdown(line(t("URL에서 slug를 찾지 못했습니다.", "Couldn't find a slug."), "b"), unsafe_allow_html=True)
        else:
            try:
                with st.spinner(t("불러오는 중", "Fetching")):
                    payload = fetch_gamma(slug)
                rows = extract_markets(payload, infer_market_category(url, ""))
                st.session_state.url_rows = rows
                if not rows:
                    st.markdown(line(t("시장을 찾지 못했습니다. /event/ URL인지 확인해주세요.", "No markets found. Check it's an /event/ URL."), "w"), unsafe_allow_html=True)
            except Exception as e:
                st.markdown(line(t(f"불러오기 실패 — {e}", f"Fetch failed — {e}"), "b"), unsafe_allow_html=True)
    if st.session_state.url_rows:
        st.dataframe(pd.DataFrame(st.session_state.url_rows), use_container_width=True, hide_index=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---- backup ----
    st.markdown(f'<div class="eyebrow">{t("백업 · 복원", "Backup · restore")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="footnote" style="margin:0 0 10px 0;">{t("새로고침하면 데이터가 사라집니다. 백업을 내려받아 두세요. 프로필도 함께 저장됩니다.", "Data is lost on refresh. Download a backup — your profile is included.")}</div>', unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        backup = {"profile": st.session_state.profile, "cash": st.session_state.cash,
                  "deposits": st.session_state.deposits, "withdrawals": st.session_state.withdrawals,
                  "portfolio": st.session_state.portfolio, "trade_log": st.session_state.trade_log,
                  "auto_trades": st.session_state.auto_trades, "wallet_addr": st.session_state.wallet_addr,
                  "imported_tx_ids": st.session_state.imported_tx_ids,
                  "watchlist": st.session_state.watchlist, "order_candidates": st.session_state.order_candidates,
                  "pnl_raw": st.session_state.pnl_raw, "profile_pnl": st.session_state.profile_pnl,
                  "explore_url": st.session_state.explore_url, "explore_markets": st.session_state.explore_markets,
                  "prefill_entry": st.session_state.prefill_entry,
                  "dev_mode": st.session_state.dev_mode,
                  "adj_month": st.session_state.adj_month, "adj_year": st.session_state.adj_year,
                  "reviews": st.session_state.reviews}
        st.download_button(t("백업 내려받기 (JSON)", "Download backup (JSON)"),
                           data=json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name="memento_backup.json", mime="application/json", use_container_width=True)
    with bc2:
        up = st.file_uploader(t("백업 불러오기", "Restore backup"), type=["json"], label_visibility="collapsed")
        if up is not None:
            try:
                data = json.loads(up.read().decode("utf-8"))
                st.session_state.profile = data.get("profile") or st.session_state.profile
                st.session_state.cash = float(data.get("cash", 0))
                st.session_state.deposits = float(data.get("deposits", 0))
                st.session_state.withdrawals = float(data.get("withdrawals", 0))
                st.session_state.dev_mode = bool(data.get("dev_mode", False))
                st.session_state.portfolio = data.get("portfolio", [])
                st.session_state.trade_log = data.get("trade_log", [])
                st.session_state.auto_trades = data.get("auto_trades", [])
                st.session_state.wallet_addr = data.get("wallet_addr", "")
                st.session_state.imported_tx_ids = data.get("imported_tx_ids", [])
                st.session_state.watchlist = data.get("watchlist", [])
                st.session_state.order_candidates = data.get("order_candidates", [])
                st.session_state.pnl_raw = data.get("pnl_raw", {})
                st.session_state.profile_pnl = data.get("profile_pnl", {})
                st.session_state.adj_month = float(data.get("adj_month", 0))
                st.session_state.adj_year = float(data.get("adj_year", 0))
                st.session_state.reviews = data.get("reviews", [])
                st.toast(t("복원했습니다", "Restored"))
                st.rerun()
            except Exception:
                st.markdown(line(t("백업 파일을 읽지 못했습니다.", "Could not read backup."), "b"), unsafe_allow_html=True)
