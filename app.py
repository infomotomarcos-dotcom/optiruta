import streamlit as st
import requests
import pandas as pd
import math
from datetime import datetime
from urllib.parse import quote
from streamlit_geolocation import streamlit_geolocation

# ============================================================
# OPTIRUTA DELIVERY - INTERFAZ CLARA AZUL Y ORO (LUQUE)
# Mantiene la API de Google Apps Script de la version anterior.
# ============================================================

st.set_page_config(
    page_title="OptiRuta Delivery",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root { color-scheme: light !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background:#F5F7FB !important; color:#17243A !important;
}
[data-testid="stHeader"] { background:rgba(245,247,251,.94) !important; }
[data-testid="stMainBlockContainer"] { max-width:1480px; padding-top:3.8rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#FFFFFF !important; border-right:1px solid #DCE4EF !important; }
[data-testid="stSidebar"] > div:first-child { padding-top:1.2rem; }
html, body, p, li, label, span, div { color:inherit; }
[data-testid="stMain"] p, [data-testid="stMain"] li { color:#34445B !important; }
h1,h2,h3,h4,[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3 {
  color:#0750B8 !important; font-weight:850 !important; letter-spacing:-.025em;
}
h1 { font-size:2.15rem !important; }
h2 { font-size:1.55rem !important; }
h3 { font-size:1.15rem !important; }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label,
.stMultiSelect label,.stDateInput label,.stTimeInput label,.stRadio label,
.stCheckbox label,.stSlider label,.stFileUploader label,
[data-testid="stForm"] label,[data-testid="stForm"] label * {
  color:#1C2D45 !important; opacity:1 !important; font-weight:700 !important;
}
input,textarea,[data-baseweb="select"] *,[data-baseweb="input"] *,[data-baseweb="textarea"] *,
[data-testid="stDateInput"] input {
  background:#FFFFFF !important; color:#17243A !important; -webkit-text-fill-color:#17243A !important;
  border-color:#C8D4E3 !important; opacity:1 !important;
}
input::placeholder,textarea::placeholder { color:#718096 !important; -webkit-text-fill-color:#718096 !important; opacity:1 !important; }
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] * { color:#64748B !important; opacity:1 !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background:#FFFFFF !important; border:1px solid #DFE6EF !important; border-radius:18px !important; box-shadow:0 5px 18px rgba(21,47,82,.045); }
[data-testid="stMetric"] { background:#FFFFFF !important; border:1px solid #DFE6EF !important; border-radius:18px !important; padding:16px 18px !important; box-shadow:0 5px 18px rgba(21,47,82,.045); }
[data-testid="stMetricLabel"] { color:#52627A !important; font-weight:700 !important; }
[data-testid="stMetricValue"] { color:#0750B8 !important; font-weight:900 !important; }
div.stButton > button:not([kind="secondary"]), div.stFormSubmitButton > button, .stLinkButton a {
  background:#0750B8 !important; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
  border:1px solid #0750B8 !important; border-radius:12px !important; min-height:46px !important;
  padding:.55rem 1rem !important; font-weight:800 !important; font-size:15px !important;
  box-shadow:0 3px 8px rgba(23,74,145,.12);
}
div.stButton > button:not([kind="secondary"]) *, div.stFormSubmitButton > button *, .stLinkButton a * {
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}
div.stButton > button:not([kind="secondary"]):hover, div.stFormSubmitButton > button:hover, .stLinkButton a:hover {
  background:#043B89 !important; border-color:#E9A817 !important; color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
}
div.stButton > button:not([kind="secondary"]):hover *, div.stFormSubmitButton > button:hover *, .stLinkButton a:hover * {
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}
button[kind="secondary"] { background:#FFFFFF !important; color:#0750B8 !important; -webkit-text-fill-color:#0750B8 !important; border:1px solid #B8C9DE !important; }
button[kind="secondary"] * { color:#0750B8 !important; -webkit-text-fill-color:#0750B8 !important; }
[data-testid="stDataFrame"] { border:1px solid #DCE4EF !important; border-radius:14px !important; overflow:hidden; }
[data-testid="stForm"] { background:#FFFFFF; border:1px solid #E0E7F0; border-radius:18px; padding:1.1rem 1.2rem .7rem; }
hr { border-color:#E0E7F0 !important; }
.optiruta-top { background:linear-gradient(115deg,#0750B8 0%,#0750B8 72%,#E9A817 72%,#E9A817 100%); border-radius:20px; padding:28px 28px; color:#FFFFFF; margin-bottom:22px; box-shadow:0 8px 22px rgba(18,59,112,.12); animation: optirutaEntrada .9s ease-out both; }
.optiruta-top * { color:#FFFFFF !important; }
.optiruta-brand { font-size:clamp(42px, 5vw, 66px); font-weight:950; letter-spacing:3px; line-height:1.08; animation: optirutaLogo .85s cubic-bezier(.2,.8,.2,1) both; text-shadow:0 3px 10px rgba(0,0,0,.12); }
@keyframes optirutaEntrada { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes optirutaLogo { from { opacity:0; transform:scale(.88); letter-spacing:10px; } to { opacity:1; transform:scale(1); letter-spacing:3px; } }
.optiruta-tag { display:inline-block; margin-top:12px; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.28); border-radius:30px; padding:5px 11px; font-size:12px; font-weight:700; }
.sidebar-brand { color:#0750B8 !important; font-size:25px; font-weight:950; letter-spacing:1.5px; }
.sidebar-caption { color:#65758B !important; font-size:12px; font-weight:700; letter-spacing:1px; }
.flag-blue { height:7px; background:#0750B8; border-radius:7px; }
.flag-gold { height:4px; background:#E9A817; border-radius:7px; margin-top:5px; }
.order-number { font-size:25px; color:#0750B8; font-weight:900; }
.order-address { font-size:18px; color:#17212F; font-weight:750; }
.small-note { color:#64748B; font-size:13px; }
.priority-high { color:#A32121; font-weight:900; }
.priority-normal { color:#0750B8; font-weight:800; }
/* Identidad visual inspirada en la referencia OptiRuta para PC */
.optiruta-top {
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  background:linear-gradient(112deg,#FFFFFF 0%,#FFFFFF 66%,#FFFAEB 100%);
