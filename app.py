import pandas as pd
import streamlit as st
import io

# --- 1. BOLD DARK UI ---
st.set_page_config(layout="wide", page_title="MAYA SNIPER v59.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; font-weight: bold; }
    .ss-box { 
        background: #111; color: #00FF00; padding: 30px; border-radius: 15px; 
        text-align: center; border: 4px solid #444; margin-bottom: 20px;
    }
    .ss-num { font-size: 80px; font-weight: 900; letter-spacing: 10px; }
    .audit-table { width: 100%; border-collapse: collapse; background: white; color: black; }
    .audit-td { border: 2px solid #000; padding: 10px; text-align: center; font-weight: bold; }
    .pass-tick { color: #008000; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE PATTERN HUNTER ENGINE ---
def clean(v):
    if pd.isna(v) or str(v).strip() in ['XX', '']: return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def get_pattern_sniper(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    # Scanning 15 days history for pattern matching
    hist = df[df['DATE'] < t_date].tail(15)
    last_res = ""
    for val in reversed(hist[s_name].values):
        c_val = clean(val)
        if c_val:
            last_res = c_val
            break
            
    if not last_res: return ["--"], [], []

    # THE FORMULA: Mirror + Neighbor + Cross-Total
    r = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
    
    # 1. VIP Single (The Confluence your friend saw)
    ss = [r[last_res[0]]+last_res[1], last_res[0]+r[last_res[1]]]
    
    # 2. Pattern Grids (v33/v24)
    a, b = int(last_res[0]), int(last_res[1])
    v33 = {f"{(a+i)%10}{(b+j)%10}" for i in [0,1,5,9] for j in [0,1,5,9]}
    v24 = {p[::-1] for p in v33}
    
    return ss, list(v33), list(v24)

# --- 3. DASHBOARD ---
with st.sidebar:
    st.header("🎯 SNIPER PANEL")
    up_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx'])
    t_date = st.date_input("Target Date")

if up_file:
    df_raw = pd.read_excel(up_file)
    df_raw['DATE'] = pd.to_datetime(df_raw['DATE'])
    
    st.markdown(f"<div class='header-info'>💎 MAYA SNIPER v59.0 | PATTERN MATCHING ACTIVE</div>", unsafe_allow_html=True)
    
    tabs = st.tabs(["DS", "FD", "GD", "GL", "DB", "SG"])
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            ss, v33, v24 = get_pattern_sniper(df_raw.to_json(), str(t_date), s_name)
            row = df_raw[df_raw['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""

            # --- VIP SINGLE DISPLAY ---
            is_hit = (actual in ss and actual != "")
            st.markdown(f"""
            <div class='ss-box'>
                <div style='color:gold; font-size:20px;'>🚀 PATTERN SINGLE SHOT</div>
                <div class='ss-num'>{', '.join(ss)}</div>
                <div style='font-size:25px;'>RESULT: {actual if actual else '--'} {'✅' if is_hit else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- TRIPLE AUDIT TABLE ---
            st.markdown("### 📋 15-Day Audit History")
            h_df = df_raw[df_raw['DATE'] < pd.to_datetime(t_date)].tail(15)
            h_table = "<table class='audit-table'><tr style='background:#000; color:gold;'><td>DATE</td><td>RES</td><td>v33</td><td>v24</td><td>SS</td></tr>"
            
            for _, hr in h_df.iloc[::-1].iterrows():
                val = clean(hr[s_name])
                h_ss, h_v33, h_v24 = get_pattern_sniper(df_raw.to_json(), str(hr['DATE']), s_name)
                c33 = "✅" if val in h_v33 else "❌"
                c24 = "✅" if val in h_v24 else "❌"
                css = "✅" if val in h_ss else "❌"
                h_table += f"<tr><td class='audit-td'>{hr['DATE'].strftime('%d-%m')}</td><td class='audit-td'>{val}</td><td>{c33}</td><td>{c24}</td><td>{css}</td></tr>"
            st.markdown(h_table + "</table>", unsafe_allow_html=True)
    
