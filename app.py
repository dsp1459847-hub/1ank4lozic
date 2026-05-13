import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(page_title="MAYA v13.0 - Multi-Month Tracker", layout="wide")

st.title("🎯 MAYA Super-AI v13.0 (History & Same-Date Tracker)")

# Jodi Generator
def get_jodis(ank):
    rashi = (ank + 5) % 10
    return [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}"]

@st.cache_data
def load_and_clean(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        # Date column ko actual datetime mein convert karna calculations ke liye
        df['DT_OBJ'] = pd.to_datetime(df['DATE'], errors='coerce')
        return df
    except Exception as e:
        return None

# Accuracy Engine (DO NOT CHANGE)
def calculate_prediction(df, data_idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[data_idx]
    history_df = df.iloc[:data_idx + 1]
    scores = {i: 0 for i in range(10)}
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    base_val = row.get(base_col, 0)
    d1, d2 = int(base_val) // 10, int(base_val) % 10
    
    if d1 == d2 and base_val > 0: scores[0] += 20; scores[5] += 20
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores[nxt] += 15; scores[(nxt+5)%10] += 12
    else: scores[d2] += 12; scores[(d2+5)%10] += 10
    
    recent = history_df.tail(10)[game_cols].astype(str).values.flatten()
    pool = "".join(recent)
    for i in range(10):
        if str(i) not in pool: scores[i] += 18
    
    res_ank = int(pd.DataFrame(scores.items()).sort_values(by=1, ascending=False).iloc[0][0])
    return res_ank

def is_it_hit(pred, actual):
    try:
        p_rashi = (pred + 5) % 10
        a_str = str(int(actual)).zfill(2)
        if str(pred) in a_str or str(p_rashi) in a_str:
            return "✅ PASS"
        return "❌ FAIL"
    except: return "❌ FAIL"

uploaded_file = st.file_uploader("📂 Apni File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_clean(uploaded_file)
    
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        # --- SELECTION ---
        all_dates = df['DATE'].unique().tolist()[::-1]
        sel_date = st.sidebar.selectbox("📅 Tarikh Chunein:", options=all_dates)
        target_s = st.sidebar.selectbox("🎰 Shift Chunein:", options=[c for c in game_cols if c in df.columns])

        idx = df[df['DATE'] == sel_date].index[0]
        sel_dt_obj = df.iloc[idx]['DT_OBJ']

        # --- SECTION 1: SAME DATE HISTORY (Pichle Mahino Ka Record) ---
        st.subheader(f"📅 Multi-Month History: Har Mahine Ki {sel_dt_obj.day} Tarikh")
        same_date_data = []
        # Pichle 11 mahino ka wahi din check karna
        for m in range(1, 12):
            past_dt = sel_dt_obj - pd.DateOffset(months=m)
            # Find the closest match in data
            match = df[df['DT_OBJ'].dt.date == past_dt.date()]
            if not match.empty:
                m_idx = match.index[0]
                m_pred = calculate_prediction(df, m_idx, target_s)
                m_actual = df.iloc[m_idx][target_s]
                m_status = is_it_hit(m_pred, m_actual)
                same_date_data.append({
                    "Month Date": df.iloc[m_idx]['DATE'],
                    "Result": m_actual,
                    "AI Prediction": f"{m_pred}/{(m_pred+5)%10}",
                    "Status": m_status
                })
        st.table(pd.DataFrame(same_date_data))

        # --- SECTION 2: LAST 10 DAYS CONTINUOUS HISTORY ---
        st.subheader("📜 Pichle 10 Dinon Ka Lagatar Record")
        last_10_data = []
        for i in range(idx - 10, idx + 1):
            if i < 0: continue
            p_date = df.iloc[i]['DATE']
            p_actual = df.iloc[i][target_s]
            p_pred = calculate_prediction(df, i, target_s)
            p_status = is_it_hit(p_pred, p_actual)
            last_10_data.append({
                "Date": p_date,
                "Actual Result": p_actual,
                "AI Prediction": f"{p_pred}/{(p_pred+5)%10}",
                "Status": p_status
            })
        st.table(pd.DataFrame(last_10_data))

        # --- SECTION 3: CURRENT PREDICTION ---
        st.divider()
        top_ank = calculate_prediction(df, idx, target_s)
        jodis = get_jodis(top_ank)
        
        st.header(f"🔮 {target_s} Today's Target: {sel_date}")
        n1, n2, n3 = st.columns(3)
        with n1: st.success(f"### Single\n{jodis[0]}")
        with n2: st.info(f"### Solid\n{jodis[1]}")
        with n3: st.warning(f"### Support\n{jodis[2]}, {jodis[3]}")
    
