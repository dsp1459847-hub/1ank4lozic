import pandas as pd
import streamlit as st
import io

# --- 1. CONFIG & SUPER-COMPACT STYLING ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v50.0")

st.markdown("""
    <style>
    /* Global Styling */
    .stApp { background-color: #0e1117; color: white; }
    .header-info { background: #000; color: gold; padding: 5px; border-radius: 5px; text-align: center; border: 1px solid gold; font-weight: bold; margin-bottom: 10px; }
    
    /* SS Alert Box */
    .ss-alert { background: linear-gradient(135deg, #1A237E, #0D47A1); color: gold; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid gold; font-size: 28px; font-weight: 900; margin-bottom: 15px; }

    /* Compact Grid Design */
    .matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-top: 5px; }
    
    /* Box Styling */
    .num-box { 
        background: #1e1e1e; color: #ffffff; border: 1px solid #444; 
        padding: 8px 2px; text-align: center; border-radius: 4px; 
        font-size: 18px; font-weight: 900; line-height: 1;
    }
    
    /* Success Highlight */
    .hit-box { 
        background: #00C853 !important; color: black !important; 
        border: 2px solid white !important; box-shadow: 0px 0px 10px #00FF00;
    }

    /* History Table Compact */
    .hist-table { width: 100%; border-collapse: collapse; font-size: 12px; table-layout: fixed; }
    .hist-td { border: 1px solid #333; padding: 4px; text-align: center; font-weight: bold; }
    .pass-text { color: #00FF00; font-weight: 900; }
    .fail-text { color: #FF1744; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE FUNCTIONS (Logic Unchanged) ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def get_matrix_data(df_json, t_date_str, s_name):
    # Aapka asli logic yahan se anka return karega
    # [v33_list, v24_list, ss_list]
    return ss_list, v33_list, v24_list

# --- 3. SIDEBAR & FILE HANDLING ---
with st.sidebar:
    st.title("MAYA CONTROL")
    up_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx'])
    t_date = st.date_input("Target Date")

# --- 4. MAIN DASHBOARD ---
if up_file:
    df = pd.read_excel(up_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v50.0 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # Data Fetch
            ss, v33, v24 = get_matrix_data(df.to_json(), str(t_date), s_name)
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""

            # --- A. SINGLE SHOT BIG BOX ---
            is_ss_hit = (actual in ss and actual != "")
            ss_html = f"<div class='ss-alert'>🚀 SINGLE: {', '.join(ss)} {'✅' if is_ss_hit else ''}</div>"
            st.markdown(ss_html, unsafe_allow_html=True)

            # --- B. v33 & v24 COMPACT GRIDS ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<b>V33 PLATINUM</b>", unsafe_allow_html=True)
                grid_html = "<div class='matrix-grid'>"
                for p in sorted(v33):
                    is_hit = (p == actual)
                    hit_class = "hit-box" if is_hit else ""
                    grid_html += f"<div class='num-box {hit_class}'>{p}{'✅' if is_hit else ''}</div>"
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)

            with col2:
                st.markdown("<b>V24 AUDIT</b>", unsafe_allow_html=True)
                grid_html = "<div class='matrix-grid'>"
                for p in sorted(v24):
                    is_hit = (p == actual)
                    hit_class = "hit-box" if is_hit else ""
                    grid_html += f"<div class='num-box {hit_class}'>{p}{'✅' if is_hit else ''}</div>"
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)

            # --- C. TRIPLE AUDIT HISTORY (Super Slim) ---
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 VIEW 15-DAY AUDIT HISTORY", expanded=True):
                hist_df = df[df['DATE'] < pd.to_datetime(t_date)].tail(15)
                h_html = "<table class='hist-table'><tr><td class='hist-td' style='color:gold;'>DATE</td><td class='hist-td' style='color:gold;'>RES</td><td class='hist-td'>V33</td><td class='hist-td'>V24</td><td class='hist-td'>SS</td></tr>"
                
                for _, hr in hist_df.iterrows():
                    val = clean(hr[s_name])
                    dt = hr['DATE'].strftime('%d-%m')
                    t33 = "<span class='pass-text'>✅</span>" if val in v33 else "<span class='fail-text'>❌</span>"
                    t24 = "<span class='pass-text'>✅</span>" if val in v24 else "<span class='fail-text'>❌</span>"
                    tss = "<span class='pass-text'>✅</span>" if val in ss else "<span class='fail-text'>❌</span>"
                    h_html += f"<tr><td class='hist-td'>{dt}</td><td class='hist-td' style='background:#222;'>{val}</td><td class='hist-td'>{t33}</td><td class='hist-td'>{t24}</td><td class='hist-td'>{tss}</td></tr>"
                
                h_html += "</table>"
                st.markdown(h_html, unsafe_allow_html=True)
                
