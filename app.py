import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v47.0", layout="wide")

# Custom CSS for Square Grids and Live Result
st.markdown("""
    <style>
    .live-result-box { 
        background: #1e293b; color: #f8fafc; padding: 15px; 
        border-radius: 12px; text-align: center; margin-bottom: 20px;
        border: 2px solid #3b82f6;
    }
    .grid-container { 
        display: grid; grid-template-columns: repeat(4, 1fr); 
        gap: 8px; max-width: 400px; margin: 10px auto; 
    }
    .grid-item { 
        background-color: #ffffff; color: #166534; padding: 12px; 
        border-radius: 8px; font-size: 20px; font-weight: bold; 
        text-align: center; border: 2px solid #bbf7d0;
    }
    .section-title { font-weight: bold; color: #334155; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v47.0 (Square Box & Live Tracking)")

def get_logic_v47(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    val = 0
    for i in range(1, 15):
        t_idx = idx - i
        if t_idx >= 0:
            raw = df.iloc[t_idx].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    blocked = set()
    for a in {pa, ra}:
        for i in range(10): blocked.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked.add(f"{i}{b}")
    
    target_36 = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked]
    
    extra_hatao = set()
    for g in [3, 5]:
        if idx - g >= 0:
            v = str(df.iloc[idx-g].get(base_col, "XX")).split('.')[0]
            if v.isdigit():
                vn = int(v)
                for i in range(10): 
                    extra_hatao.add(f"{vn//10}{i}")
                    extra_hatao.add(f"{i}{vn%10}")

    final_list = [j for j in target_36 if j not in extra_hatao]
    return final_list[:16], final_list[:9]

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    
    # --- 1. LIVE RESULT (TOP) ---
    live_val = str(df.iloc[idx].get(target_s, "XX")).split('.')[0]
    st.markdown(f"""
        <div class="live-result-box">
            <span style="font-size:16px;">LIVE RESULT ({sel_date})</span><br>
            <span style="font-size:40px; font-weight:bold;">{live_val}</span>
        </div>
    """, unsafe_allow_html=True)

    # Calculate Logic
    t16, t9 = get_logic_v47(df, idx, target_s)

    # --- 2. TARGET JODIS (SQUARE BOXES) ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<p class="section-title">✅ Table 1 (Square 16)</p>', unsafe_allow_html=True)
        grid_html = '<div class="grid-container">'
        for j in t16: grid_html += f'<div class="grid-item">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    with col_b:
        st.markdown('<p class="section-title">💎 Super Hit (Square 9)</p>', unsafe_allow_html=True)
        grid_html = '<div class="grid-container" style="grid-template-columns: repeat(3, 1fr); max-width:300px;">'
        for j in t9: grid_html += f'<div class="grid-item" style="background:#fef9c3;">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- 3. BACKTEST HISTORY (BOTTOM) ---
    st.divider()
    st.subheader("📜 Backtest History (Tikka Tracking)")
    history_data = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        h16, h9 = get_logic_v47(df, i, target_s)
        res_raw = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res_raw.isdigit():
            rv = str(int(res_raw)).zfill(2)
            if rv in h9: status = "💎 SUPER"
            elif rv in h16: status = "✅ HIT"
        history_data.append({"Date": df.iloc[i]['DATE'], "Result": res_raw, "Status": status})
    
    st.table(pd.DataFrame(history_data))
                                                          
