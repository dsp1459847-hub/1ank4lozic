import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v31.0 - Infinite Search", layout="wide")

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
    .label-rashi { font-size: 18px; margin-top: 8px; font-weight: bold; color: #ffc107; background: #111; padding: 4px 12px; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v31.0 (Infinite Timeframe Search)")

# --- INFINITE BASE SEARCH ---
def get_infinite_base(df, idx, col_name):
    """Jab tak asli number na mile, piche jump maarte raho"""
    # Steps: 1 din piche, 2 din, 7 din, 14 din, 30 din
    search_steps = [1, 2, 7, 14, 30, 3, 4, 5, 6]
    
    for step in search_steps:
        t_idx = idx - step
        if t_idx >= 0:
            val = df.iloc[t_idx].get(col_name, "XX")
            # Strict Check: Khali, XX, 0, ya 00 nahi hona chahiye
            if pd.notna(val) and str(val).upper() != 'XX' and str(val) not in ['0', '00', '0.0', '']:
                try:
                    num = int(float(str(val).split('.')[0]))
                    if num > 0: return num # Sirf tab return karo jab 0 se bada ho
                except: continue
                
    # Agar phir bhi nahi milta, toh kisi bhi shift ka pichla best result uthao
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    for col in game_cols:
        val = df.iloc[idx-1].get(col, "XX") if idx > 0 else "XX"
        if str(val).isdigit() and int(val) > 0:
            return int(val)
            
    return 14 # Ultimate fallback taaki 00 na aaye

def calculate_logic_v31(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Base Value Selection
    base_val = get_infinite_base(df, idx, base_col)
    
    d1, d2 = base_val // 10, base_val % 10
    scores_a, scores_b = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    
    # Accuracy Logic (v12.5 Weights)
    if d1 == d2:
        scores_a[0] += 20; scores_a[5] += 20
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores_a[nxt] += 18; scores_b[(nxt+5)%10] += 15
    else:
        scores_a[d2] += 15; scores_b[(d2+5)%10] += 12
    
    # Multi-Timeframe Gap Analysis (Variety Fix)
    pool = ""
    for jump in [1, 7, 14]: # Aaj, Pichla hafta, usse pichla hafta
        if idx - jump >= 0:
            row_data = "".join([str(x).split('.')[0] for x in df.iloc[idx-jump][game_cols].values if str(x).isdigit()])
            pool += row_data
            
    for i in range(10):
        if str(i) not in pool:
            scores_a[i] += 15; scores_b[i] += 15

    return max(scores_a, key=scores_a.get), max(scores_b, key=scores_b.get)

# --- UI ---
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
    p_a, p_b = calculate_logic_v31(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10

    actual_val = df.iloc[idx].get(target_s, "XX")
    clean_act = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
    
    act_a, act_b = None, None
    if clean_act.isdigit():
        v = int(clean_act); act_a, act_b = v // 10, v % 10

    c_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
    c_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
    if clean_act == "XX": c_a = c_b = "gray"

    with c3: st.metric(f"Result {target_s}", clean_act)

    st.divider()

    # Formula Display
    st.markdown(f"""
    <div class="formula-container">
        <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box-wrapper"><div class="label-top">JODI</div><div class="box {'green' if c_a=='green' and c_b=='green' else ('yellow' if 'yellow' in [c_a, c_b] else ('red' if c_a!='gray' else 'gray'))}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # History
    st.subheader(f"📜 {target_s} Performance Tracker")
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = calculate_logic_v31(df, i, target_s)
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
    
