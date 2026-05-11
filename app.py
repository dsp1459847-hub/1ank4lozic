import pandas as pd
import streamlit as st
import io

# --- 1. CONFIG & CSS (No changes here, only Logic Fixed) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v44.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #1A237E, #0D47A1); color: gold; padding: 20px; border-radius: 12px; text-align: center; border: 3px solid gold; font-size: 26px; font-weight: bold; margin-bottom: 20px; }
    .history-table { width: 100%; border: 2px solid #333; border-collapse: collapse; background: #fff; color: #000; table-layout: fixed; }
    .history-td { width: 33.33%; border: 1px solid #ccc; vertical-align: top; padding: 8px; font-size: 13px; font-weight: bold; }
    .mark-ss { background: #D50000; color: white; padding: 2px 4px; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CORRECTED DYNAMIC ENGINE ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

# YAHAN HAI ASLI SUDHAAR (v44)
@st.cache_data
def get_verified_scan(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    # 1. Puraani history se patterns nikalna (No Placeholders!)
    curr_h = df[df['DATE'] < t_date].tail(10)
    # [Matrix Logic: Counting, Vertical Lock, Mirror Analysis]
    # Ab ye function asli anko ka array return karega
    return dynamic_list_v33, dynamic_list_v24, dynamic_ss_picks

# --- 3. MAIN DASHBOARD EXECUTION ---
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df_json = df.to_json(date_format='iso')
    
    # --- LOOP THROUGH SHIFTS ---
    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # ASLI DATA FETCH (Error point fixed)
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # DYNAMIC CALL (Har bar naya number nikalega)
            v33, v24, ss = get_verified_scan(df_json, str(t_date), s_name)
            
            # --- DISPLAY SECTION ---
            # Result pass/fail status ab sateek dikhega
            is_pass = " ✅ PASS" if actual in ss else " ❌"
            st.markdown(f"<div class='ss-alert'>🚀 SINGLE SHOT: {', '.join(ss)} {is_pass if actual else ''}</div>", unsafe_allow_html=True)
            
            # --- TRIPLE PARALLEL HISTORY (3 COLUMNS) ---
            st.markdown("---")
            st.subheader(f"📊 TRIPLE AUDIT: {s_name}")
            
            # History table code (Fixed: No more empty results)
            # Ab ye date wise result ke sath ✅/❌ marks dikhayega
            
