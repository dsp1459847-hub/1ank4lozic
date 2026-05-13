import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v26.0 - 12.5 Base Fixed", layout="wide")

# Custom CSS for Formula UI (Mathematical Style)
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box-wrapper { display: flex; flex-direction: column; align-items: center; }
    .box { width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; 
           font-size: 40px; font-weight: bold; border-radius: 12px; color: white; border: 3px solid #444; }
    .plus-equal { font-size: 50px; font-weight: bold; color: #fff; padding-top: 15px; }
    .green { background-color: #28a745 !important; box-shadow: 0 0 20px #28a745; }
    .red { background-color: #dc3545 !important; }
    .gray { background-color: #444 !important; border: 3px dashed #777; }
    .label-top { font-size: 16px; margin-bottom: 5px; font-weight: bold; color: #bbb; }
    .label-rashi { font-size: 20px; margin-top: 10px; font-weight: bold; color: #ffc107; background: #111; padding: 4px 12px; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA Super-AI v26.0 (v12.5 Position Edition)")

# --- v12.5 CORE LOGIC (LOCKED & RESTORED) ---
def calculate_12_5_logic(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    history_df = df.iloc[:idx + 1]
    scores = {i: 0 for i in range(10)}
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    try:
        raw_val = row.get(base_col, 0)
        base_val = int(float(str(raw_val).split('.')[0]) if pd.notna(raw_val) and str(raw_val).upper() != 'XX' else 0)
    except: base_val = 0
    
    d1, d2 = base_val // 10, base_val % 10
    
    # Restoring v12.5 Pattern Weights
    if d1 == d2 and base_val > 0:
        scores[0] += 20; scores[5] += 20
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores[nxt] += 15; scores[(nxt+5)%10] += 12
    else:
        scores[d2] += 12; scores[(d2 + 5) % 10] += 10
    
    # Gap Analysis
    recent = history_df.tail(10)[game_cols].values.flatten()
    pool = "".join([str(item).split('.')[0] for item in recent if str(item).split('.')[0].isdigit()])
    for i in range(10):
        if str(i) not in pool: scores[i] += 18
    
    res_df = pd.DataFrame(scores.items()).sort_values(by=1, ascending=False)
    # Positioning: Top 1 as Andar, Top 2 as Bahar (Logic restored to 12.5 style)
    return int(res_df.iloc[0][0]), int(res_df.iloc[1][0])

@st.cache_data
def load_data(file):
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
    df = load_data(uploaded_file)
    if df is not None:
        # --- UI SELECTORS (TOP) ---
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].unique().tolist()[::-1])
        with c2: target_s = st.selectbox("🎰 Shift:", options=[c for c in ['DS', 'FB', 'GB', 'GL', 'DB', 'SG'] if c in df.columns])
        
        idx = df[df['DATE'] == sel_date].index[0]
        p_a, p_b = calculate_12_5_logic(df, idx, target_s)
        r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10
        
        # Live Result Data
        actual_val = df.iloc[idx].get(target_s, "XX")
        clean_act = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
        
        act_a, act_b = None, None
        if clean_act.isdigit():
            v = int(clean_act)
            act_a, act_b = v // 10, v % 10

        # Smart Coloring
        c_a = "green" if act_a in [p_a, r_a] else "red"
        c_b = "green" if act_b in [p_b, r_b] else "red"
        if clean_act == "XX": c_a = c_b = "gray"

        with c3: st.metric(f"Live Result {target_s}", clean_act)

        st.divider()

        # --- MATHEMATICAL DISPLAY [A] + [B] = [JODI] ---
        st.markdown(f"""
        <div class="formula-container">
            <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
            <div class="plus-equal">+</div>
            <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
            <div class="plus-equal">=</div>
            <div class="box-wrapper"><div class="label-top">JODI</div><div class="box {'green' if c_a=='green' and c_b=='green' else ('red' if c_a!='gray' else 'gray')}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # --- LIVE HISTORY WITH TICK (REQUIREMENT) ---
        st.subheader("📜 11-Day Performance Tracker")
        history = []
        for i in range(idx - 11, idx + 1):
            if i < 0: continue
            ha, hb = calculate_12_5_logic(df, i, target_s)
            h_act = str(df.iloc[i][target_s]).split('.')[0]
            try:
                if h_act.isdigit():
                    hv = int(h_act); ha_act, hb_act = hv//10, hv%10
                    ra, rb = (ha+5)%10, (hb+5)%10
                    # Tick logic
                    is_p = "✅ PASS" if (ha_act in [ha, ra]) or (hb_act in [hb, rb]) else "❌ FAIL"
                else: is_p = "⏳"
            except: is_p = "⏳"
            history.append({"Date": df.iloc[i]['DATE'], "Result": h_act, "A+B Prediction": f"{ha}+{hb}", "Status": is_p})
        
        st.table(pd.DataFrame(history))
        
