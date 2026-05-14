import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v44.0 - Triple Filter", layout="wide")

# Custom UI for Square Grids
st.markdown("""
    <style>
    .report-card { background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .grid-16 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 320px; margin: 0 auto; }
    .grid-5 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-width: 250px; margin: 0 auto; }
    .item-16 { background-color: #f0fdf4; color: #166534; padding: 12px; border-radius: 8px; font-size: 18px; font-weight: bold; text-align: center; border: 1px solid #bbf7d0; }
    .item-5 { background-color: #fffbeb; color: #92400e; padding: 15px; border-radius: 8px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #fde68a; }
    .label { font-weight: bold; color: #444; margin-bottom: 8px; text-align: center; }
    .ank-badge { display: inline-block; padding: 2px 8px; background: #fee2e2; color: #b91c1c; border-radius: 4px; margin: 2px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v44.0 (Triple-Filter Elimination)")

def get_worst_performing_gap(df, idx, col, count=2):
    """Scan different gaps and return digits from the one that fails most"""
    gaps = [3, 5, 8, 10, 12, 15]
    worst_gap = 3
    min_pass_count = 100
    
    for g in gaps:
        fails = 0
        for i in range(idx-10, idx):
            if i-g < 0: continue
            val = df.iloc[i-g].get(col, 0)
            res = df.iloc[i].get(col, "XX")
            # Logic to check if this gap predicted the result (we want the one that didn't)
            if str(val).split('.')[0] == str(res).split('.')[0]:
                fails -= 1 
        if fails < min_pass_count:
            min_pass_count = fails
            worst_gap = g
            
    # Return unique digits from the worst gap
    val = df.iloc[idx-worst_gap].get(col, 0)
    try:
        n = int(float(str(val).split('.')[0]))
        return [n // 10, n % 10]
    except: return [0, 5]

def calculate_triple_filter(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # 1. Level 1: Main 2-2 digits (Code 37)
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
    
    # 2. Level 2: Worst 2-2 digits
    w1_a, w1_b = get_worst_performing_gap(df, idx, base_col)
    
    # 3. Level 3: Extra 2-2 failing digits
    w2_a, w2_b = get_worst_performing_gap(df, idx-1, base_col) # Shifting index for diversity

    # Build Elimination Sets
    a_elim_16 = {pa, ra, w1_a}
    b_elim_16 = {pb, rb, w1_b}
    
    a_elim_5 = {pa, ra, w1_a, w2_a, (w1_a+1)%10}
    b_elim_5 = {pb, rb, w1_b, w2_b, (w1_b+1)%10}

    def get_targets(a_set, b_set):
        blocked = set()
        for a in a_set:
            for i in range(10): blocked.add(str(a) + str(i))
        for b in b_set:
            for i in range(10): blocked.add(str(i) + str(b))
        return [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked]

    return get_targets(a_elim_16, b_elim_16), get_targets(a_elim_5, b_elim_5), (a_elim_16, b_elim_16), (a_elim_5, b_elim_5)

uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    t16, t5, e16, e5 = calculate_triple_filter(df, idx, target_s)

    st.divider()

    # --- DISPLAY TABLES ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.markdown('<p class="label">📊 Table 1: High Stability (16 Jodis)</p>', unsafe_allow_html=True)
        st.write(f"Eliminated: A{list(e16[0])} B{list(e16[1])}")
        grid_html = '<div class="grid-16">'
        for j in t16[:16]: grid_html += f'<div class="item-16">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="report-card" style="border-left: 5px solid #f59e0b;">', unsafe_allow_html=True)
        st.markdown('<p class="label">🔥 Table 2: Super-High Accuracy (4-9 Jodis)</p>', unsafe_allow_html=True)
        st.write(f"Eliminated: A{list(e5[0])} B{list(e5[1])}")
        grid_html = '<div class="grid-5">'
        for j in t5[:9]: grid_html += f'<div class="item-5">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PERFORMANCE / TICK HISTORY ---
    st.divider()
    st.subheader("📜 10-Day Pass/Fail Tikka (Verification)")
    history_data = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        t16_h, t5_h, _, _ = calculate_triple_filter(df, i, target_s)
        res = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        status = "❌"
        if res.isdigit():
            rv = str(int(res)).zfill(2)
            if rv in t5_h: status = "💎 SUPER HIT"
            elif rv in t16_h: status = "✅ STABLE HIT"
            
        history_data.append({"Date": df.iloc[i]['DATE'], "Result": res, "Status": status})
    st.table(pd.DataFrame(history_data))
    
