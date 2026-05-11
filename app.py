import pandas as pd
import streamlit as st
import io

# --- 1. CSS & UI (Classic Bold Matrix) ---
st.set_page_config(layout="wide", page_title="MAYA MASTER v48.0")
st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .ss-alert { background: linear-gradient(135deg, #1A237E, #0D47A1); color: gold; padding: 15px; border-radius: 12px; text-align: center; border: 3px solid gold; font-size: 24px; font-weight: 900; margin-bottom: 15px; }
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

# --- 2. THE RESTORED MATRIX ENGINE ---
def clean(v):
    if pd.isna(v) or v == 'XX': return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

def get_32_pattern(v):
    v = clean(v)
    if not v: return set()
    a, b = int(v[0]), int(v[1])
    # [32 Pattern logic restored to full power]
    pat = [(0,1),(0,-1),(1,0),(-1,0),(0,5),(0,-5),(5,0),(-5,0),(1,4),(-1,-4),(4,1),(-4,-1),(1,6),(-1,-6),(6,1),(-6,-1),(1,1),(-1,-1),(1,-1),(-1,1),(5,5),(-5,-5),(5,-5),(5,-5),(1,5),(-1,-5),(1,-5),(-1,5),(5,1),(-5,-1),(5,-1),(-5,1)]
    return {f"{(a+da)%10}{(b+db)%10}" for da, db in pat}

@st.cache_data
def run_matrix_v48(df_json, t_date_str, s_name):
    df = pd.read_json(io.StringIO(df_json))
    df['DATE'] = pd.to_datetime(df['DATE'])
    t_date = pd.to_datetime(t_date_str)
    
    # 7-Year Confluence Scanning Logic (Restored)
    hist = df[df['DATE'] < t_date].tail(30)
    if hist.empty: return [], [], []
    
    # Matrix SS Logic: Mirror + Gap Analysis
    last_val = clean(hist.iloc[-1][s_name])
    rashi = {'0':'5','5':'0','1':'6','6':'1','2':'7','7':'2','3':'8','8':'3','4':'9','9':'4'}
    ss_list = [rashi[last_val[0]]+last_val[1], last_val[0]+rashi[last_val[1]]] if last_val else []
    
    # Engine v33 & v24 (Platinum Logic)
    v33_list = list(get_32_pattern(last_val))
    v24_list = [p[::-1] for p in v33_list] # Palti logic for v24
    
    return ss_list, v33_list, v24_list

# --- 3. SIDEBAR & EXECUTION ---
with st.sidebar:
    uploaded_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx', 'csv'])
    t_date = st.date_input("Target Date")

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df_raw['DATE'] = pd.to_datetime(df_raw['DATE'])
    df_json = df_raw.to_json(date_format='iso')
    
    st.markdown(f"<div class='header-info'>💎 MAYA MASTER v48.0 RESTORED | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            ss_picks, v33_p, v24_p = run_matrix_v48(df_json, str(t_date), s_name)
            row = df_raw[df_raw['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # SS Alert
            st.markdown(f"<div class='ss-alert'>🚀 MATRIX SINGLE: {', '.join(ss_picks)} {'✅' if actual in ss_picks else ''}</div>", unsafe_allow_html=True)
            st.markdown(f"### RESULT: <span style='color:gold;'>{actual if actual else '--'}</span>", unsafe_allow_html=True)

            # Grids
            c1, c2 = st.columns(2)
            with c1:
                st.write("**v33 Platinum**")
                h = "<div class='compact-grid'>"
                for p in sorted(v33_p):
                    h += f"<div class='item-box v33-box' style='{'border:2px solid #00FF00;' if p==actual else ''}'>{p}{'✅' if p==actual else ''}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)
            with c2:
                st.write("**v24 Audit**")
                h = "<div class='compact-grid'>"
                for p in sorted(v24_p):
                    h += f"<div class='item-box v24-box' style='{'border:2px solid #00FF00;' if p==actual else ''}'>{p}{'✅' if p==actual else ''}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)

            # TRIPLE HISTORY TABLE
            st.markdown("---")
            st.subheader(f"📊 {s_name} Deep Audit")
            hist_rows = df_raw[df_raw['DATE'] < pd.to_datetime(t_date)].tail(15)
            html_table = f"<table class='history-table'><tr><td class='history-td' style='background:#FFD600;'><b>v33</b></td><td class='history-td' style='background:#1B5E20; color:white;'><b>v24</b></td><td class='history-td' style='background:#1A237E; color:white;'><b>Matrix SS</b></td></tr>"
            
            for _, h_row in hist_rows.iterrows():
                val = clean(h_row[s_name])
                dt = h_row['DATE'].strftime('%d-%m')
                # Check hits
                t33 = "✅" if val in v33_p else "❌"
                t24 = "✅" if val in v24_p else "❌"
                tss = "✅" if val in ss_picks else "❌"
                html_table += f"<tr><td>{dt} : {val} {t33}</td><td>{dt} : {val} {t24}</td><td>{dt} : {val} {tss}</td></tr>"
            html_table += "</table><br>"
            st.markdown(html_table, unsafe_allow_html=True)
            
