import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v12.0 - History & Prediction", layout="wide")

st.title("🎯 MAYA Super-AI v12.0 (History Match Edition)")

# Function to get Jodis and check results
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
        return df
    except Exception as e:
        st.error(f"File Error: {e}")
        return None

uploaded_file = st.file_uploader("📂 Apni Excel File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_clean(uploaded_file)
    
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        for col in game_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # --- SELECTION PANEL ---
        st.markdown("### ⚙️ Control Panel")
        c1, c2 = st.columns(2)
        with c1:
            all_dates = df['DATE'].unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Tarikh Select Karein:", options=all_dates)
        with c2:
            available_shifts = [c for c in game_cols if c in df.columns]
            target_s = st.selectbox("🎰 Shift Select Karein:", options=available_shifts)

        # --- CALCULATION LOGIC ---
        try:
            idx = df[df['DATE'] == sel_date].index[0]
            f_df = df.iloc[:idx + 1]
            current_data = df.iloc[idx]

            # Logic Engine
            def calculate_for_date(data_idx, shift):
                row = df.iloc[data_idx]
                history_df = df.iloc[:data_idx + 1]
                scores = {i: 0 for i in range(10)}
                flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
                base_col = flow.get(shift, 'DS')
                base_val = row.get(base_col, 0)
                d1, d2 = base_val // 10, base_val % 10
                
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

            # Current Prediction
            top_ank = calculate_for_date(idx, target_s)
            jodis = get_jodis(top_ank)

            # --- HISTORY COMPARISON (Aapki Main Demand) ---
            st.markdown("### 📜 Past 5 Days: Prediction vs Actual Result")
            history_list = []
            for i in range(idx - 5, idx):
                if i < 0: continue
                past_date = df.iloc[i]['DATE']
                actual_res = df.iloc[i][target_s]
                pred_ank = calculate_for_date(i, target_s)
                
                # Check if hit (If actual result's digit matches prediction)
                is_hit = "✅ HIT" if str(pred_ank) in str(actual_res) or str((pred_ank+5)%10) in str(actual_res) else "❌ MISS"
                history_list.append({"Date": past_date, "Actual Result": actual_res, "AI Predicted Ank": f"{pred_ank}/{ (pred_ank+5)%10 }", "Status": is_hit})
            
            st.table(pd.DataFrame(history_list))

            # --- CURRENT PREDICTION DISPLAY ---
            st.divider()
            st.subheader(f"🔮 {target_s} Prediction for {sel_date}")
            n1, n2 = st.columns(2)
            with n1:
                st.success(f"### Single Jodi\n# {jodis[0]}")
                st.info(f"### Solid Jodi\n# {jodis[1]}")
            with n2:
                st.warning(f"### Support Jodis\n{jodis[2]}, {jodis[3]}")
                st.write(f"**Based on {target_s}'s Base Result:** {current_data.get(target_s, 'XX')}")

        except Exception as e:
            st.error(f"Data Match Error: {e}")
else:
    st.info("Bhai, file upload karo, 5 din ki history aur aaj ki prediction turant dikhegi.")
    
