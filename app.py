import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v13.5 - Final Stable", layout="wide")

st.title("🎯 MAYA Super-AI v13.5 (Accuracy Locked)")

# Jodi Generator
def get_jodis(ank):
    rashi = (ank + 5) % 10
    return [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}"]

@st.cache_data
def load_and_clean(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        df['DT_OBJ'] = pd.to_datetime(df['DATE'], errors='coerce')
        return df
    except Exception as e:
        return None

# Accuracy Engine (STRICTLY UNCHANGED)
def calculate_prediction(df, data_idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[data_idx]
    history_df = df.iloc[:data_idx + 1]
    scores = {i: 0 for i in range(10)}
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Error Fix: String values (XX) ko handle karne ke liye
    try:
        raw_val = row.get(base_col, 0)
        base_val = int(pd.to_numeric(raw_val, errors='coerce') if raw_val != 'XX' else 0)
    except:
        base_val = 0
        
    d1, d2 = int(base_val) // 10, int(base_val) % 10
    
    # Core Accuracy Logic (Locked)
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
        if pd.isna(actual) or actual == 'XX' or actual == '': return "➖"
        p_rashi = (pred + 5) % 10
        a_str = str(int(pd.to_numeric(actual, errors='coerce'))).zfill(2)
        if str(pred) in a_str or str(p_rashi) in a_str:
            return "✅ PASS"
        return "❌ FAIL"
    except: return "❌ FAIL"

uploaded_file = st.file_uploader("📂 Apni File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_clean(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        available_shifts = [c for c in game_cols if c in df.columns]
        
        st.sidebar.header("⚙️ Selection")
        all_dates = df['DATE'].unique().tolist()[::-1]
        sel_date = st.sidebar.selectbox("📅 Tarikh Chunein:", options=all_dates)
        target_s = st.sidebar.selectbox("🎰 Shift Chunein:", options=available_shifts)

        idx = df[df['DATE'] == sel_date].index[0]
        sel_dt_obj = df.iloc[idx]['DT_OBJ']

        # --- SECTION 1: SAME DATE HISTORY ---
        st.subheader(f"📅 Multi-Month History: Har Mahine Ki {sel_dt_obj.day} Tarikh")
        same_date_data = []
        for m in range(1, 13):
            try:
                past_dt = sel_dt_obj - pd.DateOffset(months=m)
                match = df[df['DT_OBJ'].dt.date == past_dt.date()]
                if not match.empty:
                    m_idx = match.index[0]
                    m_pred = calculate_prediction(df, m_idx, target_s)
                    m_actual = df.iloc[m_idx][target_s]
                    same_date_data.append({
                        "Month Date": df.iloc[m_idx]['DATE'],
                        "Result": m_actual,
                        "AI Prediction": f"{m_pred}/{(m_pred+5)%10}",
                        "Status": is_it_hit(m_pred, m_actual)
                    })
            except: continue
        st.table(pd.DataFrame(same_date_data))

        # --- SECTION 2: LAST 11 DAYS HISTORY ---
        st.subheader("📜 Pichle 11 Dinon Ka Continuous Record")
        last_11_data = []
        for i in range(idx - 11, idx + 1):
            if i < 0: continue
            p_date = df.iloc[i]['DATE']
            p_actual = df.iloc[i][target_s]
            p_pred = calculate_prediction(df, i, target_s)
            last_11_data.append({
                "Date": p_date,
                "Actual Result": p_actual,
                "AI Prediction": f"{p_pred}/{(p_pred+5)%10}",
                "Status": is_it_hit(p_pred, p_actual)
            })
        st.table(pd.DataFrame(last_11_data))

        # --- SECTION 3: CURRENT PREDICTION ---
        st.divider()
        top_ank = calculate_prediction(df, idx, target_s)
        jodis = get_jodis(top_ank)
        st.header(f"🔮 Today's Target ({target_s}): {sel_date}")
        n1, n2, n3 = st.columns(3)
        with n1: st.success(f"### Single\n{jodis[0]}")
        with n2: st.info(f"### Solid\n{jodis[1]}")
        with n3: st.warning(f"### Support\n{jodis[2]}, {jodis[3]}")
        
