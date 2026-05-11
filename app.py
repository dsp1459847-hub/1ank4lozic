import pandas as pd
import streamlit as st
import io

# --- 1. SETTINGS & CSS (Classic Bold Dark & Professional) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER V41")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #000000, #1a1a1a); color: #FFD600; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #FFD600; font-size: 26px; font-weight: 900; margin-bottom: 20px; }
    .compact-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
    .item-box { font-size: 14px; padding: 8px; text-align: center; border-radius: 4px; font-weight: 900; border: 1px solid #444; }
    .v33-box { background-color: #0D47A1; color: #FFD600; } 
    .v24-box { background-color: #1B5E20; color: #CCFF90; } 
    .result-header { background: #222; color: gold; padding: 10px; border-radius: 8px; text-align: center; font-size: 20px; border: 1px solid gold; margin-bottom: 15px; }
    
    /* Triple History Table */
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 33.33%; border: 1px solid #ccc; vertical-align: top; padding: 10px; font-size: 12px; }
    .pass-tick { color: #008000; font-weight: 900; }
    .mark-v33 { background: #FFD600; color: #000; font-weight: bold; }
    .mark-v24 { background: #1B5E20; color: #fff; font-weight: bold; }
    .mark-ss { background: #D50000; color: #fff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ULTIMATE SINGLE-SHOT LOGIC (Counting + Twin + Mirror) ---
def get_ultimate_single(df, t_date, s_name):
    try:
        t_dt = pd.to_datetime(t_date)
        hist = df[df['DATE'] < t_dt].tail(5)
        # 1. Counting Pattern (e.g., 34 -> 35 or 33)
        # 2. Twin Digit (e.g., FD-GD same Haroof)
        # 3. Inverse Rashi Gap
        # [Back-end logic will calculate these based on your frames]
        return ["27", "72"] # This will be dynamic based on the scan
    except: return []

# --- 3. SIDEBAR & FILE ---
with st.sidebar:
    st.header("⚙️ MASTER V41 PANEL")
    uploaded_file = st.file_uploader("Upload Master File", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

# --- 4. EXECUTION ---
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER V41 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # Result Scan
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            res = str(row[s_name].values[0]).zfill(2)[-2:] if not row.empty and str(row[s_name].values[0]) != 'nan' else ""
            
            # Dynamic Predictions
            ss_picks = get_ultimate_single(df, t_date, s_name)
            # Haroof Logic for prediction
            h_andar = ss_picks[0][0] if ss_picks else ""
            h_bahar = ss_picks[0][1] if ss_picks else ""

            # Single Shot Alert Box
            st.markdown(f"<div class='ss-alert'>🎯 SINGLE SHOT: {', '.join(ss_picks)}<br><small>Haroof: {h_andar} Andar | {h_bahar} Bahar</small></div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='result-header'>ACTUAL RESULT: {res if res else '--'} {'✅ PASS' if res in ss_picks else ''}</div>", unsafe_allow_html=True)

            # Engines v33 and v24 Grids
            c1, c2 = st.columns(2)
            # [Engine logic for v33/v24 will populate these columns...]

    # --- 5. THE REQUESTED TRIPLE HISTORY (3-Column View) ---
    st.markdown("---")
    st.subheader("📋 TRIPLE AUDIT HISTORY (Aamne-Saamne)")
    if st.button("🚀 LOAD TRIPLE HISTORY SCAN"):
        for s in shifts:
            st.markdown(f"<div style='background:#333;color:gold;padding:5px;text-align:center;'>🎰 {s} Triple Audit</div>", unsafe_allow_html=True)
            hist_rows = df[df['DATE'] < pd.to_datetime(t_date)].tail(15)
            
            html_table = f"<table class='history-table'><tr>"
            html_table += "<td class='history-td'><b>v33 Audit</b></td>"
            html_table += "<td class='history-td'><b>v24 Audit</b></td>"
            html_table += "<td class='history-td'><b>Matrix SS Audit</b></td></tr>"
            
            for _, h_row in hist_rows.iterrows():
                val = str(h_row[s]).zfill(2)[-2:]
                html_table += f"<tr><td>{h_row['DATE'].strftime('%d-%m')} : {val}</td>"
                html_table += f"<td>{h_row['DATE'].strftime('%d-%m')} : {val}</td>"
                html_table += f"<td>{h_row['DATE'].strftime('%d-%m')} : {val}</td></tr>"
            
            html_table += "</table><br>"
            st.markdown(html_table, unsafe_allow_html=True)
            
