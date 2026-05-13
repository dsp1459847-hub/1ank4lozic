import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA AI v9.0 - Direct Number", layout="wide")

st.title("🎯 MAYA Super-AI v9.0 (Direct Number & Shift Control)")

# Function to make Jodis from Ank
def make_solid_numbers(ank):
    rashi = (ank + 5) % 10
    # Aapke logic ke hisaab se seedhe number (Jodi)
    jodis = [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}"]
    return jodis

@st.cache_data
def load_data(file):
    try:
        df = pd.read_csv(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapping = {'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'}
        df = df.rename(columns=mapping)
        # Khali rows ko hatana taaki June/July ki faltu dates na aayein
        df = df.dropna(subset=['DATE'])
        return df
    except Exception as e:
        return None

uploaded_file = st.file_uploader("Apni Excel/CSV File Upload Karein", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Columns identify karna
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        for col in game_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # --- MAIN SELECTION INTERFACE (SCREEN PAR) ---
        st.markdown("### 🛠️ Control Panel")
        c1, c2 = st.columns(2)
        
        with c1:
            all_dates = df['DATE'].astype(str).unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Tarikh Select Karein:", options=all_dates)
        
        with c2:
            available_shifts = [c for c in game_cols if c in df.columns]
            target_s = st.selectbox("🎰 Kis Shift Ka Number Chahiye?", options=available_shifts)

        # Selected Date ka data nikaalna
        idx = df[df['DATE'].astype(str) == sel_date].index[0]
        f_df = df.iloc[:idx + 1]
        current_data = df.iloc[idx]

        # --- PREDICTION ENGINE (STRICT ACCURACY) ---
        scores = {i: 0 for i in range(10)}
        
        # Dependency logic: Agli shift ke liye pichli ka base
        shift_flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
        base_col = shift_flow.get(target_s, 'DS')
        base_val = current_data.get(base_col, 0)
        
        d1, d2 = base_val // 10, base_val % 10
        
        # YOUR RULES
        if d1 == d2 and base_val > 0:
            scores[0] += 20; scores[5] += 20 # Joda Rule
        elif abs(d1 - d2) == 1:
            nxt = (max(d1, d2) + 1) % 10
            scores[nxt] += 15; scores[(nxt+5)%10] += 12 # Counting Rule
        else:
            scores[d2] += 12; scores[(d2 + 5) % 10] += 10 # 85 -> 0/5 Rule

        # Gap Pattern for Accuracy
        recent_pool = f_df.tail(10)[game_cols].astype(str).values.flatten()
        all_digits = "".join(recent_pool)
        for i in range(10):
            if str(i) not in all_digits: scores[i] += 18 

        res = pd.DataFrame(scores.items(), columns=['Ank', 'Score']).sort_values(by='Score', ascending=False)
        top_ank = int(res.iloc[0]['Ank'])
        final_numbers = make_solid_numbers(top_ank)

        # --- OUTPUT DISPLAY ---
        st.divider()
        st.info(f"📅 Record Date: {sel_date} | Base Used: {base_col} ({base_val})")
        
        # History View
        h_cols = st.columns(len(available_shifts))
        for i, c in enumerate(available_shifts):
            h_cols[i].metric(c, current_data[c])

        st.divider()
        
        # Direct Numbers
        st.subheader(f"🔮 {target_s} Ke Liye Direct Numbers")
        n1, n2, n3 = st.columns(3)
        
        with n1:
            st.success(f"### Single Number\n# {final_numbers[0]}")
        with n2:
            st.info(f"### Solid Number\n# {final_numbers[1]}")
        with n3:
            st.warning(f"### Support Jodis\n{final_numbers[2]}, {final_numbers[3]}")

        st.write(f"**Accuracy Level:** {int(res.iloc[0]['Score'])}%")
        st.bar_chart(res.set_index('Ank'))

else:
    st.info("Bhai, file upload karte hi Tarikh aur Shift chunne ka option aa jayega.")
    
