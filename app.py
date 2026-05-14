import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v15.0 - AB Position Logic", layout="wide")

st.title("🎯 MAYA Super-AI v15.0 (Andar-Bahar Direct Number)")

@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'}
        df = df.rename(columns=mapping)
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        return df
    except Exception as e:
        return None

# --- NEW LOGIC: POSITION BASED PREDICTION ---
def calculate_ab_prediction(df, data_idx, shift):
    row = df.iloc[data_idx]
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    base_val = int(pd.to_numeric(row.get(base_col, 0), errors='coerce') or 0)
    
    # Split Base into A and B (Andar and Bahar)
    a_base = base_val // 10
    b_base = base_val % 10
    
    # 1. Prediction for Andar (A)
    # Pattern: Agar Joda hai toh 0/5, warna Base A ka mirror
    a_scores = {i: 0 for i in range(10)}
    if a_base == b_base:
        a_scores[0] += 20; a_scores[5] += 20
    else:
        a_scores[a_base] += 15; a_scores[(a_base + 5) % 10] += 10
        
    # 2. Prediction for Bahar (B)
    # Pattern: Gap analysis specific to Bahar position
    b_scores = {i: 0 for i in range(10)}
    b_scores[b_base] += 15; b_scores[(b_base + 5) % 10] += 10
    
    # Gap Analysis for Confluence (Last 10 Days)
    recent_pool = df.iloc[:data_idx + 1].tail(10)[shift].astype(str).values
    for i in range(10):
        if str(i) not in "".join(recent_pool):
            a_scores[i] += 5; b_scores[i] += 10 # Bahar ka gap zyada matter karta hai

    best_a = max(a_scores, key=a_scores.get)
    best_b = max(b_scores, key=b_scores.get)
    
    return best_a, best_b

def check_jodi_hit(a_pred, b_pred, actual):
    actual_val = int(pd.to_numeric(actual, errors='coerce') or 0)
    act_a = actual_val // 10
    act_b = actual_val % 10
    
    # Check if both match or mirrors match (Strict Pass)
    if (a_pred == act_a or (a_pred+5)%10 == act_a) and (b_pred == act_b or (b_pred+5)%10 == act_b):
        return "✅ PASS"
    return "❌ FAIL"

uploaded_file = st.file_uploader("📂 Apni Excel File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        st.sidebar.header("⚙️ Settings")
        all_dates = df['DATE'].unique().tolist()[::-1]
        sel_date = st.sidebar.selectbox("📅 Tarikh Chunein:", options=all_dates)
        target_s = st.sidebar.selectbox("🎰 Shift Chunein:", options=[c for c in game_cols if c in df.columns])

        idx = df[df['DATE'] == sel_date].index[0]
        a_pred, b_pred = calculate_ab_prediction(df, idx, target_s)
        
        # --- OUTPUT ---
        st.subheader(f"🔮 {target_s} Ki Prediction ({sel_date})")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"### Andar (A): {a_pred}")
            st.info(f"### Bahar (B): {b_pred}")
        with c2:
            st.success(f"### Single Number: {a_pred}{b_pred}")
            st.warning(f"### Support Number: {(a_pred+5)%10}{(b_pred+5)%10}")

        # --- HISTORY TRACKER ---
        st.markdown("### 📜 Position-Based History (10 Days)")
        history_list = []
        for i in range(idx - 10, idx):
            if i < 0: continue
            ha, hb = calculate_ab_prediction(df, i, target_s)
            h_actual = df.iloc[i][target_s]
            status = check_jodi_hit(ha, hb, h_actual)
            history_list.append({"Date": df.iloc[i]['DATE'], "Actual": h_actual, "Predicted": f"{ha}{hb}", "Status": status})
        
        st.table(pd.DataFrame(history_list))
                     
