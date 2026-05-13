import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v21.5 - Strict Match", layout="wide")

# Custom CSS for boxes and colors
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 20px; }
    .box { width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; 
           font-size: 35px; font-weight: bold; border-radius: 10px; color: white; border: 2px solid #333; }
    .jodi-box { width: 120px; height: 80px; display: flex; align-items: center; justify-content: center; 
                font-size: 35px; font-weight: bold; border-radius: 10px; color: white; border: 2px solid #333; }
    .plus-equal { font-size: 40px; font-weight: bold; color: #fff; }
    .green { background-color: #28a745 !important; }
    .yellow { background-color: #ffc107 !important; color: black !important; } /* For Mirror Match */
    .red { background-color: #dc3545 !important; }
    .label { font-size: 14px; text-align: center; font-weight: bold; color: #ccc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA Super-AI v21.5 (Strict Result Match)")

# Core Logic Engine (No Change in Accuracy)
def get_logic(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    try:
        raw = row.get(base_col, 0)
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
    pool = "".join([str(i) for i in recent if str(i).isdigit()])
    for i in range(10):
        if str(i) not in pool:
            a_scores[i] += 10; b_scores[i] += 15
            
    return max(a_scores, key=a_scores.get), max(b_scores, key=b_scores.get)

uploaded_file = st.file_uploader("📂 Upload Excel", type=["csv", "xlsx"])

if uploaded_file:
    df = (pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') 
          else pd.read_csv(uploaded_file))
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    df['DATE'] = df['DATE'].astype(str).str.strip()

    # --- TOP FIXED PANEL ---
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        all_dates = df['DATE'].unique().tolist()[::-1]
        sel_date = st.selectbox("📅 Date:", options=all_dates)
    with c2:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        available = [c for c in game_cols if c in df.columns]
        target_s = st.selectbox("🎰 Shift:", options=available)
    
    idx = df[df['DATE'] == sel_date].index[0]
    p_a, p_b = get_logic(df, idx, target_s)
    actual_val = df.iloc[idx][target_s]
    
    try:
        act_num = int(pd.to_numeric(actual_val, errors='coerce'))
        act_a, act_b = act_num // 10, act_num % 10
    except: act_a, act_b = None, None

    # --- STRICT COLOR LOGIC ---
    # Andar Check
    if act_a is not None:
        if p_a == act_a: color_a = "green"
        elif (p_a+5)%10 == act_a: color_a = "yellow" # Mirror pass
        else: color_a = "red"
    else: color_a = "red"

    # Bahar Check
    if act_b is not None:
        if p_b == act_b: color_b = "green"
        elif (p_b+5)%10 == act_b: color_b = "yellow" # Mirror pass
        else: color_b = "red"
    else: color_b = "red"

    # Jodi Check - ONLY GREEN IF DIRECT MATCH
    if act_num is not None and int(f"{p_a}{p_b}") == act_num:
        color_j = "green"
    elif color_a in ["green", "yellow"] and color_b in ["green", "yellow"]:
        color_j = "yellow" # Family/Mirror pass
    else:
        color_j = "red"

    with c3:
        st.metric(f"Live Result ({target_s})", actual_val if actual_val != 0 else "Waiting")

    st.divider()

    # --- MATHEMATICAL FORMULA DISPLAY ---
    st.markdown(f"""
    <div class="formula-container">
        <div><div class="label">Andar (A)</div><div class="box {color_a}">{p_a}</div></div>
        <div class="plus-equal">+</div>
        <div><div class="label">Bahar (B)</div><div class="box {color_b}">{p_b}</div></div>
        <div class="plus-equal">=</div>
        <div><div class="label">Jodi</div><div class="jodi-box {color_j}">{p_a}{p_b}</div></div>
    </div>
    <p style='text-align:center;'><b>Note:</b> <span style='color:#28a745;'>Green</span> = Direct, <span style='color:#ffc107;'>Yellow</span> = Mirror/Family, <span style='color:#dc3545;'>Red</span> = Fail</p>
    """, unsafe_allow_html=True)

    # --- PERFORMANCE TABLE ---
    st.subheader("📜 10-Day Performance Record")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = get_logic(df, i, target_s)
        h_act = df.iloc[i][target_s]
        try:
            h_v = int(pd.to_numeric(h_act, errors='coerce')); h_a, h_b = h_v // 10, h_v % 10
            # History Hit Logic
            if int(f"{ha}{hb}") == h_v: s = "💎 DIRECT"
            elif (ha==h_a or (ha+5)%10==h_a) and (hb==h_b or (hb+5)%10==h_b): s = "👪 FAMILY"
            elif (ha==h_a or (ha+5)%10==h_a) or (hb==h_b or (hb+5)%10==h_b): s = "🎯 ANK"
            else: s = "❌"
        except: s = "➖"
        history.append({"Date": df.iloc[i]['DATE'], "Result": h_act, "AI Pred": f"{ha}+{hb}", "Status": s})
    
    st.table(pd.DataFrame(history))
    
