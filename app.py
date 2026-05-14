import streamlit as st
import pandas as pd

st.set_page_config(page_title="MAYA v40.0 - 36 Jodi Target", layout="wide")

st.markdown("""
    <style>
    .target-box { background: #111; padding: 15px; border: 2px solid #28a745; border-radius: 10px; margin-top: 10px; }
    .block-box { background: #111; padding: 15px; border: 2px solid #dc3545; border-radius: 10px; margin-top: 10px; }
    .stat-text { font-size: 18px; font-weight: bold; }
    .green-text { color: #28a745; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v40.0 (Target 36 Jodis)")

def calculate_logic_v40(df, idx, shift):
    # Step 1: Base Selection (Original Logic)
    val = 0
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    for i in range(1, 10):
        t_idx = idx - i
        if t_idx < 0: break
        raw = df.iloc[t_idx].get(base_col, "XX")
        if str(raw).isdigit() and int(raw) > 0:
            val = int(raw); break
    
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    # 4 Andar and 4 Bahar digits
    andar_set = {pa, ra, (pa+1)%10, (pa+9)%10} # Expanding for 4 digits each
    bahar_set = {pb, rb, (pb+1)%10, (pb+9)%10}
    
    # Blocked List
    blocked = set()
    for a in andar_set:
        for i in range(10): blocked.add(str(a) + str(i))
    for b in bahar_set:
        for i in range(10): blocked.add(str(i) + str(b))
        
    # Target List (Bachi hui 36 Jodis)
    target = []
    for i in range(100):
        jodi = str(i).zfill(2)
        if jodi not in blocked:
            target.append(jodi)
            
    return andar_set, bahar_set, target

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    as_set, bs_set, target_jodis = calculate_logic_v40(df, idx, target_s)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='block-box'><p class='stat-text'>🚫 Blocked Digits</p>
        Andar: {list(as_set)}<br>Bahar: {list(bs_set)}</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='target-box'><p class='stat-text'>✅ Target Jodis: <span class='green-text'>{len(target_jodis)}</span></p>
        {target_jodis[:18]}...</div>""", unsafe_allow_html=True)

    # Performance
    st.subheader("📜 10-Day Target Performance")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        _, _, t_list = calculate_logic_v40(df, i, target_s)
        res = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res.isdigit():
            if str(int(res)).zfill(2) in t_list: status = "✅ HIT"
        history.append({"Date": df.iloc[i]['DATE'], "Result": res, "Status": status})
    st.table(pd.DataFrame(history))
    
