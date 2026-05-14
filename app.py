import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v41.0 - Square Grid Engine", layout="wide")

# Custom UI for Grid and Formula
st.markdown("""
    <style>
    .main-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .grid-container { 
        display: grid; 
        grid-template-columns: repeat(6, 1fr); 
        gap: 10px; 
        max-width: 500px; 
        margin: 0 auto; 
    }
    .grid-item { 
        background-color: #f0fff4; 
        color: #234d20; 
        padding: 15px; 
        border-radius: 8px; 
        font-size: 22px; 
        font-weight: bold; 
        text-align: center; 
        border: 2px solid #c6f6d5;
    }
    .formula-box { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px; 
        background: #fdfdfd; 
        padding: 15px; 
        border-radius: 12px; 
        border: 2px solid #eee;
    }
    .small-box { 
        width: 60px; height: 60px; 
        display: flex; align-items: center; justify-content: center; 
        font-size: 24px; font-weight: bold; border-radius: 8px; border: 2px solid #ccc;
    }
    .rashi-text { font-size: 14px; color: #666; text-align: center; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v41.0 (36-Jodi Square Grid)")

# --- DYNAMIC DIVERSITY LOGIC ---
def get_diverse_logic(df, idx, col):
    """Scan back until we find 4 unique digits (2 Main + 2 Rashi)"""
    for jump in range(1, 15):
        t_idx = idx - jump
        if t_idx < 0: break
        
        val_raw = df.iloc[t_idx].get(col, "XX")
        try:
            val = int(float(str(val_raw).split('.')[0]))
            if val <= 0: continue
            
            d1, d2 = val // 10, val % 10
            pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
            pb = (d2 + 1) % 10
            ra, rb = (pa + 5) % 10, (pb + 5) % 10
            
            # Check for 4 unique digits
            unique_check = {pa, ra, pb, rb}
            if len(unique_check) == 4:
                return pa, ra, pb, rb, jump
        except: continue
    return 1, 6, 2, 7, 0 # Default Fallback

uploaded_file = st.file_uploader("📂 Upload Excel", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    
    # Run Diversity Search
    pa, ra, pb, rb, used_jump = get_diverse_logic(df, idx, flow.get(target_s, 'DS'))
    
    # Elimination Logic
    as_set = {pa, ra}
    bs_set = {pb, rb}
    blocked = set()
    for a in as_set:
        for i in range(10): blocked.add(str(a) + str(i))
    for b in bs_set:
        for i in range(10): blocked.add(str(i) + str(b))
    
    target_jodis = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked]

    # --- TOP UI: FORMULA BOX ---
    st.subheader(f"🔢 Analysis Base (Used Gap: {used_jump} Day)")
    st.markdown(f"""
    <div class="formula-box">
        <div><div class="small-box" style="background:#e3f2fd;">{pa}</div><div class="rashi-text">R: {ra}</div></div>
        <div style="font-size:30px;">+</div>
        <div><div class="small-box" style="background:#fff3e0;">{pb}</div><div class="rashi-text">R: {rb}</div></div>
        <div style="font-size:30px;">=</div>
        <div class="small-box" style="background:#f1f8e9; width:100px;">{pa}{pb}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- MIDDLE UI: SQUARE GRID (6x6) ---
    st.markdown(f"### ✅ Target Jodis (Total {len(target_jodis)})")
    grid_html = '<div class="grid-container">'
    for jodi in target_jodis:
        grid_html += f'<div class="grid-item">{jodi}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    st.divider()

    # --- BOTTOM UI: HISTORY ---
    st.subheader("📜 Backtest History")
    history_data = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        h_pa, h_ra, h_pb, h_rb, _ = get_diverse_logic(df, i, flow.get(target_s, 'DS'))
        h_blocked = set()
        for a in {h_pa, h_ra}:
            for j in range(10): h_blocked.add(str(a) + str(j))
        for b in {h_pb, h_rb}:
            for j in range(10): h_blocked.add(str(j) + str(b))
            
        res_raw = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res_raw.isdigit():
            r_val = str(int(res_raw)).zfill(2)
            status = "✅ HIT" if r_val not in h_blocked else "🚫 BLOCKED"
            
        history_data.append({"Date": df.iloc[i]['DATE'], "Result": res_raw, "Status": status})
    st.table(pd.DataFrame(history_data))
        
