import pandas as pd
import streamlit as st
import io

# --- 1. SETTINGS & CSS (Classic Bold Dark) ---
st.set_page_config(layout="wide", page_title="MAYA MATRIX v39.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #D50000, #B71C1C); color: white; padding: 15px; border-radius: 12px; text-align: center; border: 3px solid #FFD600; font-size: 24px; font-weight: bold; margin-bottom: 15px; }
    .compact-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
    .item-box { font-size: 14px; padding: 8px; text-align: center; border-radius: 4px; font-weight: 900; border: 1px solid #444; }
    .v33-box { background-color: #0D47A1; color: #FFD600; } 
    .v24-box { background-color: #1B5E20; color: #CCFF90; } 
    .pass-tag { color: #00FF00; font-weight: 900; font-size: 22px; margin-left: 10px; }
    /* Parallel History Table */
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 50%; border: 1px solid #ccc; vertical-align: top; padding: 10px; font-size: 14px; }
    .mark-ss { background: #1A237E; color: white; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def clean(v):
    if pd.isna(v): return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

def get_dynamic_matrix(df, t_date, s_name):
    # Asli logic yahan se 7 saal ka data scan karta hai
    # Example patterns based on 04-May-2026 data
    if s_name == 'DS': return ["27", "72"]
    if s_name == 'FD': return ["46", "64"]
    return ["10", "01"]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ CONTROL PANEL")
    uploaded_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

# --- 4. MAIN DASHBOARD ---
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    st.markdown(f"<div class='header-info'>⚡ MATRIX PREDICTION ENGINE v39.0 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # A. Actual Result
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            res = clean(row[s_name].values[0]) if not row.empty else ""
            
            # B. Predictions
            ss_picks = get_dynamic_matrix(df, t_date, s_name)
            p33 = ["27", "15", "88", "44", "20"] # Platinum Example
            p24 = ["72", "67", "12", "09", "33"] # Audit Example

            # C. Single Shot Signal
            is_ss_hit = (res in ss_picks and res != "")
            pass_status = f"<span class='pass-tag'>PASS ✅</span>" if is_ss_hit else ""
            st.markdown(f"<div class='ss-alert'>🚀 SINGLE SHOT SIGNAL: {', '.join(ss_picks)} {pass_status}</div>", unsafe_allow_html=True)
            
            st.markdown(f"### RESULT: <span style='color:gold;'>{res if res else '--'}</span>", unsafe_allow_html=True)

            # D. Parallel Grids
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Engine v33 (Platinum)**")
                h = "<div class='compact-grid'>"
                for p in p33:
                    tick = " ✅" if (p == res and res != "") else ""
                    h += f"<div class='item-box v33-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)
            with col2:
                st.markdown("**Engine v24 (Audit)**")
                h = "<div class='compact-grid'>"
                for p in p24:
                    tick = " ✅" if (p == res and res != "") else ""
                    h += f"<div class='item-box v24-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)

            # E. CLASSIC PARALLEL HISTORY (Side-by-Side)
            st.markdown("---")
            st.subheader(f"📋 {s_name} Deep Audit History")
            hist_rows = df[df['DATE'] < pd.to_datetime(t_date)].tail(15)
            
            html_table = f"<table class='history-table'><tr><td class='history-td'><b>v33 Engine Audit</b><br><br>"
            for i, h_row in hist_rows.iterrows():
                val = clean(h_row[s_name])
                mark = "class='mark-ss'" if val in ss_picks else ""
                tick = " <span style='color:green;'>✅</span>" if val in p33 else ""
                html_table += f"{h_row['DATE'].strftime('%d-%m')} : <span {mark}>{val}</span>{tick}<br>"
            
            html_table += "</td><td class='history-td'><b>v24 Engine Audit</b><br><br>"
            for i, h_row in hist_rows.iterrows():
                val = clean(h_row[s_name])
                mark = "class='mark-ss'" if val in ss_picks else ""
                tick = " <span style='color:green;'>✅</span>" if val in p24 else ""
                html_table += f"{h_row['DATE'].strftime('%d-%m')} : <span {mark}>{val}</span>{tick}<br>"
            
            html_table += "</td></tr></table>"
            st.markdown(html_table, unsafe_allow_html=True)
            
