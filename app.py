import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v19.0 - Final Prediction", layout="wide")

st.title("🎯 MAYA Super-AI v19.0 (Full Prediction Mode)")

# --- CORE LOGIC: NO CHANGE IN ACCURACY ---
def get_prediction_engine(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    
    # Base Shift Flow
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    try:
        raw = row.get(base_col, 0)
        base_val = int(pd.to_numeric(raw, errors='coerce') or 0)
    except:
        base_val = 0
    
    d1, d2 = base_val // 10, base_val % 10
    scores = {i: 0 for i in range(10)}
    
    # Rule 1: Joda/Counting/Normal (Locked Accuracy)
    if d1 == d2 and base_val > 0:
        scores[0] += 25; scores[5] += 25
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores[nxt] += 20; scores[(nxt+5)%10] += 15
    else:
        scores[d2] += 15; scores[(d2+5)%10] += 12
        
    # Rule 2: 10-Day Gap Analysis
    recent = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(i) for i in recent if str(i).isdigit()])
    for i in range(10):
        if str(i) not in pool:
            scores[i] += 22
            
    res_df = pd.DataFrame(scores.items()).sort_values(by=1, ascending=False)
    top = int(res_df.iloc[0][0])
    return top, (top+5)%10

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

# --- UI INTERFACE ---
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        
        st.markdown("### ⚙️ Control Panel")
        c1, c2 = st.columns(2)
        with c1:
            all_dates = df['DATE'].unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Select Date:", options=all_dates)
        with c2:
            target_s = st.selectbox("🎰 Select Shift:", options=[c for c in game_cols if c in df.columns])

        idx = df[df['DATE'] == sel_date].index[0]
        ank, rashi = get_prediction_engine(df, idx, target_s)

        # --- SECTION 1: ASLI PREDICTION (TOP PAR) ---
        st.divider()
        st.header(f"🔮 Prediction for {target_s} ({sel_date})")
        
        p1, p2, p3 = st.columns(3)
        with p1:
            st.success(f"### Single Number\n# {ank}{ank}")
        with p2:
            st.info(f"### Solid Jodis\n{ank}{rashi}, {rashi}{ank}")
        with p3:
            st.warning(f"### Support\n{rashi}{rashi}, {ank}0, {ank}5")

        # --- SECTION 2: LIVE HISTORY WITH TICKS ---
        st.divider()
        st.subheader("📜 11-Day Live Result & Performance")
        
        history = []
        for i in range(idx - 11, idx + 1):
            if i < 0: continue
            h_ank, h_rashi = get_prediction_engine(df, i, target_s)
            h_act_val = df.iloc[i][target_s]
            h_act_str = str(h_act_val).zfill(2)
            
            # Hit check logic
            is_pass = "✅ PASS" if str(h_ank) in h_act_str or str(h_rashi) in h_act_str else "❌ FAIL"
            if h_act_val == "XX" or h_act_val == 0: is_pass = "➖"
            
            history.append({
                "Date": df.iloc[i]['DATE'],
                "Actual Result": h_act_val,
                "AI Prediction": f"{h_ank}/{h_rashi}",
                "Status": is_pass
            })
        
        st.table(pd.DataFrame(history))
        
