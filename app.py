import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v20.0 - Visual Hit Tracker", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .green-box { background-color: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    .red-box { background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    .gray-box { background-color: #6c757d; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA Super-AI v20.0 (Visual Color Match)")

# --- ACCURACY ENGINE (STRICT) ---
def get_ab_prediction(df, idx, shift):
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
    
    # Position Logic (Locked Accuracy)
    if a_base == b_base and base_val > 0:
        a_scores[0] += 20; a_scores[5] += 20
    else:
        a_scores[a_base] += 15; a_scores[(a_base+5)%10] += 10
    
    b_scores[b_base] += 15; b_scores[(b_base+5)%10] += 10
    
    # Gap Pattern (Last 10 Days)
    recent = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(i) for i in recent if str(i).isdigit()])
    for i in range(10):
        if str(i) not in pool:
            a_scores[i] += 10; b_scores[i] += 15
            
    return max(a_scores, key=a_scores.get), max(b_scores, key=b_scores.get)

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

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        
        # --- UI SELECTORS ---
        c1, c2 = st.columns(2)
        with c1:
            all_dates = df['DATE'].unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Select Date:", options=all_dates)
        with c2:
            target_s = st.selectbox("🎰 Select Shift:", options=[c for c in game_cols if c in df.columns])

        idx = df[df['DATE'] == sel_date].index[0]
        p_a, p_b = get_ab_prediction(df, idx, target_s)
        
        # Asli Result Selection
        actual_val = df.iloc[idx][target_s]
        try:
            act_num = int(pd.to_numeric(actual_val, errors='coerce'))
            act_a, act_b = act_num // 10, act_num % 10
        except:
            act_num, act_a, act_b = None, None, None

        # --- LIVE RESULT DISPLAY (TOP) ---
        st.divider()
        st.markdown(f"### 📊 Live Result for {target_s} ({sel_date}): **{actual_val if actual_val != 0 else 'Waiting...'}**")
        
        # --- POSITION-WISE COLOR BOXES ---
        res_a, res_b, res_jodi = "red-box", "red-box", "red-box"
        if act_a is not None:
            if p_a == act_a or (p_a+5)%10 == act_a: res_a = "green-box"
            if p_b == act_b or (p_b+5)%10 == act_b: res_b = "green-box"
            if res_a == "green-box" and res_b == "green-box": res_jodi = "green-box"

        col_a, col_b, col_j = st.columns(3)
        with col_a:
            st.markdown(f"**Andar (A) Prediction: {p_a}**")
            st.markdown(f'<div class="{res_a} big-font">{p_a if res_a == "green-box" else p_a}</div>', unsafe_allow_html=True)
        with col_b:
            st.markdown(f"**Bahar (B) Prediction: {p_b}**")
            st.markdown(f'<div class="{res_b} big-font">{p_b if res_b == "green-box" else p_b}</div>', unsafe_allow_html=True)
        with col_j:
            st.markdown(f"**Direct Jodi: {p_a}{p_b}**")
            st.markdown(f'<div class="{res_jodi} big-font">{p_a}{p_b}</div>', unsafe_allow_html=True)

        # --- DETAILED HISTORY TABLE ---
        st.divider()
        st.subheader("📜 11-Day Performance History (A/B Wise)")
        
        history_list = []
        for i in range(idx - 11, idx + 1):
            if i < 0: continue
            ha, hb = get_ab_prediction(df, i, target_s)
            h_act = df.iloc[i][target_s]
            
            # Check Status
            try:
                h_val = int(pd.to_numeric(h_act, errors='coerce'))
                h_a, h_b = h_val // 10, h_val % 10
                a_pass = "✅" if ha == h_a or (ha+5)%10 == h_a else "❌"
                b_pass = "✅" if hb == h_b or (hb+5)%10 == h_b else "❌"
                j_pass = "💎 BLAST" if a_pass == "✅" and b_pass == "✅" else "❌"
            except: a_pass, b_pass, j_pass = "➖", "➖", "➖"

            history_list.append({
                "Date": df.iloc[i]['DATE'],
                "Actual Result": h_act,
                "Andar (A)": f"{ha} {a_pass}",
                "Bahar (B)": f"{hb} {b_pass}",
                "Jodi Status": j_pass
            })
        
        st.table(pd.DataFrame(history_list))
        
