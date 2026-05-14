import streamlit as st
import pandas as pd

# Page Setup - Light Theme Focus
st.set_page_config(page_title="MAYA v40.5 - Clear View", layout="wide")

# Custom CSS for High Visibility (Light Colors)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTable { background-color: white; border-radius: 10px; }
    
    /* Result Box Styling */
    .target-container { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #28a745; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .jodi-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 10px;
        text-align: center;
    }
    
    .jodi-item {
        background-color: #e9f7ef;
        color: #1e7e34;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 20px;
        border: 1px solid #c3e6cb;
    }
    
    .block-item {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 18px;
        border: 1px solid #f5c6cb;
        margin: 2px;
        display: inline-block;
    }
    
    .title-text { color: #1e1e1e; font-size: 32px; font-weight: bold; text-align: center; }
    .label-text { font-size: 18px; font-weight: bold; color: #444; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-text">🎯 MAYA v40.5 (36-Jodi Clean Target)</p>', unsafe_allow_html=True)

def calculate_logic_v40_5(df, idx, shift):
    # Step 1: Base Selection (Original Pure Logic)
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
    
    # Andar Set (2 Main + 2 Rashi = 4 Digits)
    # Bahar Set (2 Main + 2 Rashi = 4 Digits)
    as_set = sorted(list({pa, ra, (pa+1)%10, (pa+9)%10}))
    bs_set = sorted(list({pb, rb, (pb+1)%10, (pb+9)%10}))
    
    # Blocked List (Elimination)
    blocked = set()
    for a in as_set:
        for i in range(10): blocked.add(str(a) + str(i))
    for b in bs_set:
        for i in range(10): blocked.add(str(i) + str(b))
        
    # Target Jodis (Bachi hui strictly 36 Jodis)
    target = []
    for i in range(100):
        jodi = str(i).zfill(2)
        if jodi not in blocked:
            target.append(jodi)
            
    return as_set, bs_set, target

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    col1, col2 = st.columns(2)
    with col1:
        sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with col2:
        target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    as_set, bs_set, target_jodis = calculate_logic_v40_5(df, idx, target_s)

    st.divider()

    # --- TOP SECTION: ELIMINATED ANK ---
    st.markdown('<p class="label-text">🚫 Eliminated Sets (Inko Hata Diya):</p>', unsafe_allow_html=True)
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        st.write("**Andar Digits:**")
        for a in as_set: st.markdown(f'<span class="block-item">{a}</span>', unsafe_allow_html=True)
    with e_col2:
        st.write("**Bahar Digits:**")
        for b in bs_set: st.markdown(f'<span class="block-item">{b}</span>', unsafe_allow_html=True)

    # --- MIDDLE SECTION: TARGET JODIS (BIG & CLEAR) ---
    st.markdown(f'<div class="target-container"><p class="label-text" style="color:#28a745;">✅ Target Jodis ({len(target_jodis)} Total):</p>', unsafe_allow_html=True)
    
    # Display Jodis in a clear grid
    cols = st.columns(10)
    for i, jodi in enumerate(target_jodis):
        cols[i % 10].markdown(f'<div class="jodi-item">{jodi}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTTOM SECTION: HISTORY ---
    st.subheader("📜 10-Day Live Tracking (Elimination Test)")
    history_data = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        _, _, t_list = calculate_logic_v40_5(df, i, target_s)
        res_raw = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        
        status = "❌ FAIL"
        if res_raw.isdigit():
            r_val = str(int(res_raw)).zfill(2)
            if r_val in t_list: status = "✅ HIT (Target)"
            else: status = "🚫 BLOCKED"
            
        history_data.append({"Date": df.iloc[i]['DATE'], "Result": res_raw, "Status": status})
    
    st.table(pd.DataFrame(history_data))
    
