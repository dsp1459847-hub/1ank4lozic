import streamlit as st
import pandas as pd

# Page Setup - Dashboard ko hamesha wide rakhega
st.set_page_config(page_title="MAYA v17.0 - Final Fix", layout="wide")

st.title("🎯 MAYA Super-AI v17.0 (Strict Logic & Fixed UI)")

# --- ERROR-PROOF DATA LOADER ---
@st.cache_data
def load_and_clean_data(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # Column names ki safai
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'}
        df = df.rename(columns=mapping)
        
        # Sirf data wali rows rakhna
        df = df.dropna(subset=['DATE'])
        df['DATE'] = df['DATE'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"File Load Error: {e}")
        return None

# --- ACCURACY ENGINE: POSITION LOGIC (NO CHANGE) ---
def get_prediction(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    row = df.iloc[idx]
    
    # Base Selection
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    try:
        val_raw = row.get(base_col, 0)
        base_val = int(pd.to_numeric(val_raw, errors='coerce')) if pd.notna(val_raw) and str(val_raw).upper() != 'XX' else 0
    except:
        base_val = 0
    
    a_base = int(base_val // 10)
    b_base = int(base_val % 10)
    
    # Position Logic Scores
    a_scores = {i: 0 for i in range(10)}
    b_scores = {i: 0 for i in range(10)}
    
    if a_base == b_base and base_val > 0:
        a_scores[0] += 20; a_scores[5] += 20
    else:
        a_scores[a_base] += 15; a_scores[(a_base + 5) % 10] += 10
        
    b_scores[b_base] += 15; b_scores[(b_base + 5) % 10] += 10
    
    # 10-Day Gap Analysis
    recent = df.iloc[:idx + 1].tail(10)[game_cols].values.flatten()
    pool = "".join([str(i) for i in recent if str(i).isdigit()])
    
    for i in range(10):
        if str(i) not in pool:
            a_scores[i] += 12; b_scores[i] += 18
            
    return max(a_scores, key=a_scores.get), max(b_scores, key=b_scores.get)

# --- UI INTERFACE ---
uploaded_file = st.file_uploader("📂 Apni Excel File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_clean_data(uploaded_file)
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        available_shifts = [c for c in game_cols if c in df.columns]
        
        # Tarikh aur Shift Selectors - Main Screen par sabse upar
        st.markdown("### ⚙️ Control Panel")
        c1, c2 = st.columns(2)
        
        with c1:
            all_dates = df['DATE'].unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Tarikh Select Karein:", options=all_dates, key="date_box")
        
        with c2:
            target_s = st.selectbox("🎰 Shift Select Karein:", options=available_shifts, key="shift_box")

        # Result Calculation
        try:
            idx = df[df['DATE'] == sel_date].index[0]
            best_a, best_b = get_prediction(df, idx, target_s)
            
            # --- MAIN DISPLAY ---
            st.divider()
            st.subheader(f"🔮 {target_s} Target for {sel_date}")
            
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.info(f"### Andar (A): {best_a}")
                st.info(f"### Bahar (B): {best_b}")
            with res_c2:
                st.success(f"### Single Number: {best_a}{best_b}")
                st.warning(f"### Support: {(best_a+5)%10}{(best_b+5)%10}")

            # --- PERFORMANCE TRACKER ---
            st.markdown("### 📜 10-Day Position History")
            history = []
            for i in range(idx - 10, idx + 1):
                if i < 0: continue
                ha, hb = get_prediction(df, i, target_s)
                h_act = df.iloc[i][target_s]
                # Hit Check
                try:
                    act_val = int(pd.to_numeric(h_act, errors='coerce'))
                    h_status = "✅ PASS" if (ha == act_val//10 or (ha+5)%10 == act_val//10) and (hb == act_val%10 or (hb+5)%10 == act_val%10) else "❌ FAIL"
                except: h_status = "➖"
                
                history.append({"Date": df.iloc[i]['DATE'], "Actual": h_act, "AI Pred": f"{ha}{hb}", "Status": h_status})
            
            st.table(pd.DataFrame(history))

        except Exception as e:
            st.error(f"Calculation Error: {e}")
            
