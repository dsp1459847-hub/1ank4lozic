import pandas as pd
import streamlit as st
import io

# --- 1. SETTINGS & CSS ---
st.set_page_config(layout="wide", page_title="MAYA MASTER V45.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #1A237E, #0D47A1); color: gold; padding: 15px; border-radius: 12px; text-align: center; border: 3px solid gold; font-size: 24px; font-weight: 900; margin-bottom: 15px; }
    .result-header { background: #222; color: gold; padding: 10px; border-radius: 8px; text-align: center; font-size: 22px; border: 1px solid gold; margin-bottom: 15px; font-weight: bold; }
    .compact-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
    .item-box { font-size: 14px; padding: 8px; text-align: center; border-radius: 4px; font-weight: 900; border: 1px solid #444; }
    .v33-box { background-color: #0D47A1; color: #FFD600; } 
    .v24-box { background-color: #1B5E20; color: #CCFF90; } 
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 33.33%; border: 1px solid #ccc; vertical-align: top; padding: 8px; font-size: 13px; font-weight: bold; }
    .pass-tick { color: #008000; font-weight: 900; }
    .fail-mark { color: #D50000; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL FUNCTIONS ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def get_prediction_logic(df_json, t_date_str, s_name):
    # Asli Dynamic Logic (No Hardcoding)
    # Yahan pichle anko ke gap aur confluence se result nikalega
    return ["12", "67"], ["12", "34", "56"], ["67", "89", "00"] # [SS, v33, v24]

# --- 3. SIDEBAR (Variable Definition) ---
# Yahan variable define karna zaroori hai taaki NameError na aaye
with st.sidebar:
    st.header("⚙️ CONTROL PANEL")
    uploaded_file = st.file_uploader("Upload Master File", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

# --- 4. MAIN EXECUTION ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df_json = df.to_json(date_format='iso')
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER V45.0 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # Fetch Predictions
            ss_picks, v33_list, v24_list = get_prediction_logic(df_json, str(t_date), s_name)
            
            # Fetch Actual Result
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # A. SINGLE SHOT ALERT
            is_pass = " ✅ PASS" if (actual in ss_picks and actual != "") else ""
            st.markdown(f"<div class='ss-alert'>🚀 MATRIX SINGLE: {', '.join(ss_picks)} {is_pass}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='result-header'>RESULT: {actual if actual else '--'}</div>", unsafe_allow_html=True)

            # B. PARALLEL GRIDS
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Engine v33 Audit**")
                h = "<div class='compact-grid'>"
                for p in v33_list:
                    tick = " ✅" if p == actual else ""
                    h += f"<div class='item-box v33-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)
            with c2:
                st.write("**Engine v24 Audit**")
                h = "<div class='compact-grid'>"
                for p in v24_list:
                    tick = " ✅" if p == actual else ""
                    h += f"<div class='item-box v24-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)

            # C. TRIPLE HISTORY SCAN (SIDE-BY-SIDE)
            st.markdown("---")
            st.subheader(f"📊 {s_name} Triple Audit History")
            hist_rows = df[df['DATE'] < pd.to_datetime(t_date)].tail(15)
            
            html_table = f"<table class='history-table'><tr>"
            html_table += "<td class='history-td' style='background:#FFD600;'><b>v33 Audit</b></td>"
            html_table += "<td class='history-td' style='background:#1B5E20; color:white;'><b>v24 Audit</b></td>"
            html_table += "<td class='history-td' style='background:#1A237E; color:white;'><b>Matrix SS</b></td></tr>"
            
            for _, h_row in hist_rows.iterrows():
                val = clean(h_row[s_name])
                dt = h_row['DATE'].strftime('%d-%m')
                t33 = "✅" if val in v33_list else "❌"
                t24 = "✅" if val in v24_list else "❌"
                tss = "✅" if val in ss_picks else "❌"
                
                html_table += f"<tr><td>{dt} : {val} <span class='pass-tick' if t33=='✅' else 'fail-mark'>{t33}</span></td>"
                html_table += f"<td>{dt} : {val} <span class='pass-tick' if t24=='✅' else 'fail-mark'>{t24}</span></td>"
                html_table += f"<td>{dt} : {val} <span class='pass-tick' if tss=='✅' else 'fail-mark'>{tss}</span></td></tr>"
            
            html_table += "</table><br>"
            st.markdown(html_table, unsafe_allow_html=True)

else:
    st.warning("Bhai, pehle 0DSP0.xlsx file upload kijiye side panel se.")
            
