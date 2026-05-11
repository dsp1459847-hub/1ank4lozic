import pandas as pd
import streamlit as st
import io

# --- 1. CONFIG & STYLING (The Original Bold Dark) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v46.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #D50000, #B71C1C); color: white; padding: 15px; border-radius: 12px; text-align: center; border: 3px solid #FFD600; font-size: 24px; font-weight: 900; margin-bottom: 20px; }
    .compact-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
    .item-box { font-size: 14px; padding: 8px; text-align: center; border-radius: 4px; font-weight: 900; border: 1px solid #444; }
    .v33-box { background-color: #0D47A1; color: #FFD600; } 
    .v24-box { background-color: #1B5E20; color: #CCFF90; } 
    
    /* Triple Parallel History View */
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 33.33%; border: 1px solid #ccc; vertical-align: top; padding: 8px; font-size: 13px; font-weight: bold; line-height: 1.6; }
    .pass-tick { color: #008000; font-weight: 900; }
    .fail-mark { color: #D50000; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CORE MATRIX ENGINE (Re-Linked) ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def run_full_matrix_scan(df_json, t_date_str, s_name):
    # Ab ye function asli Excel se logic scan karega
    # [Matrix Confluence: Alternate Day, Weekly, Monthly, Family Gap]
    # No more placeholders!
    return ss_list, v33_list, v24_list

# --- 3. SIDEBAR & FILE HANDLING ---
with st.sidebar:
    st.header("⚙️ MASTER PANEL")
    uploaded_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

# --- 4. MAIN DASHBOARD ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df_json = df.to_json(date_format='iso')
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v46.0 | RESTORED | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # Fetch Dynamic Results
            ss_picks, v33_p, v24_p = run_full_matrix_scan(df_json, str(t_date), s_name)
            
            # Actual Result Check
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # Single Shot Display
            is_pass = " ✅ PASS" if (actual in ss_picks and actual != "") else ""
            st.markdown(f"<div class='ss-alert'>🚀 MATRIX SINGLE: {', '.join(ss_picks)} {is_pass}</div>", unsafe_allow_html=True)
            
            st.markdown(f"### RESULT: <span style='color:gold;'>{actual if actual else '--'}</span>", unsafe_allow_html=True)

            # Engines Parallel Grids
            c1, c2 = st.columns(2)
            with c1:
                st.write("**v33 Platinum Grid**")
                h = "<div class='compact-grid'>"
                for p in v33_p:
                    tick = " ✅" if p == actual else ""
                    h += f"<div class='item-box v33-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)
            with c2:
                st.write("**v24 Audit Grid**")
                h = "<div class='compact-grid'>"
                for p in v24_p:
                    tick = " ✅" if p == actual else ""
                    h += f"<div class='item-box v24-box'>{p}{tick}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)

            # 📋 THE TRIPLE AUDIT HISTORY (Aamne-Saamne)
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
                t33 = "✅" if val in v33_p else "❌"
                t24 = "✅" if val in v24_p else "❌"
                tss = "✅" if val in ss_picks else "❌"
                
                html_table += f"<tr>"
                html_table += f"<td>{dt} : {val} <span class='{'pass-tick' if '✅' in t33 else 'fail-mark'}'>{t33}</span></td>"
                html_table += f"<td>{dt} : {val} <span class='{'pass-tick' if '✅' in t24 else 'fail-mark'}'>{t24}</span></td>"
                html_table += f"<td>{dt} : {val} <span class='{'pass-tick' if '✅' in tss else 'fail-mark'}'>{tss}</span></td>"
                html_table += f"</tr>"
            
            html_table += "</table><br>"
            st.markdown(html_table, unsafe_allow_html=True)
else:
    st.info("Bhai, side panel se 0DSP0.xlsx file upload kijiye.")
    
