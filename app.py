import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v12.5 - Hit Tracker", layout="wide")

st.title("🎯 MAYA Super-AI v12.5 (Live Hit Tracker)")

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
        return df
    except Exception as e:
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

        # --- ACCURACY ENGINE (Unchanged & Strict) ---
        def calculate_prediction(data_idx, shift):
            row = df.iloc[data_idx]
            history_df = df.iloc[:data_idx + 1]
            scores = {i: 0 for i in range(10)}
            flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
            base_col = flow.get(shift, 'DS')
            base_val = row.get(base_col, 0)
            d1, d2 = base_val // 10, base_val % 10
            
            # Pattern Logic
            if d1 == d2 and base_val > 0: scores[0] += 20; scores[5] += 20
            elif abs(d1 - d2) == 1:
                nxt = (max(d1, d2) + 1) % 10
                scores[nxt] += 15; scores[(nxt+5)%10] += 12
            else: scores[d2] += 12; scores[(d2+5)%10] += 10
            
            # Gap Analysis
            recent = history_df.tail(10)[game_cols].astype(str).values.flatten()
            pool = "".join(recent)
            for i in range(10):
                if str(i) not in pool: scores[i] += 18
            
            res_ank = int(pd.DataFrame(scores.items()).sort_values(by=1, ascending=False).iloc[0][0])
            return res_ank

        try:
            idx = df[df['DATE'] == sel_date].index[0]
            top_ank = calculate_prediction(idx, target_s)
            jodis = get_jodis(top_ank)
            actual_res = df.iloc[idx][target_s]

            # Hit Check Logic
            def is_it_hit(pred, actual):
                p_rashi = (pred + 5) % 10
                a_str = str(int(actual)).zfill(2)
                if str(pred) in a_str or str(p_rashi) in a_str:
                    return "✅ PASS"
                return "❌ FAIL"

            # --- LIVE RESULT WITH TICK ---
            st.divider()
            status_now = is_it_hit(top_ank, actual_res)
            st.subheader(f"🔮 {target_s} Prediction vs Result: {status_now}")
            
            # --- HISTORY TRACKER (Past 10 Days) ---
            st.markdown("### 📜 10-Day Performance History")
            history_data = []
            pass_count = 0
            for i in range(idx - 10, idx):
                if i < 0: continue
                p_date = df.iloc[i]['DATE']
                p_actual = df.iloc[i][target_s]
                p_pred = calculate_prediction(i, target_s)
                p_status = is_it_hit(p_pred, p_actual)
                if "PASS" in p_status: pass_count += 1
                
                history_data.append({
                    "Date": p_date,
                    "Actual Result": p_actual,
                    "AI Prediction (Ank/Rashi)": f"{p_pred}/{ (p_pred+5)%10 }",
                    "Result Status": p_status
                })
            
            st.table(pd.DataFrame(history_data))
            st.write(f"📈 **10 dinon ki accuracy:** {pass_count * 10}%")

            # --- CURRENT JODIS ---
            st.divider()
            n1, n2 = st.columns(2)
            with n1:
                st.success(f"### Single Number\n# {jodis[0]}")
                st.info(f"### Solid Number\n# {jodis[1]}")
            with n2:
                st.warning(f"### Support Jodis\n{jodis[2]}, {jodis[3]}")

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Bhai, Excel upload karein. Sabhi ✅ Ticks aur History turant dikhegi.")
            
