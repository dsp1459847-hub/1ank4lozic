import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.0 - 90 Gap Scanner", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .live-res { background: #1e293b; color: #fbbf24; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; }
    .grid-square { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 400px; margin: 10px auto; }
    .grid-item { background: #ffffff; color: #1e40af; padding: 12px; border-radius: 8px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #bfdbfe; }
    .worst-badge { background: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin: 2px; border: 1px solid #fecaca; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.0 (90-Gap Deep Scanner)")

def find_worst_gaps_90(df, idx, col):
    """1 se 90 tak ke gaps ko scan karke sabse bekar results nikalna"""
    gap_scores = {}
    # Scan gaps from 1 to 90
    for g in range(1, 91):
        if idx - g - 10 < 0: continue
        score = 0
        for check in range(idx-10, idx):
            if check - g < 0: continue
            pred = str(df.iloc[check-g].get(col, "XX")).split('.')[0]
            act = str(df.iloc[check].get(col, "XX")).split('.')[0]
            if pred.isdigit() and act.isdigit() and pred == act:
                score += 1 # Agar match ho gaya (Yaani gap 'Acha' hai, humein 'Bekar' chahiye)
        gap_scores[g] = score
    
    # Sabse kam score (sabse bekar) wale 5 gaps uthana
    worst_gaps = sorted(gap_scores, key=gap_scores.get)[:5]
    
    # In bekar gaps se common digits nikalna
    bad_andar = []
    bad_bahar = []
    for wg in worst_gaps:
        val = str(df.iloc[idx-wg].get(col, 0)).split('.')[0]
        if val.isdigit():
            bad_andar.append(int(val)//10)
            bad_bahar.append(int(val)%10)
            
    # Common digits (Jo sabse zyada baar bekar gaps mein aaye)
    final_a = max(set(bad_andar), key=bad_andar.count) if bad_andar else 0
    final_b = max(set(bad_bahar), key=bad_bahar.count) if bad_bahar else 5
    return final_a, final_b, worst_gaps

def calculate_v48_logic(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # 1. Level 1: Code 37 Base (64 Jodis)
    val = 0
    for i in range(1, 15):
        if idx - i >= 0:
            raw = df.iloc[idx-i].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    blocked_64 = set()
    for a in {pa, ra}:
        for i in range(10): blocked_64.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked_64.add(f"{i}{b}")
    
    target_36 = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked_64]
    
    # 2. Level 2: Worst 90-Gap Filter
    wa, wb, wgaps = find_worst_gaps_90(df, idx, base_col)
    
    extra_hatao = set()
    # Hatao worst gap ke sets
    for i in range(10):
        extra_hatao.add(f"{wa}{i}")
        extra_hatao.add(f"{i}{wb}")
        
    final_list = [j for j in target_36 if j not in extra_hatao]
    return final_list[:16], final_list[:9], wgaps

uploaded_file = st.file_uploader("📂 Upload Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    
    # --- LIVE RESULT ---
    live_val = str(df.iloc[idx].get(target_s, "XX")).split('.')[0]
    st.markdown(f'<div class="live-res">RESULT: <span style="font-size:30px; font-weight:bold;">{live_val}</span></div>', unsafe_allow_html=True)

    # --- CALCULATE ---
    t16, t9, worst_gaps = calculate_v48_logic(df, idx, target_s)

    st.divider()
    st.write(f"⚠️ **Worst Gaps Found:** " + " ".join([f'<span class="worst-badge">Gap-{g}</span>' for g in worst_gaps]), unsafe_allow_html=True)

    # --- TARGET BOXES ---
    c1, c2 = st.columns(2)
    with c1:
        st.write("**✅ Stable Target (Square 16)**")
        grid_html = '<div class="grid-square">'
        for j in t16: grid_html += f'<div class="grid-item">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    with c2:
        st.write("**💎 Super Hit (Square 9)**")
        grid_html = '<div class="grid-square" style="grid-template-columns: repeat(3, 1fr);">'
        for j in t9: grid_html += f'<div class="grid-item" style="background:#fff7ed; color:#9a3412; border-color:#fed7aa;">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- HISTORY ---
    st.divider()
    st.subheader("📜 10-Day Deep Scan Backtest")
    hist = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        h16, h9, _ = calculate_v48_logic(df, i, target_s)
        res = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res.isdigit():
            rv = str(int(res)).zfill(2)
            if rv in h9: status = "💎 SUPER"
            elif rv in h16: status = "✅ HIT"
        hist.append({"Date": df.iloc[i]['DATE'], "Result": res, "Status": status})
    st.table(pd.DataFrame(hist))
    
