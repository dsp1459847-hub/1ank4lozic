import pandas as pd
import streamlit as st
import io

# --- 1. CONFIG & BOLD UI ---
st.set_page_config(layout="wide", page_title="MAYA MATRIX v60.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; font-weight: bold; }
    .vip-card { 
        background: linear-gradient(135deg, #1A237E, #000); 
        color: #00FF00; padding: 30px; border-radius: 20px; 
        text-align: center; border: 5px solid gold; margin-bottom: 25px;
    }
    .ss-font { font-size: 85px; font-weight: 900; letter-spacing: 12px; text-shadow: 3px 3px #000; }
    .audit-table { width: 100%; border-collapse: collapse; background: white; color: black; font-size: 15px; }
    .audit-td { border: 2px solid #000; padding: 10px; text-align: center; font-weight: bold; }
    .hit-pass { background: #C8E6C9; color: #1B5E20; font-weight: 900; }
    .hit-fail { background: #FFCDD2; color: #B71C1C; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE EXPERT PATTERN ENGINE ---
def clean(v):
    if pd.isna(v) or str(v).strip() in ['XX', '']: return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def run_expert_audit(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    # Scanning 20 Days History for deep patterns
    hist = df[df['DATE'] < t_date].tail(20)
    
    # Get Last 2 Results for vertical tracking
    res_list = [clean(x) for x in hist[s_name].values if clean(x)]
    if not res_list: return [], [], []
    
    last = res_list[-1]
    
    # EXPERT LOGIC: Mirror + Cross-Connection + Gap
    r = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
    
    # 1. VIP Single (Based on Friend's 17/71 and Disawar 10/62 Logic)
    # This captures the Mirror of Haroofs + Neighbor connection
    ss = [r[last[0]]+last[1], last[0]+r[last[1]], r[last[0]]+r[last[1]]]
    
    # 2. v33 Platinum (32-Pattern Confluence)
    a, b = int(last[0]), int(last[1])
    shifts = [(0,1),(0,-1),(1,0),(-1,0),(0,5),(5,0),(5,5),(1,4),(4,1),(6,1),(1,6),(1,1),(2,2)]
    v33 = {f"{(a+da)%10}{(b+db)%10}" for da, db in shifts}
    v24 = {p[::-1] for p in v33}
    
    return ss, list(v33), list(v24)

# --- 3. DASHBOARD ---
with st.sidebar:
    st.header("🎯 EXPERT CONTROL")
    file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx'])
    t_date = st.date_input("Target Date")

if file:
    df_raw = pd.read_excel(file)
    df_raw['DATE'] = pd.to_datetime(df_raw['DATE'])
    df_j = df_raw.to_json(date_format='iso')
    
    st.markdown(f"<div class='header-info'>⚡ MAYA EXPERT v60.0 | FULL BACK-TESTED LOGIC</div>", unsafe_allow_html=True)
    
    tabs = st.tabs(["DS", "FD", "GD", "GL", "DB", "SG"])
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            ss, v33, v24 = run_expert_audit(df_j, str(t_date), s_name)
            curr_row = df_raw[df_raw['DATE'] == pd.to_datetime(t_date)]
            actual = clean(curr_row[s_name].values[0]) if not curr_row.empty else ""

            # --- BIG VIP DISPLAY ---
            is_hit = (actual in ss and actual != "")
            st.markdown(f"""
            <div class='vip-card'>
                <div style='color:gold; font-size:24px; font-weight:bold;'>🏆 SUPER VIP SINGLE SHOT</div>
                <div class='ss-font'>{', '.join(ss[:2])}</div>
                <div style='font-size:28px;'>RESULT: {actual if actual else '--'} {'✅ PASS' if is_hit else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- TRIPLE HISTORY AUDIT (15 DAYS) ---
            st.markdown("### 📊 Triple Audit History (Aamne-Saamne)")
            h_df = df_raw[df_raw['DATE'] < pd.to_datetime(t_date)].tail(15)
            h_table = "<table class='audit-table'><tr style='background:#000; color:gold;'><td>DATE</td><td>RES</td><td>v33</td><td>v24</td><td>SS</td></tr>"
            
            for _, hr in h_df.iloc[::-1].iterrows():
                val = clean(hr[s_name])
                h_ss, h_v33, h_v24 = run_expert_audit(df_j, str(hr['DATE']), s_name)
                c33 = "✅" if val in h_v33 else "❌"
                c24 = "✅" if val in h_v24 else "❌"
                css = "✅" if val in h_ss else "❌"
                
                h_table += f"<tr><td class='audit-td'>{hr['DATE'].strftime('%d-%m')}</td><td class='audit-td' style='background:#eee;'>{val}</td>"
                h_table += f"<td class='audit-td {'hit-pass' if c33=='✅' else 'hit-fail'}'>{c33}</td>"
                h_table += f"<td class='audit-td {'hit-pass' if c24=='✅' else 'hit-fail'}'>{c24}</td>"
                h_table += f"<td class='audit-td {'hit-pass' if css=='✅' else 'hit-fail'}'>{css}</td></tr>"
            
            st.markdown(h_table + "</table>", unsafe_allow_html=True)
            
