import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v23.5 - Format Fix", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box-wrapper { display: flex; flex-direction: column; align-items: center; }
    .box { width: 85px; height: 85px; display: flex; align-items: center; justify-content: center; 
           font-size: 38px; font-weight: bold; border-radius: 12px; color: white; border: 2px solid #444; }
    .jodi-box { width: 130px; height: 85px; display: flex; align-items: center; justify-content: center; 
                font-size: 38px; font-weight: bold; border-radius: 12px; color: white; border: 2px solid #444; }
    .plus-equal { font-size: 45px; font-weight: bold; color: #fff; padding-top: 20px; }
    .green { background-color: #28a745 !important; box-shadow: 0 0 15px #28a745; }
    .yellow { background-color: #ffc107 !important; color: black !important; box-shadow: 0 0 15px #ffc107; }
    .red { background-color: #dc3545 !important; }
    .gray { background-color: #6c757d !important; border: 2px dashed #999; }
    .label-top { font-size: 14px; margin-bottom: 5px; font-weight: bold; color: #ccc; }
    .label-rashi { font-size: 18px; margin-top: 8px; font-weight: bold; color: #ffc107; background: #222; padding: 2px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA Super-AI v23.5 (History Clean Edition)")

def get_logic(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    try:
        raw = row.get(base_col, 0)
        # Convert to numeric safely, then to int
        base_val = int(pd.to_numeric(raw, errors='coerce') or 0)
    except: base_val = 0
    a_base, b_base = base_val // 10, base_val % 10
    a_scores, b_scores = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    if a_base == b_base and base_val > 0:
        a_scores[0] += 20; a_scores[5] += 20
    else:
        a_scores[a_base] += 15; a_scores[(a_base+5)%10] += 10
    b_scores[b_base] += 15; b_scores[(b_base+5)%10] += 10
    recent = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(int(pd.to_numeric(i, errors='coerce') or 0)) for i in recent if pd.notna(i)])
    for i in range(10):
        if str(i) not in pool:
            a_scores[i] += 10; b_scores[i] += 15
    return max(a_scores, key=a_scores.get), max(b_scores, key=b_scores.get)

uploaded_file = st.file_uploader("📂 Upload Excel", type=["csv", "xlsx"])

if uploaded_file:
    df = (pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file))
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    df['DATE'] = df['DATE'].astype(str).str.strip()

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=[c for c in ['DS', 'FB', 'GB', 'GL', 'DB', 'SG'] if c in df.columns])
    
    idx = df[df['DATE'] == sel_date].index[0]
    p_a, p_b = get_logic(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10 
    
    # Error Proofing Result
    actual_val = df.iloc[idx].get(target_s, "XX")
    act_a, act_b, act_num = None, None, None
    if pd.notna(actual_val) and str(actual_val).upper() != 'XX':
        try:
            act_num = int(pd.to_numeric(actual_val, errors='coerce'))
            act_a, act_b = act_num // 10, act_num % 10
        except: pass

    # Color Logic
    if act_num is None: color_a, color_b, color_j = "gray", "gray", "gray"
    else:
        color_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
        color_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
        if act_num == int(f"{p_a}{p_b}"): color_j = "green"
        elif color_a in ["green", "yellow"] and color_b in ["green", "yellow"]: color_j = "yellow"
        else: color_j = "red"

    with c3: st.metric(f"Live Result ({target_s})", str(actual_val).split('.')[0] if act_num is not None else "Wait")

    st.divider()
    st.markdown(f"""
    <div class="formula-container">
        <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {color_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {color_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box-wrapper"><div class="label-top">JODI</div><div class="jodi-box {color_j}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📜 History Record")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = get_logic(df, i, target_s)
        ra, rb = (ha+5)%10, (hb+5)%10
        h_act = df.iloc[i][target_s]
        
        # Clean History Result Display
        clean_res = str(h_act).split('.')[0] if pd.notna(h_act) else "XX"
        
        try:
            if pd.isna(h_act) or str(h_act).upper() == 'XX': s = "⏳"
            else:
                hv = int(pd.to_numeric(h_act, errors='coerce'))
                ha_act, hb_act = hv//10, hv%10
                if int(f"{ha}{hb}") == hv: s = "💎 DIRECT"
                elif (ha_act in [ha, ra]) and (hb_act in [hb, rb]): s = "👪 FAMILY"
                elif (ha_act in [ha, ra]) or (hb_act in [hb, rb]): s = "🎯 ANK"
                else: s = "❌"
        except: s = "⏳"
        history.append({"Date": df.iloc[i]['DATE'], "Result": clean_res, "Pred": f"{ha}+{hb}", "Status": s})
    st.table(pd.DataFrame(history))
    
