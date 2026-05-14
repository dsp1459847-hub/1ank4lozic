import streamlit as st
import pandas as pd

# Page Configuration for Mobile
st.set_page_config(page_title="MAYA v46.0", layout="wide")

# Custom CSS for 4x5 Grid and Fixed Display
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .report-card { 
        background: #ffffff; padding: 10px; border-radius: 10px; 
        border: 1px solid #ddd; margin-bottom: 10px; 
    }
    /* 4x5 Grid Styling */
    .grid-container { 
        display: grid; 
        grid-template-columns: repeat(4, 1fr); 
        gap: 5px; 
        max-width: 100%;
    }
    .grid-item { 
        background-color: #fef9c3; color: #854d0e; padding: 12px 5px; 
        border-radius: 5px; font-size: 18px; font-weight: bold; 
        text-align: center; border: 1px solid #fde68a;
    }
    .history-table { font-size: 12px !important; width: 100%; }
    .status-hit { color: #16a34a; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

def get_logic_v46(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    val = 0
    for i in range(1, 12):
        t_idx = idx - i
        if t_idx >= 0:
            raw = df.iloc[t_idx].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    blocked = set()
    for a in {pa, ra}:
        for i in range(10): blocked.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked.add(f"{i}{b}")
    
    # Worst Gap Elimination (3 & 5)
    extra_hatao = set()
    for g in [3, 5]:
        if idx - g >= 0:
            v = str(df.iloc[idx-g].get(base_col, 0)).split('.')[0]
            if v.isdigit():
                vn = int(v)
                for i in range(10): 
                    extra_hatao.add(f"{vn//10}{i}")
                    extra_hatao.add(f"{i}{vn%10}")

    target = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked and str(i).zfill(2) not in extra_hatao]
    return target[:20] # Sirf top 20 ank for 4x5 grid

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]

    # --- TOP: LIVE HISTORY (1st Priority) ---
    st.markdown("### 📜 Live Result & History")
    hist_data = []
    for i in range(idx - 5, idx + 1): # Last 5 days for compact view
        if i < 0: continue
        h_target = get_logic_v46(df, i, target_s)
        res = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res.isdigit():
            rv = str(int(res)).zfill(2)
            status = "✅ HIT" if rv in h_target else "🚫"
        hist_data.append({"Date": df.iloc[i]['DATE'], "Res": res, "St": status})
    st.table(pd.DataFrame(hist_data))

    st.divider()

    # --- MIDDLE: 4x5 TARGET GRID ---
    t_20 = get_logic_v46(df, idx, target_s)
    st.markdown(f"### 💎 Super Hit (Top {len(t_20)})")
    
    grid_html = '<div class="grid-container">'
    for jodi in t_20:
        grid_html += f'<div class="grid-item">{jodi}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    st.markdown("<p style='font-size:12px; color:gray; text-align:center;'>Mobile Display Optimized - No Scroll Needed</p>", unsafe_allow_html=True)
