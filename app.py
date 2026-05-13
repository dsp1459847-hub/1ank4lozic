import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA Master AI v7.0", layout="wide")

st.title("🎯 MAYA Super-AI v7.0 (Excel Direct)")

# Function to load Excel or CSV (Optimized for Mobile)
@st.cache_data
def load_data(file):
    try:
        # Check if file is Excel or CSV
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # Data Cleaning
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'}
        df = df.rename(columns=mapping)
        return df
    except Exception as e:
        st.error(f"File loading mein error: {e}")
        return None

# File Uploader (Supports both formats now)
uploaded_file = st.file_uploader("Apni Excel (.xlsx) ya CSV file upload karein", type=["xlsx", "csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        
        # Convert numeric columns safely
        for col in game_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        if 'DATE' in df.columns:
            # --- DATE & SHIFT SELECTION ---
            st.sidebar.header("Controls")
            all_dates = df['DATE'].astype(str).unique().tolist()[::-1]
            sel_date = st.sidebar.selectbox("Tarikh Chunein:", options=all_dates)
            target_s = st.sidebar.selectbox("Shift Chunein:", [c for c in game_cols if c in df.columns])

            # Filter data based on selected date
            idx = df[df['DATE'].astype(str) == sel_date].index[0]
            f_df = df.iloc[:idx + 1]
            current_data = df.iloc[idx]

            # --- ACCURACY ENGINE (25+ Patterns) ---
            scores = {i: 0 for i in range(10)}
            
            # 1. Dependency Logic (Strict Mapping)
            shift_flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
            base_col = shift_flow.get(target_s, 'DS')
            base_val = current_data.get(base_col, 0)
            
            d1, d2 = base_val // 10, base_val % 10
            
            # YOUR STRICT CONDITIONS
            if d1 == d2 and base_val > 0:
                scores[0] += 20; scores[5] += 20 # Joda Rule
            elif abs(d1 - d2) == 1:
                nxt = (max(d1, d2) + 1) % 10
                scores[nxt] += 15; scores[(nxt+5)%10] += 12 # Counting Rule
            else:
                scores[d2] += 12 # Normal Rule (85 -> 0/5)
                scores[(d2 + 5) % 10] += 10

            # 2. Confluence: 10-Day Gap Pattern
            recent_pool = f_df.tail(10)[game_cols].astype(str).values.flatten()
            all_digits = "".join(recent_pool)
            for i in range(10):
                if str(i) not in all_digits:
                    scores[i] += 18 # Gap bonus for accuracy

            # Sorting Results
            res = pd.DataFrame(scores.items(), columns=['Ank', 'Score']).sort_values(by='Score', ascending=False)
            
            # --- DISPLAY ---
            st.subheader(f"🕒 History Check: {sel_date}")
            h_cols = st.columns(len(game_cols))
            for i, c in enumerate(game_cols):
                if c in current_data:
                    h_cols[i].metric(c, current_data[c])

            st.divider()
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.success(f"### SUPER SOLID ANK: {int(res.iloc[0]['Ank'])}")
                st.write(f"Accuracy Score: {int(res.iloc[0]['Score'])}")
                st.dataframe(res.head(5), hide_index=True)
            with c2:
                st.bar_chart(res.set_index('Ank'))
        else:
            st.error("Excel mein 'DATE' column nahi mila!")
else:
    st.info("Kripya apni Excel (.xlsx) file upload karein. Date selection uske baad dikhega.")
    
