import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v28.0 - TimeShift Pro", layout="wide")

st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box-wrapper { display: flex; flex-direction: column; align-items: center; }
    .box { width: 95px; height: 95px; display: flex; align-items: center; justify-content: center; 
           font-size: 45px; font-weight: bold; border-radius: 15px; color: white; border: 3px solid #555; }
    .plus-equal { font-size: 55px; font-weight: bold; color: #fff; padding-top: 15px; }
    .green { background-color: #28a745 !important; box-shadow: 0 0 20px #28a745; }
    .yellow { background-color: #ffc107 !important; color: black !important; box-shadow: 0 0 20px #ffc107; }
    .red { background-color: #dc3545 !important; }
    .gray { background-color: #333 !important; border: 3px dashed #666; }
    .label-top { font-size: 16px; margin-bottom: 5px; font-weight: bold; color: #bbb; }
    .label-rashi { font-size: 20px; margin-top: 10px; font-weight: bold; color: #ffc107; background: #111; padding: 4px 12px; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v28.0 (Dynamic Time-Frame Shift)")

# --- CLEANING & TIME-SHIFT LOGIC ---
def get_safe_base(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Pehle usi din ka base dekho
    val = df.iloc[idx].get(base_col, "XX")
    
    # Agar aaj ka base khali hai ya XX hai, toh ek din piche (Time-Frame Shift)
    if pd.isna(val) or str(val).upper() == 'XX' or val == 0:
        if idx > 0:
            val = df.iloc[idx-1].get(base_col, 0)
    
    # String cleaning (0000 problem fix)
    try:
        clean_val = int(float(str(val).split('.')[0]) if pd.notna(val) and str(val).upper() != 'XX' else 0)
    except: clean_val = 0
    return clean_val

def calculate_logic_v28(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    base_val = get_safe_base(df, idx, shift)
    
    d1, d2 = base_val // 10, base_val % 10
    scores_a, scores_b = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    
    # v12.5 Core Weights
    if d1 == d2 and base_val > 0:
        scores_a[0] += 20; scores_a[5] += 20
        scores_b[0] += 20; scores_b[5] += 20
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores_a[nxt] += 15; scores_b[(nxt+5)%10] += 12
    else:
        scores_a[d2] += 12; scores_b[(d2+5)%10] += 10
    
    # Gap Analysis across shifts (Last 12 records)
    recent = df.iloc[:idx+1].tail(12)[game_cols].values.flatten()
    pool = "".join([str(item).split('.')[0] for item in recent if str(item).split('.')[0].isdigit()])
    for i in range(10):
        if str(i) not in pool:
            scores_a[i] += 18; scores_b[i] += 18

    return max(scores_a, key=scores_a.get), max(scores_b, key=scores_b.get)

# --- APP INTERFACE ---
uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    df['DATE'] = df['DATE'].astype(str).str.strip()

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'] == sel_date].index[0]
    p_a, p_b = calculate_logic_v28(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10

    # Live Result Display Fix
    actual_val = df.iloc[idx].get(target_s, "XX")
    clean_act = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
    
    act_a, act_b = None, None
    if clean_act.isdigit():
        v = int(clean_act); act_a, act_b = v // 10, v % 10

    # Colors
    c_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
    c_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
    if clean_act == "XX": c_a = c_b = "gray"

    with c3: st.metric(f"Live {target_s}", clean_act)

    st.divider()

    # --- FORMULA ---
    st.markdown(f"""
    <div class="formula-container">
        <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box-wrapper"><div class="label-top">JODI</div><div class="box {'green' if c_a=='green' and c_b=='green' else ('yellow' if 'yellow' in [c_a, c_b] else ('red' if c_a!='gray' else 'gray'))}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- HISTORY ---
    st.subheader("📜 Live Backtest History")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = calculate_logic_v28(df, i, target_s)
        h_act = str(df.iloc[i][target_s]).split('.')[0]
        try:
            if h_act.isdigit():
                hv = int(h_act); ha_act, hb_act = hv//10, hv%10
                ra, rb = (ha+5)%10, (hb+5)%10
                if ha_act == ha and hb_act == hb: s = "💎 DIRECT"
                elif (ha_act in [ha, ra]) and (hb_act in [hb, rb]): s = "👪 FAMILY"
                elif (ha_act in [ha, ra]) or (hb_act in [hb, rb]): s = "🎯 ANK"
                else: s = "❌"
            else: s = "⏳"
        except: s = "⏳"
        history.append({"Date": df.iloc[i]['DATE'], "Result": h_act, "AI Pred": f"{ha}+{hb}", "Status": s})
    st.table(pd.DataFrame(history))
             
