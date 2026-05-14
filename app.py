import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v37.0 - Absolute Original", layout="wide")

# Custom UI for Clarity
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

st.title("🎯 MAYA v37.0 (The First Original Logic)")

# --- RESTORING THE VERY FIRST LOGIC (BACK TO BASICS) ---

def get_pure_base(df, idx, col):
    """Pichli shift ka asli number bina kisi filter ke"""
    for i in range(1, 10):
        t_idx = idx - i
        if t_idx < 0: break
        val = df.iloc[t_idx].get(col, "XX")
        try:
            clean = str(val).split('.')[0]
            if clean.isdigit() and int(clean) > 0:
                return int(clean)
        except: continue
    return 14 # Fallback

def calculate_first_logic(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Sabse pehla base selection
    base_val = get_pure_base(df, idx, base_col)
    
    # --- THE ORIGINAL 1st CODE RULES ---
    # Harf/Ank positioning based on the unit and tens digit
    d1 = base_val // 10  # Andar
    d2 = base_val % 10   # Bahar
    
    # 1. Primary Ank Logic (Simple Addition/Subtraction)
    p_a = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    p_b = (d2 + 1) % 10
    
    # 2. Secondary/Rashi Logic for variety
    r_a = (p_a + 5) % 10
    r_b = (p_b + 5) % 10
    
    return p_a, p_b

# --- DATA PROCESSING ---
uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    df['DATE'] = df['DATE'].astype(str).str.strip()

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: sel_date = st.selectbox("📅 Select Date:", options=df['DATE'].unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Select Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'] == sel_date].index[0]
    p_a, p_b = calculate_first_logic(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10

    # Result Cleaning
    actual_val = df.iloc[idx].get(target_s, "XX")
    clean_act = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
    
    act_a, act_b = None, None
    if clean_act.isdigit():
        v = int(clean_act); act_a, act_b = v // 10, v % 10

    # Strict Colors
    c_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
    c_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
    if clean_act == "XX" or clean_act == "0": c_a = c_b = "gray"

    with c3: st.metric(f"Live {target_s}", clean_act)

    st.divider()

    # --- DISPLAY FORMULA ---
    st.markdown(f"""
    <div class="formula-container">
        <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box-wrapper"><div class="label-top">JODI</div><div class="box {'green' if (act_a==p_a and act_b==p_b) else ('yellow' if (act_a in [p_a,r_a] and act_b in [p_b,r_b]) else ('red' if c_a!='gray' else 'gray'))}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- 11-DAY HISTORY (CHECK THIS!) ---
    st.subheader("📜 11-Day Back-Test History (Original Logic)")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = calculate_first_logic(df, i, target_s)
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
    
