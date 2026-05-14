import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v15.5 - AB Position Stable", layout="wide")

st.title("🎯 MAYA Super-AI v15.5 (Andar-Bahar Direct Number)")

# Optimized File Loader
@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'}
        df = df.rename(columns=mapping)
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        return df
    except Exception as e:
        return None

# --- ACCURACY ENGINE: POSITION BASED (STRICT) ---
def calculate_ab_prediction(df, data_idx, shift):
    row = df.iloc[data_idx]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # ERROR FIX: Handling XX, NaN, and Empty values strictly
    try:
        val_raw = row.get(base_col, 0)
        # Agar value XX hai ya khali hai toh 0 maanein
        base_val = int(pd.to_numeric(val_raw, errors='coerce')) if pd.notna(val_raw) and str(val_raw).upper() != 'XX' else 0
    except:
        base_val = 0
    
    # Split into Andar (A) and Bahar (B)
    a_base = int(base_val // 10)
    b_base = int(base_val % 10)
    
    # 1. Andar (A) Logic - (Accuracy Locked)
    a_scores = {i: 0 for i in range(10)}
    if a_base == b_base and base_val > 0:
        a_scores[0] += 20; a_scores[5] += 20
    else:
        a_scores[a_base] += 15; a_scores[(a_base + 5) % 10] += 10
        
    # 2. Bahar (B) Logic - (Accuracy Locked)
    b_scores = {i: 0 for i in range(10)}
    b_scores[b_base] += 15; b_scores[(b_base + 5) % 10] += 10
    
    # 3. Confluence (10-Day Position Gap)
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    recent_data = df.iloc[:data_idx + 1].tail(10)[game_cols].astype(str).values.flatten()
    pool = "".join([s for s in recent_data if s.isdigit()])
    for i in range(10):
        if str(i) not in pool:
            a_scores[i] += 12; b_scores[i] += 18 # Bahar gap has more weight

    best_a = max(a_scores, key=a_scores.get)
    best_b = max(b_scores, key=b_scores.get)
    
    return best_a, best_b

def check_jodi_hit(a_pred, b_pred, actual):
    try:
        if pd.isna(actual) or str(actual).upper() == 'XX': return "➖"
        act_val = int(pd.to_numeric(actual, errors='coerce'))
        act_a, act_b = act_val // 10, act_val % 10
        # Position wise check (with Mirror/Rashi)
        if (a_pred == act_a or (a_pred+5)%10 == act_a) and (b_pred == act_b or (b_pred+5)%10 == act_b):
            return "✅ PASS"
        return "❌ FAIL"
    except: return "❌ FAIL"

uploaded_file = st.file_uploader("📂 Apni Excel File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        st.sidebar.header("⚙️ Settings")
        all_dates = df['DATE'].unique().tolist()[::-1]
        sel_date = st.sidebar.selectbox("📅 Tarikh Select Karein:", options=all_dates)
        target_s = st.sidebar.selectbox("🎰 Shift Select Karein:", options=[c for c in game_cols if c in df.columns])

        idx = df[df['DATE'] == sel_date].index[0]
        
        # Calculation
        a_pred, b_pred = calculate_ab_prediction(df, idx, target_s)
        
        # --- OUTPUT DISPLAY ---
        st.subheader(f"🔮 {target_s} Target for {sel_date}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"### Andar (A): {a_pred}")
            st.info(f"### Bahar (B): {b_pred}")
        with c2:
            st.success(f"### Single Number\n# {a_pred}{b_pred}")
            st.warning(f"### Support Number\n# {(a_pred+5)%10}{(b_pred+5)%10}")

        # --- HISTORY TRACKER ---
        st.markdown("### 📜 10-Day Performance (Position Wise)")
        history_list = []
        for i in range(idx - 10, idx + 1):
            if i < 0: continue
            ha, hb = calculate_ab_prediction(df, i, target_s)
            h_actual = df.iloc[i][target_s]
            history_list.append({
                "Date": df.iloc[i]['DATE'],
                "Actual": h_actual,
                "AI Prediction (A/B)": f"{ha}{hb}",
                "Status": check_jodi_hit(ha, hb, h_actual)
            })
        
        st.table(pd.DataFrame(history_list))
            
