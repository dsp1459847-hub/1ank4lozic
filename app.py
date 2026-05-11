import pandas as pd
import streamlit as st
import io

# --- 1. CONFIG & STYLING (Bold Dark Classic) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v42.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #1A237E, #0D47A1); color: gold; padding: 20px; border-radius: 12px; text-align: center; border: 3px solid gold; font-size: 26px; font-weight: 900; margin-bottom: 20px; }
    .result-header { background: #222; color: gold; padding: 10px; border-radius: 8px; text-align: center; font-size: 22px; border: 1px solid gold; margin-bottom: 15px; font-weight: bold; }
    
    /* Parallel History Table (Triple Column) */
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 33.33%; border: 1px solid #ccc; vertical-align: top; padding: 8px; font-size: 13px; font-weight: bold; }
    .pass-tick { color: #008000; font-weight: 900; font-size: 16px; }
    .fail-mark { color: #D50000; font-weight: 900; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DYNAMIC LOGIC FUNCTIONS ---
def clean(v):
    if pd.isna(v): return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

def get_dynamic_ss(df, t_date, s_name):
    """Placeholder logic that MUST be replaced by the 7-year Matrix scanner"""
    # Isko 10/62 ya 27/72 nahi, balki asli calculation karni chahiye
    try:
        t_dt = pd.to_datetime(t_date)
        hist_val = df[df['DATE'] < t_dt].tail(2)[s_name].values
        # Example dynamic calculation (Mirror of last result)
        if len(hist_val) > 0:
            v = clean(hist_val[-1])
            r = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
            return [r[v[0]]+v[1], v[0]+r[v[1]]]
        return []
    except: return []

# --- 3. SIDEBAR & EXECUTION ---
with st.sidebar:
    st.header("⚙️ MASTER V42 PANEL")
    uploaded_file = st.file_uploader("Upload Master File", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v42.0 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # A. Actual Result
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual_res = clean(row[s_name].values[0]) if not row.empty else ""
            
            # B. Get Predictions (v33, v24, Matrix)
            ss_picks = get_dynamic_ss(df, t_date, s_name)
            p33 = ["11", "22", "33"] # Example Engine results
            p24 = ["44", "55", "66"]

            # C. Single Shot Alert Box
            st.markdown(f"<div class='ss-alert'>🚀 MATRIX SINGLE: {', '.join(ss_picks) if ss_picks else 'SCANNING...'}</div>", unsafe_allow_html=True)
            
            # D. Result Header with TICK
            is_pass = " ✅ PASS" if (actual_res in ss_picks or actual_res in p33 or actual_res in p24) else " ❌ FAIL"
            st.markdown(f"<div class='result-header'>RESULT: {actual_res if actual_res else '--'} {is_pass if actual_res else ''}</div>", unsafe_allow_html=True)

            # E. TRIPLE HISTORY SCAN (Triple Column View)
            st.markdown("---")
            st.subheader("📋 TRIPLE AUDIT HISTORY (Aamne-Saamne)")
            hist_rows = df[df['DATE'] < pd.to_datetime(t_date)].tail(15)
            
            html_table = f"<table class='history-table'><tr>"
            html_table += "<td class='history-td' style='background:#FFD600;'><b>v33 Engine</b></td>"
            html_table += "<td class='history-td' style='background:#1B5E20; color:white;'><b>v24 Engine</b></td>"
            html_table += "<td class='history-td' style='background:#1A237E; color:white;'><b>Matrix SS</b></td></tr>"
            
            for _, h_row in hist_rows.iterrows():
                val = clean(h_row[s_name])
                dt = h_row['DATE'].strftime('%d-%m')
                
                # Check for each engine
                t33 = "<span class='pass-tick'>✅</span>" if val in p33 else "<span class='fail-mark'>❌</span>"
                t24 = "<span class='pass-tick'>✅</span>" if val in p24 else "<span class='fail-mark'>❌</span>"
                tss = "<span class='pass-tick'>✅</span>" if val in ss_picks else "<span class='fail-mark'>❌</span>"
                
                html_table += f"<tr><td>{dt} : {val} {t33}</td>"
                html_table += f"<td>{dt} : {val} {t24}</td>"
                html_table += f"<td>{dt} : {val} {tss}</td></tr>"
            
            html_table += "</table><br>"
            st.markdown(html_table, unsafe_allow_html=True)
        
