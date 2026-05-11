import pandas as pd
import streamlit as st
import io

# --- 1. PRESTIGE UI ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v56.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 15px; font-weight: bold; }
    .ss-container { 
        background: linear-gradient(135deg, #FFD700, #B8860B); 
        color: #000; padding: 20px; border-radius: 15px; text-align: center; 
        border: 4px solid #000; box-shadow: 0px 0px 15px gold; margin-bottom: 20px;
    }
    .ss-value { font-size: 50px; font-weight: 900; }
    .matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; }
    .num-box { background: #222; color: #fff; border: 1px solid #555; padding: 10px 2px; text-align: center; border-radius: 4px; font-size: 18px; font-weight: 900; }
    .hit-box { background: #00E676 !important; color: #000 !important; border: 2px solid #fff !important; }
    .hist-table { width: 100%; border-collapse: collapse; font-size: 14px; background: #fff; color: #000; }
    .hist-td { border: 1px solid #000; padding: 8px; text-align: center; font-weight: bold; }
    .pass { background: #C8E6C9; }
    .fail { background: #FFCDD2; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE STABLE ENGINE ---
def clean(v):
    if pd.isna(v) or str(v).strip() == 'XX' or str(v).strip() == '': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if len(s) >= 1 else ""

@st.cache_data
def run_vip_scan(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    hist = df[df['DATE'] < t_date].tail(30)
    last_val = ""
    # Finding last valid result to avoid IndexError
    for i in range(len(hist)-1, -1, -1):
        temp = clean(hist.iloc[i][s_name])
        if temp: 
            last_val = temp
            break

    if not last_val or len(last_val) < 2:
        return ["--"], [], []

    a, b = int(last_val[0]), int(last_val[1])
    shifts = [(0,1),(0,-1),(1,0),(-1,0),(0,5),(5,0),(5,5),(1,1),(1,4),(4,1),(6,1),(1,6),(2,2),(7,7)]
    v33 = {f"{(a+da)%10}{(b+db)%10}" for da, db in shifts}
    
    rashi = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
    ss = [rashi[last_val[0]]+last_val[1], last_val[0]+rashi[last_val[1]]]
    
    return ss, list(v33), [p[::-1] for p in v33]

# --- 3. EXECUTION ---
with st.sidebar:
    up_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx'])
    t_date = st.date_input("Target Date")

if up_file:
    df_raw = pd.read_excel(up_file)
    df_raw['DATE'] = pd.to_datetime(df_raw['DATE'])
    df_j = df_raw.to_json(date_format='iso')
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v56.0 | VIP SINGLE | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    tabs = st.tabs(["DS", "FD", "GD", "GL", "DB", "SG"])
    shifts_list = ["DS", "FD", "GD", "GL", "DB", "SG"]

    for idx, s_name in enumerate(shifts_list):
        with tabs[idx]:
            ss, v33, v24 = run_vip_scan(df_j, str(t_date), s_name)
            row = df_raw[df_raw['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""

            # VIP SINGLE BOX
            hit_ss = (actual in ss and actual != "")
            st.markdown(f"<div class='ss-container'><div style='font-weight:bold;'>🔥 VIP SINGLE 🔥</div><div class='ss-value'>{', '.join(ss)}</div><div>RESULT: {actual if actual else '--'} {'✅' if hit_ss else ''}</div></div>", unsafe_allow_html=True)

            # GRIDS
            c1, c2 = st.columns(2)
            with c1:
                st.write("**v33 Platinum**")
                g = "<div class='matrix-grid'>"
                for p in sorted(v33):
                    hit = "hit-box" if p == actual else ""
                    g += f"<div class='num-box {hit}'>{p}</div>"
                st.markdown(g + "</div>", unsafe_allow_html=True)
            with c2:
                st.write("**v24 Audit**")
                g = "<div class='matrix-grid'>"
                for p in sorted(v24):
                    hit = "hit-box" if p == actual else ""
                    g += f"<div class='num-box {hit}'>{p}</div>"
                st.markdown(g + "</div>", unsafe_allow_html=True)

            # TRIPLE HISTORY
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📊 15-DAY AUDIT", expanded=True):
                h_df = df_raw[df_raw['DATE'] < pd.to_datetime(t_date)].tail(15)
                h_html = "<table class='hist-table'><tr style='background:#000; color:gold;'><td>DATE</td><td>RES</td><td>v33</td><td>v24</td><td>SS</td></tr>"
                for _, hr in h_df.iloc[::-1].iterrows():
                    v = clean(hr[s_name])
                    h_ss, h_v33, h_v24 = run_vip_scan(df_j, str(hr['DATE']), s_name)
                    c33 = "✅" if v in h_v33 else "❌"
                    c24 = "✅" if v in h_v24 else "❌"
                    css = "✅" if v in h_ss else "❌"
                    h_html += f"<tr><td class='hist-td'>{hr['DATE'].strftime('%d-%m')}</td><td class='hist-td'>{v}</td><td class='hist-td {'pass' if c33=='✅' else 'fail'}'>{c33}</td><td class='hist-td {'pass' if c24=='✅' else 'fail'}'>{c24}</td><td class='hist-td {'pass' if css=='✅' else 'fail'}'>{css}</td></tr>"
                st.markdown(h_html + "</table>", unsafe_allow_html=True)
    
