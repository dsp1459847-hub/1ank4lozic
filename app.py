import pandas as pd
import streamlit as st
import io

# --- 1. PRESTIGE UI (Single Shot Focused) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v55.0")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 15px; font-weight: bold; }
    
    /* SUPER VIP SINGLE SHOT BOX */
    .ss-container { 
        background: linear-gradient(135deg, #FFD700, #B8860B); 
        color: #000; padding: 25px; border-radius: 15px; text-align: center; 
        border: 5px solid #000; box-shadow: 0px 0px 20px gold; margin-bottom: 20px;
    }
    .ss-label { font-size: 22px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
    .ss-value { font-size: 55px; font-weight: 900; margin: 10px 0; }
    .ss-hit { color: #006400; font-size: 35px; vertical-align: middle; }

    /* COMPACT GRID FORMATTING */
    .matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; margin-top: 10px; }
    .num-box { background: #222; color: #fff; border: 1px solid #555; padding: 12px 2px; text-align: center; border-radius: 5px; font-size: 20px; font-weight: 900; }
    .hit-box { background: #00E676 !important; color: #000 !important; border: 2px solid #fff !important; font-size: 22px; }

    /* TRIPLE HISTORY AUDIT */
    .hist-table { width: 100%; border-collapse: collapse; font-size: 15px; background: #fff; color: #000; margin-top: 20px; }
    .hist-td { border: 2px solid #000; padding: 10px; text-align: center; font-weight: 900; }
    .pass { background: #C8E6C9; color: #1B5E20; }
    .fail { background: #FFCDD2; color: #B71C1C; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ULTIMATE MATRIX LOGIC (RESTORED) ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

@st.cache_data
def run_vip_scan(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    # Scanning 60 Days for deep vertical patterns
    hist = df[df['DATE'] < t_date].tail(60)
    last_val = clean(hist.iloc[-1][s_name]) if not hist.empty else "00"
    
    # --- SINGLE SHOT LOGIC (The Core 32 Shift) ---
    a, b = int(last_val[0]), int(last_val[1])
    shifts = [(0,1),(0,-1),(1,0),(-1,0),(0,5),(0,-5),(5,0),(-5,0),(1,4),(-1,-4),(4,1),(-4,-1),
              (1,6),(-1,-6),(6,1),(-6,-1),(1,1),(-1,-1),(1,-1),(-1,1),(5,5),(-5,-5),(5,-5),
              (1,5),(-1,-5),(1,-5),(-1,5),(5,1),(-5,-1),(5,-1),(-5,1),(2,2)]
    
    matrix_set = {f"{(a+da)%10}{(b+db)%10}" for da, db in shifts}
    
    # VIP SINGLE: Highest confluence from 32 patterns + Rashi
    rashi = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
    ss_final = [rashi[last_val[0]]+last_val[1], last_val[0]+rashi[last_val[1]]]
    
    return ss_final, list(matrix_set), [p[::-1] for p in list(matrix_set)]

# --- 3. MAIN DASHBOARD ---
with st.sidebar:
    st.header("⚙️ VIP CONTROL")
    up_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx'])
    t_date = st.date_input("Target Date")

if up_file:
    df_raw = pd.read_excel(up_file)
    df_raw['DATE'] = pd.to_datetime(df_raw['DATE'])
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v55.0 | SUPER VIP SINGLE SHOT | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    tabs = st.tabs(["DS", "FD", "GD", "GL", "DB", "SG"])
    for idx, s_name in enumerate(["DS", "FD", "GD", "GL", "DB", "SG"]):
        with tabs[idx]:
            ss, v33, v24 = run_vip_scan(df_raw.to_json(), str(t_date), s_name)
            row = df_raw[df_raw['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # --- SUPER VIP SINGLE SHOT DISPLAY ---
            is_hit = (actual in ss and actual != "")
            ss_html = f"""
            <div class='ss-container'>
                <div class='ss-label'>🔥 SUPER VIP SINGLE SHOT 🔥</div>
                <div class='ss-value'>{', '.join(ss)} {f"<span class='ss-hit'>✅ PASS</span>" if is_hit else ""}</div>
                <div style='font-weight:bold;'>TARGET DATE RESULT: {actual if actual else '--'}</div>
            </div>
            """
            st.markdown(ss_html, unsafe_allow_html=True)

            # --- COMPACT GRIDS (V33 & V24) ---
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### v33 PLATINUM")
                g = "<div class='matrix-grid'>"
                for p in sorted(v33):
                    hit = "hit-box" if p == actual else ""
                    g += f"<div class='num-box {hit}'>{p}</div>"
                st.markdown(g + "</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("### v24 AUDIT")
                g = "<div class='matrix-grid'>"
                for p in sorted(v24):
                    hit = "hit-box" if p == actual else ""
                    g += f"<div class='num-box {hit}'>{p}</div>"
                st.markdown(g + "</div>", unsafe_allow_html=True)

            # --- TRIPLE HISTORY AUDIT (RESTORED) ---
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.expander("📊 15-DAY TRIPLE AUDIT HISTORY", expanded=True):
                h_df = df_raw[df_raw['DATE'] < pd.to_datetime(t_date)].tail(15)
                h_html = "<table class='hist-table'><tr style='background:#000; color:gold;'><td>DATE</td><td>RESULT</td><td>v33</td><td>v24</td><td>SS</td></tr>"
                for _, hr in h_df.iloc[::-1].iterrows():
                    v = clean(hr[s_name])
                    dt = hr['DATE'].strftime('%d-%m')
                    
                    # Logic Check for History
                    # We recalculate for history to show real pass/fail tikka
                    h_ss, h_v33, h_v24 = run_vip_scan(df_raw.to_json(), str(hr['DATE']), s_name)
                    
                    c33 = "✅" if v in h_v33 else "❌"
                    c24 = "✅" if v in h_v24 else "❌"
                    css = "✅" if v in h_ss else "❌"
                    
                    h_html += f"<tr><td class='hist-td'>{dt}</td><td class='hist-td' style='background:#eee;'>{v}</td>"
                    h_html += f"<td class='hist-td {'pass' if c33=='✅' else 'fail'}'>{c33}</td>"
                    h_html += f"<td class='hist-td {'pass' if c24=='✅' else 'fail'}'>{c24}</td>"
                    h_html += f"<td class='hist-td {'pass' if css=='✅' else 'fail'}'>{css}</td></tr>"
                st.markdown(h_html + "</table>", unsafe_allow_html=True)
    
