import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA Super-AI v8.0", layout="wide")

st.title("🎯 MAYA Super-AI v8.0 (Direct Number Edition)")

# Function to generate Family Numbers (Jodi)
def get_family_numbers(ank):
    # Ank se bani top jodi aur rashi
    rashi = (ank + 5) % 10
    # Aapke logic ke hisaab se sabse solid numbers
    jodis = [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}"]
    return jodis

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
        # Khali rows hatana
        df = df.dropna(subset=['DS', 'FB', 'GB', 'GL'], how='all')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

uploaded_file = st.file_uploader("Apni Excel (.xlsx) ya CSV file upload karein", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        for col in game_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        if 'DATE' in df.columns:
            # --- DATE SELECTION OPTION ---
            st.sidebar.header("🎯 Settings")
            all_dates = df['DATE'].astype(str).unique().tolist()[::-1]
            sel_date = st.sidebar.selectbox("📅 Tarikh Select Karein:", options=all_dates)
            target_s = st.sidebar.selectbox("🎰 Shift Chunein:", [c for c in game_cols if c in df.columns])

            idx = df[df['DATE'].astype(str) == sel_date].index[0]
            f_df = df.iloc[:idx + 1]
            current_data = df.iloc[idx]

            # --- ACCURACY LOGIC ---
            scores = {i: 0 for i in range(10)}
            shift_flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
            base_col = shift_flow.get(target_s, 'DS')
            base_val = current_data.get(base_col, 0)
            d1, d2 = base_val // 10, base_val % 10
            
            # Logic implementation
            if d1 == d2 and base_val > 0:
                scores[0] += 20; scores[5] += 20
            elif abs(d1 - d2) == 1:
                nxt = (max(d1, d2) + 1) % 10
                scores[nxt] += 15; scores[(nxt+5)%10] += 12
            else:
                scores[d2] += 12; scores[(d2 + 5) % 10] += 10

            # Gap Pattern
            recent_pool = f_df.tail(10)[game_cols].astype(str).values.flatten()
            all_digits = "".join(recent_pool)
            for i in range(10):
                if str(i) not in all_digits: scores[i] += 18 

            res = pd.DataFrame(scores.items(), columns=['Ank', 'Score']).sort_values(by='Score', ascending=False)
            
            # --- RESULT DISPLAY ---
            st.markdown(f"### 🕒 History Record: {sel_date}")
            h_cols = st.columns(len(game_cols))
            for i, c in enumerate(game_cols):
                if c in current_data:
                    h_cols[i].metric(c, current_data[c])

            st.divider()
            
            # --- FINAL NUMBER PREDICTION ---
            top_ank = int(res.iloc[0]['Ank'])
            predicted_numbers = get_family_numbers(top_ank)
            
            st.subheader(f"🔮 {target_s} Direct Number Prediction")
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"### 🔥 SINGLE NUMBER: {predicted_numbers[0]}")
                st.info(f"Strong Support: {predicted_numbers[1]}")
            
            with col2:
                st.write("**Family Jodi (Solid Numbers):**")
                st.code(", ".join(predicted_numbers))
                st.write(f"Confidence Level: {int(res.iloc[0]['Score'])}%")

        else:
            st.error("Excel mein 'DATE' column nahi mila!")
else:
    st.info("Bhai, Excel upload karte hi 'Tarikh' chunne ka option Sidebar mein aa jayega.")
            
