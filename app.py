import streamlit as st
import pandas as pd

st.set_page_config(page_title="MAYA v45.0 - Real Target", layout="wide")

st.markdown("""
    <style>
    .target-box { background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
    .jodi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
    .jodi-item { background: #ffffff; color: #166534; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 20px; border: 1px solid #bbf7d0; }
    .eliminated-text { color: #dc2626; font-size: 14px; font-weight: bold; }
    .status-hit { color: #16a34a; font-weight: bold; }
    .status-fail { color: #dc2626; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v45.0 (The Real Target Engine)")

def get_logic_v45(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # 1. Base Numbers (Code 37 Logic)
    val = 0
    for i in range(1, 10):
        t_idx = idx - i
        if t_idx >= 0:
            raw = df.iloc[t_idx].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    # 2. Block List (40 Andar + 40 Bahar = 64 Unique Jodis)
    blocked_64 = set()
    for a in {pa, ra}:
        for i in range(10): blocked_64.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked_64.add(f"{i}{b}")
    
    # 3. Khelne wali 36 Jodiyan (Initial Target)
    target_36 = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked_64]
    
    # 4. Worst Gap Filtration (Level 2 & 3)
    # Hum pichle 3 din aur 5 din ke anko ko is 36 mein se bhi Minus karenge
    extra_hatao = set()
    for g in [3, 5]:
        if idx - g >= 0:
            v = str(df.iloc[idx-g].get(base_col, "XX")).split('.')[0]
            if v.isdigit():
                v_num = int(v)
                # Inke Andar/Bahar sets ko 36 mein se nikalenge
                for i in range(10): 
                    extra_hatao.add(f"{v_num//10}{i}")
                    extra_hatao.add(f"{i}{v_num%10}")

    # Final Filters
    final_16 = [j for j in target_36 if j not in extra_hatao]
    final_super = final_16[:9] if len(final_16) > 9 else final_16 # Top 9 for super accuracy
    
    return final_16, final_super, (pa, ra, pb, rb)

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    t16, t_super, sets = get_logic_v45(df, idx, target_s)

    st.divider()

    # --- DISPLAY TARGET JODIS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="target-box"><h4>✅ Table 1 (16-20 Jodis)</h4><div class="jodi-grid">', unsafe_allow_html=True)
        for j in t16: st.markdown(f'<div class="jodi-item">{j}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="target-box" style="border-color:#eab308;"><h4>💎 Super Hit (Max 9 Jodis)</h4><div class="jodi-grid">', unsafe_allow_html=True)
        for j in t_super: st.markdown(f'<div class="jodi-item" style="color:#854d0e; background:#fef9c3;">{j}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # --- HISTORY VERIFICATION ---
    st.subheader("📜 10-Day Real Backtest (Only show HIT if number was in list)")
    history_data = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        h16, h_super, _ = get_logic_v45(df, i, target_s)
        res_raw = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        
        status = "❌ FAIL"
        if res_raw.isdigit():
            rv = str(int(res_raw)).zfill(2)
            if rv in h_super: status = "💎 SUPER HIT"
            elif rv in h16: status = "✅ TABLE HIT"
            
        history_data.append({"Date": df.iloc[i]['DATE'], "Result": res_raw, "Status": status})
    
    st.table(pd.DataFrame(history_data))
    
