import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v27.0 - Deep Scan Edition", layout="wide")

def calculate_deep_scan_logic(df, idx, shift):
    # Sirf usi shift ka pura pichla data uthana
    shift_history = df[shift].iloc[:idx+1].replace('XX', 0).fillna(0).astype(float).astype(int)
    
    # 1. Position Analysis (Last 20 Days)
    # Dekhna ki Andar zyada pass ho raha hai ya Bahar
    recent_20 = shift_history.tail(20)
    
    # Base Value (Last Result of same shift)
    base_val = shift_history.iloc[-1] if not shift_history.empty else 0
    d1, d2 = base_val // 10, base_val % 10
    
    scores_a = {i: 0 for i in range(10)}
    scores_b = {i: 0 for i in range(10)}
    
    # --- DEEP PATTERN RULES ---
    # Rule A: Movement Pattern (Agar 1 chhota 1 bada chal raha ho)
    for i in range(1, len(recent_20)):
        diff = abs(recent_20.iloc[i] - recent_20.iloc[i-1])
        if diff < 10: # Narrow range movement
            scores_a[d1] += 10
            scores_b[d2] += 10
            
    # Rule B: Mirror/Rashi Sync
    r_d1, r_d2 = (d1+5)%10, (d2+5)%10
    scores_a[r_d1] += 15
    scores_b[r_d2] += 15
    
    # Rule C: Gap Analysis (Single Shift Specific)
    pool = "".join([str(x).zfill(2) for x in recent_20.tail(10)])
    for i in range(10):
        if str(i) not in pool:
            scores_a[i] += 20
            scores_b[i] += 20

    best_a = max(scores_a, key=scores_a.get)
    best_b = max(scores_b, key=scores_b.get)
    
    return best_a, best_b

# --- UI DISPLAY (AS PER YOUR DESIGN) ---
st.title("🎯 MAYA v27.0 (Deep Scan & Resampling)")

uploaded_file = st.file_uploader("📂 Upload Excel", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date:", df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", ['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    p_a, p_b = calculate_deep_scan_logic(df, idx, target_s)
    
    # Display Logic
    st.divider()
    st.markdown(f"### [ {p_a} ] + [ {p_b} ] = Jodi: **{p_a}{p_b}**")
    
    # Comparison and 10-day history
    st.subheader("📜 Efficiency Check (Last 10 Months/Days Analysis)")
    # (Yahan history table wahi ✅/❌ ticks ke saath aayegi)
    
