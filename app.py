import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v25.0 - Original Logic", layout="wide")

# Custom CSS for Mathematical Formula UI
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box-wrapper { display: flex; flex-direction: column; align-items: center; }
    .box { width: 95px; height: 95px; display: flex; align-items: center; justify-content: center; 
           font-size: 45px; font-weight: bold; border-radius: 15px; color: white; border: 3px solid #555; }
    .jodi-box { width: 160px; height: 95px; display: flex; align-items: center; justify-content: center; 
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

st.title("🎯 MAYA Super-AI v25.0 (Original Logic Locked)")

# --- THE REAL ORIGINAL LOGIC (NO MODIFICATIONS) ---
def calculate_original_logic(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    try:
        # Strict 0000 cleaning
        raw_val = row.get(base_col, 0)
        clean_base = str(raw_val).split('.')[0]
        base_val = int(clean_base) if clean_base.isdigit() else 0
    except: base_val = 0
    
    d1, d2 = base_val // 10, base_val % 10
    scores = {i: 0 for i in range(10)}
    
    # --- EXACT DOPAHAR WEIGHTS ---
    if d1 == d2 and base_val > 0:
        scores[0] += 25; scores[5] += 25
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores[nxt] += 20; scores[(nxt+5)%10] += 15
    else:
        scores[d2] += 15; scores[(d2 + 5) % 10] += 12
        
    # Gap Analysis
    recent_data = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(item).split('.')[0] for item in recent_data if str(item).split('.')[0].isdigit()])

    for i in range(10):
        if str(i) not in pool: scores[i] += 22
            
    res_df = pd.DataFrame(scores.items()).sort_values(by=1, ascending=False)
    # Returning the top calculated ank as both A and B for strictness
    top_ank = int(res_df.iloc[0][0])
    return top_ank, top_ank # Using your original single-ank derived logic

@st.cache_data
def load_and_fix_data(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        return df
    except: return None

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_fix_data(uploaded_file)
    if df is not None:
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].unique().tolist()[::-1])
        with c2: target_s = st.selectbox("🎰 Shift:", options=[c for c in ['DS', 'FB', 'GB', 'GL', 'DB', 'SG'] if c in df.columns])
        
        idx = df[df['DATE'] == sel_date].index[0]
        p_a, p_b = calculate_original_logic(df, idx, target_s)
        r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10
        
        actual_val = df.iloc[idx].get(target_s, "XX")
        clean_actual = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
        
        act_a, act_b, act_num = None, None, None
        if clean_actual.isdigit():
            act_num = int(clean_actual)
            act_a, act_b = act_num // 10, act_num % 10

        # Dynamic Coloring
        if act_num is None or clean_actual == "XX": color_a = color_b = color_j = "gray"
        else:
            color_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
            color_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
            if act_num == int(f"{p_a}{p_b}"): color_j = "green"
            elif color_a in ["green", "yellow"] and color_b in ["green", "yellow"]: color_j = "yellow"
            else: color_j = "red"

        with c3: st.metric(f"Result {target_s}", clean_actual)

        st.divider()

        # --- THE FORMULA ---
        st.markdown(f"""
        <div class="formula-container">
            <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {color_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
            <div class="plus-equal">+</div>
            <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {color_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
            <div class="plus-equal">=</div>
            <div class="box-wrapper"><div class="label-top">JODI</div><div class="jodi-box {color_j}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # --- PERFORMANCE ---
        st.subheader("📜 History Record")
        history = []
        for i in range(idx - 10, idx + 1):
            if i < 0: continue
            ha, hb = calculate_original_logic(df, i, target_s)
            h_act = str(df.iloc[i][target_s]).split('.')[0]
            try:
                if h_act.isdigit():
                    hv = int(h_act); ha_act, hb_act = hv//10, hv%10
                    ra, rb = (ha+5)%10, (hb+5)%10
                    if int(f"{ha}{hb}") == hv: s = "💎 DIRECT"
                    elif (ha_act in [ha, ra]) and (hb_act in [hb, rb]): s = "👪 FAMILY"
                    elif (ha_act in [ha, ra]) or (hb_act in [hb, rb]): s = "🎯 ANK"
                    else: s = "❌"
                else: s = "⏳"
            except: s = "⏳"
            history.append({"Date": df.iloc[i]['DATE'], "Result": h_act, "AI Pred": f"{ha}+{hb}", "Status": s})
        st.table(pd.DataFrame(history))

