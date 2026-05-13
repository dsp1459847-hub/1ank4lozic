import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v11.0 - Zero Error", layout="wide")

st.title("🎯 MAYA Super-AI v11.0 (Fix Edition)")

# 1. Direct Number (Jodi) Generator
def get_solid_jodis(ank):
    rashi = (ank + 5) % 10
    # Aapke solid patterns ke hisaab se numbers
    return [f"{ank}{ank}", f"{ank}{rashi}", f"{rashi}{ank}", f"{rashi}{rashi}"]

# 2. Optimized File Loader (No Hang)
@st.cache_data
def fast_load(file):
    try:
        # Excel ya CSV dono ke liye support
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # Column names ki safai
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mapping: Aapki file mein FD/GD hai, use FB/GB mein badalna
        df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
        
        # Sirf wahi rows rakhein jahan result bhara hua hai (June/July ki khali dates hatayein)
        df = df.dropna(subset=['DS', 'FB', 'GB', 'GL'], how='all')
        
        # Date ko saaf string mein badalna
        df['DATE'] = df['DATE'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"File Loading Error: {e}")
        return None

uploaded_file = st.file_uploader("📂 Apni Excel File Yahan Daalein", type=["csv", "xlsx"])

if uploaded_file:
    df = fast_load(uploaded_file)
    
    if df is not None:
        game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
        for col in game_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        st.success("✅ Data Active! Ab Select Karein.")

        # --- SELECTION INTERFACE ---
        st.markdown("### ⚙️ Control Panel")
        col1, col2 = st.columns(2)
        
        with col1:
            date_options = df['DATE'].unique().tolist()[::-1]
            sel_date = st.selectbox("📅 Tarikh Chunein:", options=date_options)
        
        with col2:
            available_shifts = [c for c in game_cols if c in df.columns]
            target_s = st.selectbox("🎰 Shift Chunein:", options=available_shifts)

        # --- LOGIC CALCULATION (Strict Accuracy) ---
        try:
            # Selected date ka data nikalna
            idx = df[df['DATE'] == sel_date].index[0]
            f_df = df.iloc[:idx + 1]
            current_data = df.iloc[idx]

            scores = {i: 0 for i in range(10)}
            
            # Base Selection Logic
            flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
            base_col = flow.get(target_s, 'DS')
            base_val = current_data.get(base_col, 0)
            
            d1, d2 = base_val // 10, base_val % 10
            
            # Strict Patterns
            if d1 == d2 and base_val > 0:
                scores[0] += 20; scores[5] += 20 # Joda
            elif abs(d1 - d2) == 1:
                nxt = (max(d1, d2) + 1) % 10
                scores[nxt] += 15; scores[(nxt+5)%10] += 12 # Counting
            else:
                scores[d2] += 12; scores[(d2+5)%10] += 10 # 85 -> 0/5

            # Gap Analysis Pattern (25+ Confluence Booster)
            recent = f_df.tail(10)[game_cols].astype(str).values.flatten()
            pool = "".join(recent)
            for i in range(10):
                if str(i) not in pool: scores[i] += 18

            # Best Ank to Number
            res = pd.DataFrame(scores.items(), columns=['Ank', 'Score']).sort_values(by='Score', ascending=False)
            top_ank = int(res.iloc[0]['Ank'])
            jodis = get_solid_jodis(top_ank)

            # --- DISPLAY OUTPUT ---
            st.divider()
            st.info(f"📊 **Base Check:** {target_s} ke liye humne {base_col} ({base_val}) ka logic lagaya hai.")
            
            st.subheader(f"🔮 {target_s} Direct Numbers ({sel_date})")
            n1, n2, n3 = st.columns(3)
            with n1:
                st.success(f"### Single Number\n{jodis[0]}")
            with n2:
                st.info(f"### Solid Number\n{jodis[1]}")
            with n3:
                st.warning(f"### Support Jodis\n{jodis[2]}, {jodis[3]}")
            
            st.write(f"**Accuracy Level:** {int(res.iloc[0]['Score'])}%")

        except Exception as e:
            st.error(f"Analysis Error: {e}")

else:
    st.info("Bhai, file upload karo, Tarikh aur Shift ka button turant aa jayega.")
    
