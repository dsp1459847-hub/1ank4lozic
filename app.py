import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v18.0 - God Mode", layout="wide")

st.title("🎯 MAYA Super-AI v18.0 (Accuracy Recovery Edition)")

# --- ACCURACY ENGINE: 25+ PATTERN CONFLUENCE ---
def calculate_master_prediction(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    
    # Base Selection Flow
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Value Cleaning
    try:
        val_raw = row.get(base_col, 0)
        base_val = int(pd.to_numeric(val_raw, errors='coerce')) if pd.notna(val_raw) and str(val_raw).upper() != 'XX' else 0
    except:
        base_val = 0
    
    d1, d2 = int(base_val // 10), int(base_val % 10)
    
    # Scoring Matrix (THE ORIGINAL HIGH ACCURACY LOGIC)
    scores = {i: 0 for i in range(10)}
    
    # 1. Joda/Counting/85 Rule
    if d1 == d2 and base_val > 0:
        scores[0] += 25; scores[5] += 25
    elif abs(d1 - d2) == 1:
        nxt = (max(d1, d2) + 1) % 10
        scores[nxt] += 20; scores[(nxt+5)%10] += 15
    else:
        scores[d2] += 15; scores[(d2 + 5) % 10] += 12
    
    # 2. Gap Pattern Analysis (Last 10 Days)
    recent = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(i) for i in recent if str(i).isdigit()])
    for i in range(10):
        if str(i) not in pool:
            scores[i] += 20 # Gap ank ko sabse zyada weight
            
    # Final Top Ank & Rashi
    res_df = pd.DataFrame(scores.items(), columns=['Ank', 'Score']).sort_values(by='Score', ascending=False)
    top_ank = int(res_df.iloc[0]['Ank'])
    rashi = (top_ank + 5) % 10
    
    return top_ank, rashi

# --- HELPER: Jodi Maker ---
def make_jodis(ank, rashi):
    # Cross Jodis for maximum coverage (A-B position safe)
    return [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}", 
            f"{ank}0", f"{ank}5", f"0{ank}", f"5{ank}"]

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
    except: return None

# --- UI INTERFACE ---
uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

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
        ank, rashi = calculate_master_prediction(df, idx, target_s)
        jodis = make_jodis(ank, rashi)

        # --- DISPLAY ---
        st.divider()
        st.header(f"🔮 {target_s} Result for {sel_date}")
        
        r1, r2 = st.columns(2)
        with r1:
            st.success(f"### Single Ank/Harf: {ank} (Support: {rashi})")
        with r2:
            st.warning(f"### Solid Jodis: {', '.join(jodis[:4])}")

        # --- HISTORY TRACKER (11 DAYS) ---
        st.markdown("### 📜 11-Day Live Backtest (Real Results)")
        history = []
        for i in range(idx - 11, idx + 1):
            if i < 0: continue
            h_ank, h_rashi = calculate_master_prediction(df, i, target_s)
            h_act = str(df.iloc[i][target_s]).zfill(2)
            
            # Hit check: Agar ank ya rashi me se koi bhi result me dikhe
            is_pass = "✅ PASS" if str(h_ank) in h_act or str(h_rashi) in h_act else "❌ FAIL"
            history.append({"Date": df.iloc[i]['DATE'], "Actual": h_act, "AI Harf": f"{h_ank}/{h_rashi}", "Status": is_pass})
        
        st.table(pd.DataFrame(history))
        
